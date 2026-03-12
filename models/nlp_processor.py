import re
from dateutil import parser as date_parser


def extract_entities(raw_text: str) -> dict:
    """
    Main function — backend calls this.
    Input:  raw text string from OCR
    Output: dict with all extracted information
    """
    return {
        "name":                 _extract_name(raw_text),
        "dob":                  _extract_dob(raw_text),
        "aadhaar":              _extract_aadhaar(raw_text),
        "pan":                  _extract_pan(raw_text),
        "phone":                _extract_phone(raw_text),
        "address":              _extract_address(raw_text),
        "account_no":           _extract_account_no(raw_text),
        "ifsc":                 _extract_ifsc(raw_text),
        "passport_number":      _extract_passport_no(raw_text),
        "passport_expiry":      _extract_passport_expiry(raw_text),
        "category":             _extract_category(raw_text),
        "caste":                _extract_caste(raw_text),
        "percentage":           _extract_percentage(raw_text),
        "board_name":           _extract_board_name(raw_text),
        "passing_year":         _extract_passing_year(raw_text),
        "annual_income":        _extract_income(raw_text),
        "birth_place":          _extract_birth_place(raw_text),
        "school_name":          _extract_school_name(raw_text),
        "bank_name":            _extract_bank_name(raw_text),
    }


# ── Original extractors ───────────────────────────────────────────

def _extract_aadhaar(text: str) -> str:
    """Aadhaar is 12 digits usually in groups of 4"""
    pattern = r'\b\d{4}\s\d{4}\s\d{4}\b|\b\d{12}\b'
    match = re.search(pattern, text)
    if match:
        return match.group().replace(" ", "")
    return ""


def _extract_pan(text: str) -> str:
    """PAN format: 5 letters, 4 digits, 1 letter"""
    pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]\b'
    match = re.search(pattern, text.upper())
    if match:
        return match.group()
    return ""


def _extract_phone(text: str) -> str:
    """Indian phone numbers: 10 digits starting with 6-9"""
    pattern = r'\b[6-9]\d{9}\b'
    match = re.search(pattern, text)
    if match:
        return match.group()
    return ""


def _extract_dob(text: str) -> str:
    """Dates in formats like 01/01/2000 or 01-01-2000"""
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
    """Looks for name after keywords like Name: or नाम"""
    pattern = r'(?:Name|NAME|नाम)\s*[:\-]?\s*([A-Za-z]+(?:\s[A-Za-z]+)+)'
    match = re.search(pattern, text)
    if match:
        name = match.group(1).strip()
        words = name.split()
        clean = [w for w in words if w.lower() not in
                ['date', 'dob', 'of', 'birth', 'father', 'mother', 'gender']]
        return " ".join(clean[:3]).title()
    return ""


def _extract_address(text: str) -> str:
    """Looks for address after Address: keyword"""
    pattern = r'(?:Address|ADDRESS|पता)\s*[:\-]?\s*(.+?)(?:\n|$)'
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    return ""


def _extract_account_no(text: str) -> str:
    """Bank account numbers: 9 to 18 digits"""
    pattern = r'\b\d{9,18}\b'
    match = re.search(pattern, text)
    if match:
        return match.group()
    return ""


def _extract_ifsc(text: str) -> str:
    """IFSC format: 4 letters, 0, 6 alphanumeric"""
    pattern = r'\b[A-Z]{4}0[A-Z0-9]{6}\b'
    match = re.search(pattern, text.upper())
    if match:
        return match.group()
    return ""


# ── New extractors ────────────────────────────────────────────────

def _extract_passport_no(text: str) -> str:
    """Passport number: 1 letter followed by 7 digits"""
    pattern = r'\b[A-Z][0-9]{7}\b'
    match = re.search(pattern, text.upper())
    if match:
        return match.group()
    return ""


def _extract_passport_expiry(text: str) -> str:
    """Looks for expiry date after Expiry or Valid Until keyword"""
    pattern = r'(?:Expiry|Expiry Date|Valid Until|Date of Expiry)\s*[:\-]?\s*(\d{2}[\/\-]\d{2}[\/\-]\d{4})'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1)
    return ""


def _extract_category(text: str) -> str:
    """Extracts caste category SC ST OBC NT General"""
    for cat in ['SC', 'ST', 'OBC', 'NT', 'GENERAL', 'GEN']:
        if re.search(r'\b' + cat + r'\b', text.upper()):
            return cat
    return ""


def _extract_caste(text: str) -> str:
    """Looks for caste after Caste: keyword"""
    pattern = r'(?:Caste|CASTE|जाति)\s*[:\-]?\s*([A-Za-z]+)'
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip().title()
    return ""


def _extract_percentage(text: str) -> str:
    """Extracts percentage from marksheets"""
    pattern = r'\b(\d{2}\.?\d{0,2})\s*%'
    match = re.search(pattern, text)
    if match:
        return match.group(1) + '%'
    # Also try CGPA format
    cgpa_pattern = r'(?:CGPA|GPA|cgpa)\s*[:\-]?\s*(\d+\.?\d{0,2})'
    cgpa_match = re.search(cgpa_pattern, text, re.IGNORECASE)
    if cgpa_match:
        return cgpa_match.group(1) + ' CGPA'
    return ""


def _extract_board_name(text: str) -> str:
    """Extracts board or university name from marksheets"""
    boards = [
        'CBSE', 'ICSE', 'SSC', 'HSC',
        'Maharashtra State Board',
        'Central Board', 'State Board',
        'Mumbai University', 'Pune University'
    ]
    for board in boards:
        if board.lower() in text.lower():
            return board
    return ""


def _extract_passing_year(text: str) -> str:
    """Extracts 4 digit year from marksheet"""
    pattern = r'\b(20[0-2][0-9])\b'
    matches = re.findall(pattern, text)
    if matches:
        return matches[-1]
    return ""


def _extract_income(text: str) -> str:
    """Extracts annual income amount"""
    pattern = r'(?:Rs\.?|INR|/-)\s*([\d,]+)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).replace(',', '')
    return ""


def _extract_birth_place(text: str) -> str:
    """Looks for place of birth keyword"""
    pattern = r'(?:Place of Birth|Birth Place|Born at|PLACE OF BIRTH)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|,|$)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip().title()
    return ""


def _extract_school_name(text: str) -> str:
    """Looks for school name keyword"""
    pattern = r'(?:School|SCHOOL|Institution|INSTITUTION)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|$)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip().title()
    return ""


def _extract_bank_name(text: str) -> str:
    """Extracts bank name from passbook"""
    banks = [
        'State Bank of India', 'SBI',
        'HDFC Bank', 'HDFC',
        'ICICI Bank', 'ICICI',
        'Bank of Maharashtra',
        'Punjab National Bank', 'PNB',
        'Canara Bank', 'Axis Bank',
        'Bank of Baroda', 'BOB',
        'Union Bank', 'Kotak'
    ]
    for bank in banks:
        if bank.lower() in text.lower():
            return bank
    return ""
