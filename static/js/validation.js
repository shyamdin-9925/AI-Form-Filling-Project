/**
 * FormAssist — validation.js
 * Client-side form validation for form_fill.html
 */

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('mainForm');
    if (!form) return;

    form.addEventListener('submit', function (e) {
      var valid = validateForm(form);
      if (!valid) {
        e.preventDefault();
        scrollToFirstError();
      }
    });

    // Live validation on blur
    form.querySelectorAll('input, textarea').forEach(function (el) {
      el.addEventListener('blur', function () {
        validateField(el);
      });
      el.addEventListener('input', function () {
        clearError(el);
      });
    });
  });

  // ── Main validation ────────────────────────────────────────
  function validateForm(form) {
    var valid = true;
    clearAllErrors(form);

    form.querySelectorAll('input[required], textarea[required]').forEach(function (el) {
      if (!el.value.trim()) {
        showError(el, el.name.replace(/_/g, ' ').replace(/\b\w/g, function(c){ return c.toUpperCase(); }) + ' is required.');
        valid = false;
      }
    });

    // Email validation
    form.querySelectorAll('input[type=email]').forEach(function (el) {
      if (el.value && !isValidEmail(el.value)) {
        showError(el, 'Enter a valid email address.');
        valid = false;
      }
    });

    // Phone validation
    form.querySelectorAll('input[type=tel]').forEach(function (el) {
      if (el.value && !isValidPhone(el.value)) {
        showError(el, 'Enter a valid 10-digit mobile number.');
        valid = false;
      }
    });

    // Aadhaar validation
    var aadhaar = form.querySelector('#aadhaar_no');
    if (aadhaar && aadhaar.value) {
      var clean = aadhaar.value.replace(/\s/g, '');
      if (!/^\d{12}$/.test(clean)) {
        showError(aadhaar, 'Aadhaar must be a 12-digit number.');
        valid = false;
      }
    }

    // PAN validation
    var pan = form.querySelector('#pan_no');
    if (pan && pan.value) {
      if (!/^[A-Z]{5}[0-9]{4}[A-Z]{1}$/i.test(pan.value.trim())) {
        showError(pan, 'Enter a valid PAN number (e.g. ABCDE1234F).');
        valid = false;
      }
    }

    return valid;
  }

  function validateField(el) {
    clearError(el);
    if (el.hasAttribute('required') && !el.value.trim()) {
      showError(el, getFieldLabel(el) + ' is required.');
      return false;
    }
    if (el.type === 'email' && el.value && !isValidEmail(el.value)) {
      showError(el, 'Enter a valid email address.');
      return false;
    }
    return true;
  }

  // ── Helpers ────────────────────────────────────────────────
  function showError(el, msg) {
    el.style.borderColor = '#dc2626';
    el.style.boxShadow   = '0 0 0 3px rgba(220,38,38,.12)';
    var errEl = document.getElementById('err-' + el.id) ||
                el.closest('.form-field-group').querySelector('.field-err-msg');
    if (errEl) errEl.textContent = msg;
  }

  function clearError(el) {
    el.style.borderColor = '';
    el.style.boxShadow   = '';
    var errEl = document.getElementById('err-' + el.id) ||
                (el.closest('.form-field-group') &&
                 el.closest('.form-field-group').querySelector('.field-err-msg'));
    if (errEl) errEl.textContent = '';
  }

  function clearAllErrors(form) {
    form.querySelectorAll('input, textarea').forEach(function (el) {
      clearError(el);
    });
    form.querySelectorAll('.field-err-msg').forEach(function (el) {
      el.textContent = '';
    });
  }

  function scrollToFirstError() {
    var first = document.querySelector('.field-err-msg:not(:empty)');
    if (first) {
      var group = first.closest('.form-field-group');
      if (group) group.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  function getFieldLabel(el) {
    var label = el.closest('.form-field-group') &&
                el.closest('.form-field-group').querySelector('label');
    return label ? label.textContent.replace('*','').trim() : el.name.replace(/_/g,' ');
  }

  function isValidEmail(val) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);
  }

  function isValidPhone(val) {
    var clean = val.replace(/[\s\-\+\(\)]/g,'');
    return /^[6-9]\d{9}$/.test(clean);
  }

})();
