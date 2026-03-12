/**
 * FormAssist — web_autofill.js
 * Sends URL + form data to /output/web-autofill backend endpoint.
 * Backend uses Selenium to open the page and fill the form fields.
 * Only available for Scholarship form.
 */

(function () {
  'use strict';

  window.startWebAutofill = function () {
    var urlInput  = document.getElementById('targetUrl');
    var statusEl  = document.getElementById('autofill-status');
    var btn       = document.querySelector('.roc-btn--amber');

    if (!urlInput || !statusEl) return;

    var url = urlInput.value.trim();

    if (!url) {
      setStatus(statusEl, '⚠ Please enter the scholarship website URL.', '#dc2626');
      urlInput.focus();
      return;
    }

    if (!isValidUrl(url)) {
      setStatus(statusEl, '⚠ Enter a valid URL starting with http:// or https://', '#dc2626');
      urlInput.style.borderColor = '#dc2626';
      return;
    }

    urlInput.style.borderColor = '';
    setStatus(statusEl, '⏳ Connecting to Selenium… opening Chrome browser window…', '#d97706');
    if (btn) { btn.disabled = true; btn.textContent = '⏳ Opening Browser…'; }

    fetch('/output/web-autofill', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({
        url:       url,
        form_data: typeof FORM_DATA !== 'undefined' ? FORM_DATA : {}
      })
    })
    .then(function (res) {
      if (!res.ok) throw new Error('Server returned ' + res.status);
      return res.json();
    })
    .then(function (data) {
      if (data.success) {
        var fieldList = (data.filled || []).join(', ');
        setStatus(statusEl,
          '✅ Chrome opened successfully! ' +
          data.filled.length + ' fields filled automatically: ' + fieldList + '. ' +
          'Please verify all fields and click Submit in the browser window.',
          '#059669');
        if (btn) { btn.disabled = false; btn.textContent = '🌐 Open Again'; }

        // Show browser instructions panel
        showBrowserInstructions(url, data.filled.length);
      } else {
        setStatus(statusEl, '⚠ Error: ' + (data.error || 'Unknown error occurred.'), '#dc2626');
        if (btn) { btn.disabled = false; btn.textContent = '🌐 Retry'; }
      }
    })
    .catch(function (err) {
      console.error('Web autofill error:', err);
      setStatus(statusEl,
        '⚠ Could not connect to browser automation service. ' +
        'Make sure the backend server is running and Selenium is installed.',
        '#dc2626');
      if (btn) { btn.disabled = false; btn.textContent = '🌐 Open & Auto-fill in Chrome →'; }
    });
  };

  // ── Helpers ────────────────────────────────────────────────
  function setStatus(el, msg, color) {
    if (!el) return;
    el.style.display    = 'block';
    el.style.padding    = '10px 14px';
    el.style.borderRadius = '9px';
    el.style.fontSize   = '13px';
    el.style.fontWeight = '500';
    el.style.lineHeight = '1.6';
    el.style.marginTop  = '8px';

    if (color === '#059669') {
      el.style.background = '#d1fae5';
      el.style.border     = '1px solid #6ee7b7';
      el.style.color      = '#065f46';
    } else if (color === '#dc2626') {
      el.style.background = '#fee2e2';
      el.style.border     = '1px solid #fca5a5';
      el.style.color      = '#991b1b';
    } else {
      el.style.background = '#fef3c7';
      el.style.border     = '1px solid #fde68a';
      el.style.color      = '#92400e';
    }

    el.textContent = msg;
  }

  function isValidUrl(url) {
    try {
      var u = new URL(url);
      return u.protocol === 'http:' || u.protocol === 'https:';
    } catch (e) {
      return false;
    }
  }

  function showBrowserInstructions(url, count) {
    var section = document.querySelector('.web-autofill-section');
    if (!section) return;

    var existing = section.querySelector('.browser-instructions');
    if (existing) existing.remove();

    var div = document.createElement('div');
    div.className = 'browser-instructions';
    div.style.cssText =
      'background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;' +
      'padding:14px 16px;margin-top:10px;font-size:13px;line-height:1.8;color:#166534;';
    div.innerHTML =
      '<strong style="display:block;margin-bottom:6px;font-size:14px">📋 What to do next:</strong>' +
      '<ol style="padding-left:16px;display:flex;flex-direction:column;gap:4px;">' +
      '<li>Chrome browser has opened <strong>' + url + '</strong></li>' +
      '<li><strong>' + count + ' fields</strong> have been filled automatically</li>' +
      '<li>Review all fields — correct any mistakes directly in the browser</li>' +
      '<li>Fill any remaining empty fields (email, mobile, etc.) manually</li>' +
      '<li>Click <strong>Submit</strong> on the scholarship website</li>' +
      '<li>Check the scholarship admin page to confirm your application</li>' +
      '</ol>';

    section.appendChild(div);
  }

})();
