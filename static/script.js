new Vue({
  el: '#app',
  data() {
    return {
      selectedFileNames: [],
      selectedFiles: [], // Store the actual file objects
      selectedLanguage: 'en', // Default language
      selectedFormat: 'txt'   // Default format
    };
  },
  methods: {
    openFileInput() {
      this.$refs.fileInput.click();
    },
    handleFileChange(event) {
      const fileList = event.target.files;
      this.selectedFileNames = [];
      this.selectedFiles = [];

      for (let i = 0; i < fileList.length; i++) {
        this.selectedFileNames.push({
          name: fileList[i].name,
          size: fileList[i].size
        });
        this.selectedFiles.push(fileList[i]); // Save the file object
      }
    },
    formatFileSize(size) {
      const units = ["B", "KB", "MB", "GB"];
      let index = 0;

      while (size >= 1024 && index < units.length - 1) {
        size /= 1024;
        index++;
      }

      return `${size.toFixed(2)} ${units[index]}`;
    },
    removeFile(index) {
      this.selectedFileNames.splice(index, 1);
      this.selectedFiles.splice(index, 1);
    },
    uploadFiles() {
      const formData = new FormData();
      for (let i = 0; i < this.selectedFiles.length; i++) {
        formData.append('document', this.selectedFiles[i]);
      }
      formData.append('language', this.selectedLanguage);
      formData.append('format', this.selectedFormat);

      fetch('/upload', {
        method: 'POST',
        body: formData,
      })
        .then(response => response.blob())
        .then(blob => {
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = 'translated_file.' + this.selectedFormat; // This will use the selected format
          document.body.appendChild(a);
          a.click();
          a.remove();
        })
        .catch(error => {
          console.error('Error:', error);
        });
    }
  }
});
