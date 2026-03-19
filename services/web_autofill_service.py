"""
web_autofill_service.py — FormAssist
Selenium autofill for the MU Scholarship Portal (multi-step form).
Fills Step 1 (Personal), Step 2 (Academic), Step 3 (Financial/Bank).
Step 4 (file uploads) and Step 5 (review) are left for the user.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time


# ── Field mapping per step ────────────────────────────────────────
# Maps FormAssist field names → scholarship portal field names
# Grouped by which step they appear on

STEP1_FIELDS = {
    'full_name':      'full_name',
    'dob':            'dob',
    'gender':         'gender',
    'mobile':         'mobile',
    'email':          'email',
    'aadhaar_number': 'aadhaar_number',
    'pan_number':     'pan_number',
    'address':        'address',
}

STEP2_FIELDS = {
    'school_name':          'college_name',
    'marksheet_10_percent': 'last_percentage',
}

STEP3_FIELDS = {
    'annual_income':  'annual_income',
    'bank_account':   'bank_account',
    'bank_name':      'bank_name',
    'ifsc_code':      'ifsc_code',
    'account_holder': 'account_holder',
}


def autofill_website(url: str, field_data: dict) -> dict:
    """
    Opens the scholarship portal and fills all 3 data steps.
    Input:  url (should be http://127.0.0.1:5001/apply)
            field_data dict with FormAssist field names as keys
    Output: dict {success, filled, failed}
    """
    filled = []
    failed = []

    if not field_data:
        return {
            'success': False,
            'error':   'No form data available. Please complete the FormAssist form first.',
            'filled':  [],
            'failed':  []
        }

    # ── Chrome setup ────────────────────────────────────────────
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    print(f"\nOpening Chrome → {url}")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    try:
        # ── STEP 1: Personal Details (/apply) ───────────────────
        print("\n── Step 1: Personal Details ──")
        driver.get(url)
        _wait_for_form(driver)

        step1_data = _build_step_data(field_data, STEP1_FIELDS)
        _fill_fields(driver, step1_data, filled, failed)
        _click_next(driver)

        # ── STEP 2: Academic Details (/apply/step2) ──────────────
        print("\n── Step 2: Academic Details ──")
        _wait_for_form(driver)

        step2_data = _build_step_data(field_data, STEP2_FIELDS)
        _fill_fields(driver, step2_data, filled, failed)
        _click_next(driver)

        # ── STEP 3: Financial / Bank Details (/apply/step3) ──────
        print("\n── Step 3: Financial Details ──")
        _wait_for_form(driver)

        step3_data = _build_step_data(field_data, STEP3_FIELDS)
        # bank_account_confirm = same as bank_account
        if field_data.get('bank_account'):
            step3_data['bank_account_confirm'] = field_data['bank_account']
        _fill_fields(driver, step3_data, filled, failed)

        # Do NOT click Next on step 3 — leave user at file upload step
        print("\n── Stopping at Step 4 (file uploads) — user fills manually ──")
        print(f"\nAutofill complete — Filled: {len(filled)}, Failed: {len(failed)}")
        print("Browser left open. Please upload documents and submit.")

        return {
            'success': True,
            'filled':  filled,
            'failed':  failed,
            'message': (
                f'Filled {len(filled)} fields across Steps 1-3. '
                f'Browser is at Step 4 — please upload your documents and submit.'
            )
        }

    except Exception as e:
        print(f"Autofill error: {e}")
        return {
            'success': False,
            'error':   str(e),
            'filled':  filled,
            'failed':  failed
        }


# ── Helpers ───────────────────────────────────────────────────────

def _build_step_data(form_data: dict, field_map: dict) -> dict:
    """Map FormAssist keys to portal field names, skip empty values."""
    result = {}
    for fa_key, portal_key in field_map.items():
        value = str(form_data.get(fa_key, '')).strip()
        if value:
            result[portal_key] = value
    return result


def _wait_for_form(driver, timeout=10):
    """Wait until a <form> is visible on the page."""
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.TAG_NAME, 'form'))
    )
    time.sleep(0.8)


def _click_next(driver):
    """Click the Next/Submit button on the current step."""
    try:
        btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"], .btn'))
        )
        btn.click()
        time.sleep(1.2)
    except Exception as e:
        print(f"  Could not click Next: {e}")


def _fill_fields(driver, step_data: dict, filled: list, failed: list):
    """Fill all fields for one step."""
    for field_name, value in step_data.items():
        if not value:
            continue
        element = _find_element(driver, field_name)
        if element is None:
            failed.append(field_name)
            print(f"  ✗ Not found: {field_name}")
            continue
        try:
            _fill_element(driver, element, field_name, value)
            filled.append(field_name)
            print(f"  ✓ Filled: {field_name} = {value}")
            time.sleep(0.15)
        except Exception as e:
            failed.append(field_name)
            print(f"  ✗ Error filling {field_name}: {e}")


def _find_element(driver, field_name: str):
    """Try to find a form element by name, id, or placeholder."""
    # By name (most reliable for this portal — all fields use name=)
    try:
        return driver.find_element(By.NAME, field_name)
    except Exception:
        pass
    # By ID
    try:
        return driver.find_element(By.ID, field_name)
    except Exception:
        pass
    # By placeholder
    try:
        hint = field_name.replace('_', ' ')
        return driver.find_element(
            By.XPATH,
            f"//input[contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            f"'abcdefghijklmnopqrstuvwxyz'),'{hint.lower()}')]"
        )
    except Exception:
        pass
    return None


def _fill_element(driver, element, field_name: str, value: str):
    """Fill a form element based on its type."""
    tag  = element.tag_name.lower()
    kind = (element.get_attribute('type') or '').lower()

    if tag == 'select':
        _fill_select(element, value)
    elif kind == 'date':
        _fill_date(element, value)
    elif kind in ('radio', 'checkbox'):
        _fill_radio_checkbox(driver, field_name, value)
    elif tag == 'textarea':
        element.clear()
        element.send_keys(value)
    else:
        element.clear()
        element.send_keys(value)


def _fill_select(element, value: str):
    """Fill <select> — try exact text, then partial match, then value attr."""
    sel = Select(element)
    # Exact match
    try:
        sel.select_by_visible_text(value)
        return
    except Exception:
        pass
    # Partial match
    for option in sel.options:
        if value.lower() in option.text.lower():
            sel.select_by_visible_text(option.text)
            return
    # Value attribute
    try:
        sel.select_by_value(value)
    except Exception:
        pass


def _fill_date(element, value: str):
    """
    Fill a date input.
    FormAssist stores dates as DD/MM/YYYY.
    HTML date inputs need YYYY-MM-DD.
    """
    if '/' in value:
        parts = value.split('/')
        if len(parts) == 3 and len(parts[2]) == 4:
            # DD/MM/YYYY → YYYY-MM-DD
            value = f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
    element.clear()
    element.send_keys(value)


def _fill_radio_checkbox(driver, field_name: str, value: str):
    """Select radio/checkbox by matching value attribute."""
    try:
        el = driver.find_element(
            By.XPATH,
            f"//input[@name='{field_name}' and "
            f"translate(@value,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')"
            f"='{value.lower()}']")
        if not el.is_selected():
            el.click()
    except Exception:
        pass