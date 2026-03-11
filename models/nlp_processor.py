import re
from dateutil import parser as date_parser


def extract_entities(raw_text: str) -> dict:
    """
    Main function — backend calls this.
    Input:  raw text string from OCR
    Output: dict with extracted information
    """
    return {
        "name":         _extract_name(raw_text),
        "dob":          _extract_dob(raw_text),
        "aadhaar":      _extract_aadhaar(raw_text),
        "pan":          _extract_pan(raw_text),
        "phone":        _extract_phone(raw_text),
        "address":      _extract_address(raw_text),
        "account_no":   _extract_account_no(raw_text),
        "ifsc":         _extract_ifsc(raw_text),
    }


def _extract_aadhaar(text: str) -> str:
    """
    Aadhaar is 12 digits, usually in groups of 4
    Examples: 1234 5678 9012 or 123456789012
    """
    pattern = r'\b\d{4}\s\d{4}\s\d{4}\b|\b\d{12}\b'
    match = re.search(pattern, text)
    if match:
        return match.group().replace(" ", "")
    return ""


def _extract_pan(text: str) -> str:
    """
    PAN format: 5 letters, 4 digits, 1 letter
    Example: ABCDE1234F
    """
    pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'
    match = re.search(pattern, text.upper())
    if match:
        return match.group()
    return ""


def _extract_phone(text: str) -> str:
    """
    Indian phone numbers: 10 digits starting with 6-9
    """
    pattern = r'\b[6-9]\d{9}\b'
    match = re.search(pattern, text)
    if match:
        return match.group()
    return ""


def _extract_dob(text: str) -> str:
    """
    Dates in formats like 01/01/2000, 01-01-2000, 01 Jan 2000
    """
    pattern = r'\b\d{2}[\/\-]\d{2}[\/\-]\d{4}\b|\b\d{2}\s\w+\s\d{4}\b'
    match = re.search(pattern, text)
    if match:
        try:
            parsed = date_parser.parse(match.group(), dayfirst=True)
            return parsed.strftime("%d/%m/%Y")
        except:
            return match.group()
    return ""


def _extract_name(text: str) -> str:
    """
    Looks for name after keywords like 'Name:' or 'नाम'
    Handles both normal case and ALL CAPS names
    """
    pattern = r'(?:Name|NAME|नाम)\s*[:\-]?\s*([A-Za-z]+(?:\s[A-Za-z]+)+)'
    match = re.search(pattern, text)
    if match:
        name = match.group(1).strip()
        words = name.split()
        # Remove keywords that are not part of the name
        clean = [w for w in words if w.lower() not in
                ['date', 'dob', 'of', 'birth', 'father', 'mother', 'gender']]
        return " ".join(clean[:3]).title()
    return ""


def _extract_address(text: str) -> str:
    """
    Looks for address after keywords like 'Address:' or 'पता'
    """
    pattern = r'(?:Address|ADDRESS|पता)\s*[:\-]?\s*(.+?)(?:\n|$)'
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    return ""


def _extract_account_no(text: str) -> str:
    """
    Bank account numbers: 9 to 18 digits
    """
    pattern = r'\b\d{9,18}\b'
    match = re.search(pattern, text)
    if match:
        return match.group()
    return ""


def _extract_ifsc(text: str) -> str:
    """
    IFSC format: 4 letters, 0, 6 alphanumeric
    Example: SBIN0001234
    """
    pattern = r'\b[A-Z]{4}0[A-Z0-9]{6}\b'
    match = re.search(pattern, text.upper())
    if match:
        return match.group()
    return ""
