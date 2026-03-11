document.addEventListener('DOMContentLoaded', () => {
  const forms = document.querySelectorAll('form');

  forms.forEach((form) => {
    form.addEventListener('submit', (event) => {
      const errors = [];

      const requiredFields = form.querySelectorAll('[required]');
      requiredFields.forEach((field) => {
        if (field.type === 'file') {
          if (!field.files || !field.files.length) {
            errors.push(`${getFieldLabel(form, field)} is required.`);
          }
          return;
        }

        if (!String(field.value || '').trim()) {
          errors.push(`${getFieldLabel(form, field)} is required.`);
        }
      });

      const emailFields = form.querySelectorAll('input[type="email"]');
      emailFields.forEach((field) => {
        const value = String(field.value || '').trim();
        if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
          errors.push(`${getFieldLabel(form, field)} must be a valid email address.`);
        }
      });

      const confirmPassword = form.querySelector('input[name="confirm_password"]');
      const password = form.querySelector('input[name="password"]');
      if (password && confirmPassword && password.value !== confirmPassword.value) {
        errors.push('Passwords do not match.');
      }

      if (errors.length) {
        event.preventDefault();
        renderErrors(form, errors);
      }
    });
  });

  function getFieldLabel(form, field) {
    const label = form.querySelector(`label[for="${field.id}"]`);
    return label ? label.textContent.trim() : (field.name || 'This field');
  }

  function renderErrors(form, errors) {
    let box = form.querySelector('.client-error-box');

    if (!box) {
      box = document.createElement('div');
      box.className = 'alert alert-error client-error-box';
      form.prepend(box);
    }

    box.innerHTML = `
      <strong>Please fix the following:</strong>
      <ul class="alert-list">
        ${errors.map((error) => `<li>${escapeHtml(error)}</li>`).join('')}
      </ul>
    `;

    box.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }
});
