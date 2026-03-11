def predict_fields(user_data: dict) -> dict:
    """
    Main function — backend calls this.
    Input:  user_data dict from database or nlp_processor
    Output: dict mapped to exact form field names
    """
    return {
        # ── Personal Details (Step 1) ──────────────────────
        "full_name":            _get(user_data, "name"),
        "dob":                  _format_date(_get(user_data, "dob")),
        "mobile":               _get(user_data, "phone"),
        "email":                _get(user_data, "email"),
        "aadhaar_number":       _get(user_data, "aadhaar"),
        "pan_number":           _get(user_data, "pan"),
        "address":              _get(user_data, "address"),

        # ── Academic Details (Step 2) ──────────────────────
        "college_name":         _get(user_data, "college_name"),
        "enrollment_no":        _get(user_data, "enrollment_no"),
        "course_name":          _get(user_data, "course_name"),

        # ── Bank Details (Step 3) ──────────────────────────
        "bank_account":         _get(user_data, "account_no"),
        "ifsc_code":            _get(user_data, "ifsc"),
        "bank_name":            _get(user_data, "bank_name"),
        "account_holder":       _get(user_data, "name"),
    }


def _get(data: dict, key: str) -> str:
    """
    Safely get a value from dict.
    Returns empty string if key not found.
    """
    return str(data.get(key, "")).strip()


def _format_date(dob: str) -> str:
    """
    Converts date to DD/MM/YYYY format for the form.
    Handles formats: YYYY-MM-DD, DD-MM-YYYY, DD/MM/YYYY
    """
    if not dob:
        return ""
    # Already in correct format
    if "/" in dob and len(dob) == 10:
        return dob
    # Convert YYYY-MM-DD to DD/MM/YYYY
    if "-" in dob:
        parts = dob.split("-")
        if len(parts) == 3:
            if len(parts[0]) == 4:
                # YYYY-MM-DD
                return f"{parts[2]}/{parts[1]}/{parts[0]}"
            else:
                # DD-MM-YYYY
                return f"{parts[0]}/{parts[1]}/{parts[2]}"
    return dob