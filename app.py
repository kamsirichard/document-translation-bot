import os
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from langdetect import detect
from googletrans import Translator
from docx import Document
import pdfkit
from PyPDF2 import PdfReader
import pytesseract

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

translator = Translator()

def save_file(file):
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    return file_path

def detect_language(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return detect(text)

def translate_text(text, target_language):
    translated = translator.translate(text, dest=target_language)
    return translated.text

def save_as_docx(text, filename):
    doc = Document()
    doc.add_paragraph(text)
    doc_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{filename}.docx")
    doc.save(doc_path)
    return doc_path

def save_as_txt(text, filename):
    txt_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{filename}.txt")
    with open(txt_path, 'w', encoding='utf-8') as file:
        file.write(text)
    return txt_path

def save_as_pdf(html, filename):
    pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], f"{filename}.pdf")
    pdfkit.from_string(html, pdf_path)
    return pdf_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist('document')
    target_language = request.form['language']
    output_format = request.form['format']
    
    processed_files = []

    if not os.path.exists(app.config['OUTPUT_FOLDER']):
        os.makedirs(app.config['OUTPUT_FOLDER'])

    for file in files:
        file_path = save_file(file)

        # Detect the language
        detected_language = detect_language(file_path)

        # Read file content
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        elif file_path.endswith('.docx'):
            doc = Document(file_path)
            content = "\n".join([para.text for para in doc.paragraphs])
        elif file_path.endswith('.pdf'):
            reader = PdfReader(file_path)
            content = ""
            for page in reader.pages:
                content += page.extract_text()
        else:
            content = pytesseract.image_to_string(file_path)

        # Translate the content
        translated_text = translate_text(content, target_language)

        # Save the translated content in the desired format
        filename = os.path.splitext(os.path.basename(file_path))[0]
        if output_format == 'doc':
            output_file_path = save_as_docx(translated_text, filename)
        elif output_format == 'txt':
            output_file_path = save_as_txt(translated_text, filename)
        elif output_format == 'pdf':
            output_file_path = save_as_pdf(translated_text, filename)
        
        processed_files.append(output_file_path)
    
    return send_file(processed_files[0], as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
