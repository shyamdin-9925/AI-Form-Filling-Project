/**
 * FormAssist — autofill.js
 * Fetches AI-extracted field values from backend and fills the form.
 * Called by: runAIAutofill() on form_fill.html
 */

(function () {
  'use strict';

  window.runAIAutofill = function () {
    var btn     = document.getElementById('aiBtn') || document.getElementById('autofillBtn');
    var sidebar = document.getElementById('aiStatus');
    var formType = (typeof FORM_TYPE !== 'undefined') ? FORM_TYPE : 'general_purpose';

    setButtonState(btn, 'loading');
    setStatus(sidebar, '⏳ Calling AI autofill…', '#a78bfa');

    fetch('/form/ai/autofill', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ form_type: formType })
    })
    .then(function (res) {
      if (!res.ok) throw new Error('Server error ' + res.status);
      return res.json();
    })
    .then(function (data) {
      var fields = data.fields || {};
      var filled = 0;
      var skipped = 0;

      Object.keys(fields).forEach(function (key) {
        var el = document.getElementById(key);
        if (!el) return;
        if (!fields[key]) { skipped++; return; }

        el.value = fields[key];
        filled++;

        // Flash highlight on filled field
        flashField(el);

        // Add AI badge if not already present
        var parent = el.closest('.form-field-group');
        if (parent) {
          parent.classList.add('autofilled');
          if (!parent.querySelector('.ai-badge')) {
            var badge = document.createElement('div');
            badge.className = 'ai-badge';
            badge.innerHTML =
              '<span class="ai-badge-dot"></span>' +
              'Filled by AI · <button type="button" class="ai-clear-btn" ' +
              'onclick="clearField(\'' + key + '\')">Clear</button>';
            el.parentNode.insertBefore(badge, el.nextSibling);
          }
        }
      });

      setButtonState(btn, 'done');
      setStatus(sidebar,
        '✓ ' + filled + ' fields filled from ' + (data.source || 'AI') + '.',
        '#6ee7b7');

      // Update sidebar stats
      updateSidebarStats(filled, skipped);
    })
    .catch(function (err) {
      console.error('Autofill error:', err);
      setButtonState(btn, 'error');
      setStatus(sidebar, '⚠ Autofill unavailable. Fill manually.', '#f87171');
    });
  };

  window.clearField = function (fieldId) {
    var el = document.getElementById(fieldId);
    if (!el) return;
    el.value = '';
    var parent = el.closest('.form-field-group');
    if (parent) {
      parent.classList.remove('autofilled');
      var badge = parent.querySelector('.ai-badge');
      if (badge) badge.remove();
    }
    el.focus();
  };

  // ── Helpers ────────────────────────────────────────────────
  function flashField(el) {
    el.style.transition = 'border-color .3s, background .3s, box-shadow .3s';
    el.style.borderColor = '#93c5fd';
    el.style.background  = '#eff6ff';
    el.style.boxShadow   = '0 0 0 3px rgba(37,99,235,.15)';
    setTimeout(function () {
      el.style.borderColor = '#93c5fd';
      el.style.background  = '#eff6ff';
      el.style.boxShadow   = '';
    }, 1800);
  }

  function setButtonState(btn, state) {
    if (!btn) return;
    if (state === 'loading') {
      btn.disabled = true;
      btn.textContent = '⏳ Running AI…';
    } else if (state === 'done') {
      btn.disabled = false;
      btn.textContent = '⚡ Re-run AI Autofill';
    } else if (state === 'error') {
      btn.disabled = false;
      btn.textContent = '⚡ Retry AI Autofill';
    }
  }

  function setStatus(el, msg, color) {
    if (!el) return;
    el.textContent = msg;
    el.style.color = color || '';
  }

  function updateSidebarStats(filled, skipped) {
    var nums = document.querySelectorAll('.ai-st-num');
    if (nums.length >= 1) nums[0].textContent = filled;
  }

})();
