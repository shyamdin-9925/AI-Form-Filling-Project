import re


def predict_fields(user_data: dict) -> dict:
    """
    Main function — backend calls this.
    Input:  user_data dict from database or nlp_processor
    Output: dict mapped to exact form field names
    """
    return {
        # ── Personal Details ───────────────────────────────
        "full_name":            _get(user_data, "name"),
        "dob":                  _format_date(_get(user_data, "dob")),
        "mobile":               _get(user_data, "phone"),
        "email":                _get(user_data, "email"),
        "aadhaar_number":       _get(user_data, "aadhaar"),
        "pan_number":           _get(user_data, "pan"),
        "address":              _get(user_data, "address"),
        "gender":               _get(user_data, "gender"),

        # ── Passport Details ───────────────────────────────
        "passport_number":      _get(user_data, "passport_number"),
        "passport_expiry":      _get(user_data, "passport_expiry"),
        "nationality":          "Indian",

        # ── Academic Details ───────────────────────────────
        "school_name":          _get(user_data, "school_name"),
        "marksheet_10_percent": _get(user_data, "percentage"),
        "marksheet_12_percent": _get(user_data, "percentage"),
        "board_name":           _get(user_data, "board_name"),
        "passing_year":         _get(user_data, "passing_year"),

        # ── Caste and Category ─────────────────────────────
        "category":             _get(user_data, "category"),
        "caste":                _get(user_data, "caste"),

        # ── Financial Details ──────────────────────────────
        "annual_income":        _get(user_data, "annual_income"),
        "bank_account":         _get(user_data, "account_no"),
        "ifsc_code":            _get(user_data, "ifsc"),
        "bank_name":            _get(user_data, "bank_name"),
        "account_holder":       _get(user_data, "name"),

        # ── Birth Details ──────────────────────────────────
        "birth_place":          _get(user_data, "birth_place"),
    }


def _get(data: dict, key: str) -> str:
    """Safely get value from dict. Returns empty string if not found."""
    val = data.get(key, "")
    return str(val).strip() if val else ""


def _format_date(dob: str) -> str:
    """
    Converts date to DD/MM/YYYY format for the form.
    Handles: YYYY-MM-DD, DD-MM-YYYY, DD/MM/YYYY, DD.MM.YYYY
    """
    if not dob:
        return ""
    if re.match(r'^\d{2}/\d{2}/\d{4}$', dob):
        return dob
    if re.match(r'^\d{2}[-\.]\d{2}[-\.]\d{4}$', dob):
        parts = re.split(r'[-\.]', dob)
        return f"{parts[0]}/{parts[1]}/{parts[2]}"
    if re.match(r'^\d{4}[-\.]\d{2}[-\.]\d{2}$', dob):
        parts = re.split(r'[-\.]', dob)
        return f"{parts[2]}/{parts[1]}/{parts[0]}"
    return dob