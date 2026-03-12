/**
 * FormAssist — upload.js
 * Handles multiple file inputs with preview, size validation,
 * drag-and-drop, and progress tracking.
 */

(function () {
  'use strict';

  var validFiles   = {};   // { doc_name: true/false }
  var selectedCount = 0;

  // ── Init on DOM ready ────────────────────────────────────
  document.addEventListener('DOMContentLoaded', function () {
    updateSubmitButton();
  });

  // ── Called from inline onchange ─────────────────────────
  window.handleFileChange = function (input, docName) {
    var file = input.files[0];
    handleFile(file, docName);
  };

  // ── Drag and Drop ────────────────────────────────────────
  window.handleDragOver = function (e, docName) {
    e.preventDefault();
    e.stopPropagation();
    var dz = document.getElementById('dropzone-' + docName);
    if (dz) dz.classList.add('dragover');
  };

  window.handleDragLeave = function (e, docName) {
    e.preventDefault();
    var dz = document.getElementById('dropzone-' + docName);
    if (dz) dz.classList.remove('dragover');
  };

  window.handleDrop = function (e, docName) {
    e.preventDefault();
    e.stopPropagation();
    var dz = document.getElementById('dropzone-' + docName);
    if (dz) dz.classList.remove('dragover');

    var files = e.dataTransfer.files;
    if (!files || !files[0]) return;

    var input = document.getElementById(docName);
    if (!input) return;

    // Transfer dropped file to input
    try {
      var dt = new DataTransfer();
      dt.items.add(files[0]);
      input.files = dt.files;
    } catch (ex) {
      // Fallback for browsers without DataTransfer constructor
    }

    handleFile(files[0], docName);
  };

  // ── Core file handler ────────────────────────────────────
  function handleFile(file, docName) {
    var previewEl  = document.getElementById('preview_' + docName);
    var errorEl    = document.getElementById('error-' + docName);
    var statusEl   = document.getElementById('status-' + docName);
    var cardEl     = document.getElementById('doc-card-' + docName);
    var reqItem    = document.getElementById('req-' + docName);
    var checkItem  = document.getElementById('check-' + docName);
    var dropInner  = document.getElementById('drop-inner-' + docName);

    // Clear previous state
    if (errorEl) errorEl.textContent = '';
    if (previewEl) previewEl.innerHTML = '';

    if (!file) return;

    var maxKb = getMaxKb(docName);

    // ── Size check ────────────────────────────────────────
    if (file.size > maxKb * 1024) {
      markInvalid(docName);
      if (errorEl) errorEl.innerHTML =
        '<span style="color:#dc2626">⚠ File too large! Max: ' + maxKb + ' KB. ' +
        'Actual: ' + Math.round(file.size / 1024) + ' KB.<br>' +
        'FormAssist will auto-compress on upload, but please try a smaller file for best results.</span>';
      if (statusEl) statusEl.innerHTML = '<span class="udc-err">⚠ Too large</span>';
      if (cardEl) cardEl.style.borderColor = '#fca5a5';
      updateSubmitButton();
      return;
    }

    // ── Image preview ─────────────────────────────────────
    if (file.type.startsWith('image/')) {
      var reader = new FileReader();
      reader.onload = function (e) {
        if (previewEl) {
          previewEl.innerHTML =
            '<div class="preview-ok">' +
            '<img src="' + e.target.result + '" alt="' + file.name + '" ' +
            'style="width:72px;height:72px;object-fit:cover;border-radius:8px;' +
            'border:2px solid #059669;display:block">' +
            '<div>' +
            '<div style="font-size:13px;font-weight:600;color:#059669">✓ ' + file.name + '</div>' +
            '<div style="font-size:12px;color:#6b7280">' + formatSize(file.size) + '</div>' +
            '</div></div>';
        }
      };
      reader.readAsDataURL(file);
    } else if (file.type === 'application/pdf') {
      // PDF — show icon
      if (previewEl) {
        previewEl.innerHTML =
          '<div class="preview-pdf" style="display:flex;align-items:center;gap:10px;padding:10px 0">' +
          '<span style="font-size:32px">📄</span>' +
          '<div>' +
          '<div style="font-size:13px;font-weight:600;color:#2563eb">✓ ' + file.name + '</div>' +
          '<div style="font-size:12px;color:#6b7280">' + formatSize(file.size) + ' · PDF</div>' +
          '</div></div>';
      }
    } else {
      if (previewEl) {
        previewEl.innerHTML =
          '<div class="preview-ok" style="padding:8px 0;font-size:13px;font-weight:600;color:#059669">' +
          '✓ ' + file.name + ' (' + formatSize(file.size) + ')' +
          '</div>';
      }
    }

    // ── Mark valid ────────────────────────────────────────
    markValid(docName);
    if (statusEl) statusEl.innerHTML = '<span class="udc-ok">✓ Ready</span>';
    if (cardEl) cardEl.style.borderColor = '#6ee7b7';
    if (dropInner) {
      dropInner.querySelector('.udc-drop-text').textContent = 'File selected — click to change';
      dropInner.querySelector('.udc-drop-icon').textContent = '✅';
    }
    if (reqItem) reqItem.classList.add('done');
    if (checkItem) checkItem.textContent = '✓';

    updateSubmitButton();
  }

  // ── Helpers ───────────────────────────────────────────────
  function getMaxKb(docName) {
    var input = document.getElementById(docName);
    if (input && input.dataset && input.dataset.maxKb) {
      return parseInt(input.dataset.maxKb);
    }
    return 500;
  }

  function markValid(docName) {
    if (!validFiles[docName]) {
      validFiles[docName] = true;
      selectedCount++;
    }
  }

  function markInvalid(docName) {
    if (validFiles[docName]) {
      validFiles[docName] = false;
      selectedCount = Math.max(0, selectedCount - 1);
    } else {
      validFiles[docName] = false;
    }
  }

  function updateSubmitButton() {
    var btn = document.getElementById('uploadSubmitBtn');
    var countEl = document.querySelector('#fileCount');
    var totalDocs = typeof TOTAL_DOCS !== 'undefined' ? TOTAL_DOCS : 1;

    var validCount = Object.values(validFiles).filter(function(v){ return v; }).length;

    if (countEl) {
      countEl.textContent = validCount + ' / ' + totalDocs;
    }
    if (btn) {
      btn.disabled = (validCount === 0);
      if (validCount === totalDocs) {
        btn.textContent = 'Upload All ' + totalDocs + ' Documents & Extract →';
        btn.style.background = '#059669';
      } else if (validCount > 0) {
        btn.textContent = 'Upload ' + validCount + ' / ' + totalDocs + ' & Extract →';
        btn.style.background = '';
      } else {
        btn.textContent = 'Upload All & Extract with AI →';
        btn.style.background = '';
      }
    }
  }

  function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return Math.round(bytes / 1024) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  // ── Upload form progress simulation ──────────────────────
  var uploadForm = document.getElementById('uploadForm');
  if (uploadForm) {
    uploadForm.addEventListener('submit', function (e) {
      var validCount = Object.values(validFiles).filter(function(v){ return v; }).length;
      if (validCount === 0) {
        e.preventDefault();
        alert('Please select at least one document to upload.');
        return;
      }
      // Show progress bar
      var progress = document.getElementById('uploadProgress');
      var fill = document.getElementById('progressFill');
      var label = document.getElementById('progressLabel');
      if (progress) {
        progress.style.display = 'block';
        var pct = 0;
        var interval = setInterval(function () {
          pct = Math.min(pct + Math.random() * 18, 95);
          if (fill) fill.style.width = pct + '%';
          if (label) label.textContent = 'Uploading & running OCR... ' + Math.round(pct) + '%';
        }, 300);
        // Stop interval on page leave
        window.addEventListener('beforeunload', function () {
          clearInterval(interval);
          if (fill) fill.style.width = '100%';
          if (label) label.textContent = 'Processing complete!';
        });
      }
    });
  }

})();
