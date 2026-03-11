document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('uploadForm');
  const input = document.getElementById('document');
  const preview = document.getElementById('filePreview');
  const message = document.getElementById('fileMessage');
  const maxSize = 10 * 1024 * 1024;

  if (!form || !input || !preview || !message) {
    return;
  }

  const setDefaultPreview = () => {
    preview.innerHTML = '<span>No file selected yet.</span>';
  };

  const formatBytes = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  setDefaultPreview();

  input.addEventListener('change', () => {
    const file = input.files && input.files[0];
    preview.innerHTML = '';

    if (!file) {
      message.textContent = 'Accepted file types: PDF, JPG, JPEG.';
      message.classList.remove('text-danger');
      setDefaultPreview();
      form.dataset.invalid = 'false';
      return;
    }

    if (file.size > maxSize) {
      message.textContent = 'File is too large. Please upload a file smaller than 10 MB.';
      message.classList.add('text-danger');
      form.dataset.invalid = 'true';
    } else {
      message.textContent = `Selected: ${file.name} (${formatBytes(file.size)})`;
      message.classList.remove('text-danger');
      form.dataset.invalid = 'false';
    }

    if (file.type.startsWith('image/')) {
      const img = document.createElement('img');
      const objectUrl = URL.createObjectURL(file);

      img.src = objectUrl;
      img.alt = 'Selected file preview';
      img.onload = () => URL.revokeObjectURL(objectUrl);

      preview.appendChild(img);
      return;
    }

    const pdfPreview = document.createElement('div');
    pdfPreview.className = 'pdf-preview';
    pdfPreview.innerHTML = `
      <div class="pdf-icon">📄</div>
      <div>
        <div>${file.name}</div>
        <small>PDF ready to upload</small>
      </div>
    `;
    preview.appendChild(pdfPreview);
  });

  form.addEventListener('submit', (event) => {
    const file = input.files && input.files[0];

    if (!file) {
      event.preventDefault();
      message.textContent = 'Please choose a file before uploading.';
      message.classList.add('text-danger');
      input.focus();
      return;
    }

    if (file.size > maxSize) {
      event.preventDefault();
      message.textContent = 'Please choose a file smaller than 10 MB.';
      message.classList.add('text-danger');
      input.focus();
    }
  });
});
