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
    """
    Safely get value from dict.
    Returns empty string if key not found.
    """
    return str(data.get(key, "")).strip()


def _format_date(dob: str) -> str:
    """
    Converts date to DD/MM/YYYY format for the form.
    Handles: YYYY-MM-DD, DD-MM-YYYY, DD/MM/YYYY
    """
    if not dob:
        return ""
    if "/" in dob and len(dob) == 10:
        return dob
    if "-" in dob:
        parts = dob.split("-")
        if len(parts) == 3:
            if len(parts[0]) == 4:
                return f"{parts[2]}/{parts[1]}/{parts[0]}"
            else:
                return f"{parts[0]}/{parts[1]}/{parts[2]}"
    return dob