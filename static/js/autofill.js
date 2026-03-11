document.addEventListener('DOMContentLoaded', () => {
  const autofillButton = document.getElementById('autofillTrigger');
  const statusEl = document.getElementById('autofillStatus');
  const userIdInput = document.getElementById('userId');

  if (!autofillButton) {
    return;
  }

  autofillButton.addEventListener('click', () => {
    const userId = userIdInput ? userIdInput.value : '';

    autofillButton.disabled = true;
    if (statusEl) {
      statusEl.textContent = 'Requesting AI suggestions...';
    }

    fetch('/form/ai/autofill', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId }),
      headers: {
        'Content-Type': 'application/json'
      }
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error('Autofill request failed.');
        }
        return res.json();
      })
      .then((data) => {
        const fields = data.field || data.fields || data;

        if (!fields || typeof fields !== 'object') {
          throw new Error('Invalid autofill payload.');
        }

        Object.keys(fields).forEach((key) => {
          const el = document.getElementById(key);
          if (el) {
            el.value = fields[key] ?? '';
          }
        });

        if (statusEl) {
          statusEl.textContent = 'Autofill suggestions applied.';
        }
      })
      .catch(() => {
        if (statusEl) {
          statusEl.textContent = 'Autofill is unavailable right now. Please fill the fields manually.';
        }
      })
      .finally(() => {
        autofillButton.disabled = false;
      });
  });
});
