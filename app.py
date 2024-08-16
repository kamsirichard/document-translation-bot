from flask import Flask, request, render_template, send_file, jsonify
import os
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'document' not in request.files:
        return "No file part", 400

    file = request.files['document']
    if file.filename == '':
        return "No selected file", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    target_language = request.form['language']

    try:
        translated_file = translate_document(filepath, target_language)
        return send_file(translated_file, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def translate_document(filepath, target_language):
    with open(filepath, 'r', encoding='utf-8') as file:
        text = file.read()

    # Call translation API
    translated_text = translate_text(text, target_language)

    # Save translated text to a new file
    translated_filepath = f"{filepath}_translated.txt"
    with open(translated_filepath, 'w', encoding='utf-8') as file:
        file.write(translated_text)

    return translated_filepath

def translate_text(text, target_language):
    api_key = os.getenv('TRANSLATION_API_KEY')
    url = "https://translation-api.example.com/translate"  # Replace with actual API URL
    data = {
        'q': text,
        'target': target_language,
        'key': api_key
    }
    response = requests.post(url, data=data)

    if response.status_code != 200:
        raise Exception(f"Translation API request failed with status code {response.status_code}")

    result = response.json()
    return result.get('translatedText', '')

if __name__ == '__main__':
    app.run(debug=True)
