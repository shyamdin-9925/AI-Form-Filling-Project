"""
nlp_processor.py — FormAssist
Doc-specific entity extraction from OCR text.
Each extractor tries multiple strategies in confidence order.
Invalid/noisy results are rejected rather than returned wrong.
"""

import re
from dateutil import parser as date_parser


# ── Document type → fields to extract ────────────────────────────
DOC_FIELD_MAP = {
    'aadhaar_doc':    ['name', 'dob', 'aadhaar', 'address', 'gender'],
    'pan_doc':        ['name', 'pan', 'dob'],
    'marksheet_10':   ['name', 'percentage', 'board_name', 'passing_year',
                       'marks_obtained', 'total_marks', 'subjects', 'roll_no'],
    'marksheet_12':   ['name', 'percentage', 'board_name', 'passing_year',
                       'marks_obtained', 'total_marks', 'subjects', 'roll_no'],
    'bank_passbook':  ['name', 'account_no', 'ifsc', 'bank_name', 'branch'],
    'passport_doc':   ['name', 'dob', 'passport_number', 'passport_expiry',
                       'nationality', 'birth_place'],
    'birth_cert':     ['name', 'dob', 'birth_place', 'father_name', 'mother_name'],
    'caste_cert':     ['name', 'caste', 'category'],
    'income_cert':    ['name', 'annual_income'],
    'school_leaving': ['name', 'school_name', 'passing_year'],
    'form16':         ['name', 'pan', 'annual_income', 'employer_name'],
    'photo':          [],
}

DEFAULT_FIELDS = ['name', 'dob', 'aadhaar', 'pan', 'phone', 'address',
                  'account_no', 'ifsc', 'bank_name']


# ── Words that should never appear in a person's name ────────────
BAD_NAME_WORDS = {
    # Document/form words
    'date', 'dob', 'birth', 'father', 'mother', 'gender', 'card',
    'aadhaar', 'aadhar', 'india', 'government', 'govt', 'authority',
    'unique', 'identification', 'address', 'phone', 'mobile', 'email',
    'name', 'signature', 'photo', 'photograph',
    # Geography words
    'delhi', 'mumbai', 'pune', 'bangalore', 'bengaluru', 'hyderabad',
    'chennai', 'kolkata', 'new', 'bagh', 'nagar', 'road', 'street',
    'block', 'sector', 'district', 'state', 'village', 'post', 'pin',
    'area', 'city', 'town', 'taluka', 'tehsil',
    # Academic words
    'pass', 'fail', 'result', 'board', 'exam', 'certificate', 'division',
    'arts', 'science', 'commerce', 'stream', 'seat', 'centre', 'dist',
    'school', 'month', 'year', 'srno', 'statement', 'secondary', 'higher',
    'education', 'maharashtra', 'candidate', 'surname', 'first', 'full',
    'leaving', 'admission',
    # Legal/cert words
    'certified', 'certify', 'that', 'son', 'daughter', 'has', 'been',
    'student', 'class', 'the', 'and', 'for', 'reg', 'ref', 'std', 'div',
    'belongs', 'caste', 'category', 'income', 'annual',
    # Bank words
    'bank', 'branch', 'account', 'manager', 'officer', 'savings',
    'current', 'deposit', 'customer', 'holder',
    # Short noise tokens
    'no', 'mrs', 'mr', 'ms', 'dr', 'shri', 'smt', 'kumari',
}


# ─────────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────────
def extract_entities(raw_text: str, doc_type: str = None) -> dict:
    """
    Extract entities from OCR text, restricted to fields
    relevant for the given document type.
    """
    # Pre-process text once — clean up common OCR noise
    text = _preprocess(raw_text)

    fields_to_extract = DOC_FIELD_MAP.get(doc_type, DEFAULT_FIELDS)

    extractors = {
        'name':            lambda t: _extract_name(t, doc_type),
        'dob':             _extract_dob,
        'aadhaar':         _extract_aadhaar,
        'pan':             _extract_pan,
        'phone':           _extract_phone,
        'address':         _extract_address,
        'gender':          _extract_gender,
        'account_no':      _extract_account_no,
        'ifsc':            _extract_ifsc,
        'bank_name':       _extract_bank_name,
        'branch':          lambda t: _extract_branch(t, doc_type),
        'passport_number': _extract_passport_no,
        'passport_expiry': _extract_passport_expiry,
        'nationality':     _extract_nationality,
        'birth_place':     _extract_birth_place,
        'category':        _extract_category,
        'caste':           _extract_caste,
        'percentage':      _extract_percentage,
        'board_name':      _extract_board_name,
        'passing_year':    lambda t: _extract_passing_year(t, doc_type),
        'school_name':     lambda t: _extract_school_name(t, doc_type),
        'marks_obtained':  _extract_marks_obtained,
        'total_marks':     _extract_total_marks,
        'subjects':        _extract_subjects,
        'roll_no':         _extract_roll_no,
        'annual_income':   _extract_income,
        'father_name':     _extract_father_name,
        'mother_name':     _extract_mother_name,
        'employer_name':   _extract_employer_name,
    }

    result = {}
    for field in fields_to_extract:
        if field in extractors:
            try:
                result[field] = extractors[field](text) or ""
            except Exception:
                result[field] = ""
    return result


# ─────────────────────────────────────────────────────────────────
# PRE-PROCESSING
# ─────────────────────────────────────────────────────────────────
def _preprocess(text: str) -> str:
    """Clean common OCR noise from text before extraction."""
    if not text:
        return ""
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Remove zero-width and non-printable chars
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    # Normalize multiple spaces within lines (but keep newlines)
    text = re.sub(r'[^\S\n]+', ' ', text)
    # Remove lines that are pure noise (only symbols, no letters or digits)
    lines = []
    for line in text.split('\n'):
        if re.search(r'[A-Za-z0-9\u0900-\u097F]', line):
            lines.append(line)
    return '\n'.join(lines)


# ─────────────────────────────────────────────────────────────────
# NAME HELPERS
# ─────────────────────────────────────────────────────────────────
def _clean_name(raw: str) -> str:
    """
    Post-process a raw extracted name string:
    - Stop at relational words (son, daughter, of, s/o, d/o, w/o)
    - Remove title prefixes (Mr, Mrs, Dr, Shri, Smt)
    - Remove 1-2 char OCR noise from edges
    - Remove bad words
    - Reject if result is too short or looks like garbage
    """
    if not raw:
        return ""
    # Stop at relational words
    raw = re.split(r'\b(?:son|daughter|s/o|d/o|w/o|c/o|of|and|whose)\b',
                   raw, flags=re.IGNORECASE)[0]
    # Remove title prefixes
    raw = re.sub(r'^(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Shri\.?|Smt\.?|Kumari\.?)\s*',
                 '', raw.strip(), flags=re.IGNORECASE)
    # Extract only clean alpha words
    words = re.findall(r'\b[A-Za-z]{2,}\b', raw)
    # Remove bad words
    words = [w for w in words if w.lower() not in BAD_NAME_WORDS]
    # Remove leading/trailing 1-2 char tokens (OCR noise like Fw, Nee, Io)
    while words and len(words[0]) <= 2:
        words.pop(0)
    while words and len(words[-1]) <= 2:
        words.pop()
    # Remove pure uppercase abbreviations > 2 chars unless they look like names
    # (names can be all-caps on official docs, but random abbreviations shouldn't appear)
    cleaned = []
    for w in words:
        # Keep if mixed case, or if ALL_CAPS and len 3-15 (could be a name)
        if not w.isupper() or 3 <= len(w) <= 15:
            cleaned.append(w)
    words = cleaned
    if not words or len(words) == 0:
        return ""
    result = ' '.join(words[:5]).title()
    # Reject if result is suspiciously short (single char names are OCR noise)
    if len(result.replace(' ', '')) < 3:
        return ""
    return result


def _is_valid_name(name: str) -> bool:
    """Return True if name looks like a real person's name."""
    if not name or len(name) < 3:
        return False
    words = name.split()
    if len(words) > 6:  # too many words
        return False
    # Each word should be mostly letters
    for w in words:
        if not re.match(r'^[A-Za-z]{2,}$', w):
            return False
    # Should not contain bad words
    if any(w.lower() in BAD_NAME_WORDS for w in words):
        return False
    return True


# ─────────────────────────────────────────────────────────────────
# NAME EXTRACTOR
# ─────────────────────────────────────────────────────────────────
def _extract_name(text, doc_type=None):

    # ── MARKSHEET: CANDIDATE'S FULL NAME header → next line ──────
    if doc_type in ('marksheet_10', 'marksheet_12'):
        match = re.search(
            r"CANDIDATE['\u2019]*S?\s+FULL\s+NAME[^\n]*\n\s*([^\n]{3,80})",
            text, re.IGNORECASE)
        if match:
            name = _clean_name(match.group(1))
            if _is_valid_name(name):
                return name

    # ── CASTE CERT: "certify that [Title] Firstname Lastname" ────
    if doc_type == 'caste_cert':
        match = re.search(
            r'certif(?:y|ied)\s+that\s+'
            r'(?:Mrs?\.?|Shri\.?|Smt\.?|Dr\.?|Kumari\.?)?\s*'
            r'([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,5})',
            text, re.IGNORECASE)
        if match:
            name = _clean_name(match.group(1))
            if _is_valid_name(name):
                return name

    # ── SCHOOL LEAVING: "Certified that X son/daughter of" ───────
    if doc_type == 'school_leaving':
        match = re.search(
            r'certif(?:y|ied)\s+that\s+'
            r'([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,4})'
            r'\s+(?:son|daughter|s/o|d/o)',
            text, re.IGNORECASE)
        if match:
            name = _clean_name(match.group(1))
            if _is_valid_name(name):
                return name

    # ── PAN CARD: name is on its own line between header and DOB ─
    if doc_type == 'pan_doc':
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for line in lines:
            # Skip known non-name lines
            if re.search(r'income|tax|dept|department|govt|government|'
                         r'bharat|india|आयकर|विभाग|permanent|account|'
                         r'signature|\d{2}[\/\-]\d{2}[\/\-]\d{4}',
                         line, re.IGNORECASE):
                continue
            if re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', line.upper()):
                continue
            words = re.findall(r'\b[A-Za-z]{2,}\b', line)
            words = [w for w in words if w.lower() not in BAD_NAME_WORDS]
            if 1 <= len(words) <= 5:
                name = _clean_name(' '.join(words))
                if _is_valid_name(name):
                    return name

    # ── BANK PASSBOOK: "Customer Name: Mrs. SITARA" ──────────────
    if doc_type == 'bank_passbook':
        match = re.search(
            r'(?:Customer\s*Name|Account\s*(?:Holder|Name)|A/C\s*Name)'
            r'\s*[:\-]\s*'
            r'(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Shri\.?|Smt\.?)?\s*'
            r'([A-Za-z][A-Za-z\s]{2,50}?)(?:\n|$)',
            text, re.IGNORECASE)
        if match:
            name = _clean_name(match.group(1))
            if _is_valid_name(name):
                return name

    # ── AADHAAR / GENERAL: "Name: Firstname" label ───────────────
    match = re.search(
        r'(?:^|\n)\s*(?:Name|NAME|नाम)\s*[:\-]?\s*'
        r'([A-Za-z][a-z]+(?:\s[A-Za-z][a-z]+){0,3})',
        text, re.MULTILINE)
    if match:
        name = _clean_name(match.group(1))
        if _is_valid_name(name):
            return name

    # Name on next line after label (Aadhaar OCR noise pattern)
    match = re.search(
        r'(?:Name|NAME|नाम)\s*[:\-]?\s*\n[^\w\n]*'
        r'([A-Za-z][a-z]+(?:\s[A-Za-z][a-z]+){0,3})',
        text)
    if match:
        name = _clean_name(match.group(1))
        if _is_valid_name(name):
            return name

    # ── Smart fallback: line with 2-4 proper capitalized words ───
    # Only use if we can't find name any other way
    for line in text.split('\n'):
        words = re.findall(r'\b[A-Za-z]{3,15}\b', line)
        if 2 <= len(words) <= 4:
            clean = [w for w in words if w.lower() not in BAD_NAME_WORDS]
            if len(clean) == len(words):
                # All words capitalized, none ALL_CAPS keyword
                if all(w[0].isupper() for w in clean):
                    if not any(w.isupper() and len(w) > 4 for w in clean):
                        name = ' '.join(clean[:4]).title()
                        if _is_valid_name(name):
                            return name
    return ""


# ─────────────────────────────────────────────────────────────────
# ADDRESS EXTRACTOR
# ─────────────────────────────────────────────────────────────────
def _extract_address(text):
    def clean_line(line):
        # Strip non-ASCII noise
        c = re.sub(r'[^A-Za-z0-9,\s\-\/]', '', line).strip()
        # Remove isolated 1-2 char tokens
        c = re.sub(r'(?<!\w)[A-Za-z]{1,2}(?!\w)', '', c)
        c = re.sub(r'\s+', ' ', c).strip()
        return c

    def is_valid_addr_line(line):
        words = re.findall(r'\b[A-Za-z]{3,}\b', line)
        digits = re.findall(r'\b\d{3,}\b', line)
        return (len(words) >= 1 or len(digits) >= 1) and len(line) > 4

    # Strategy 1: After Address/पता label
    match = re.search(
        r'(?:Address|ADDRESS|पता)\s*[:\-]?\s*([\s\S]+?)(?:\n\s*\n|\Z)',
        text, re.IGNORECASE)
    if match:
        lines = [l.strip() for l in match.group(1).split('\n') if l.strip()]
        result = []
        for line in lines[:6]:
            c = clean_line(line)
            if is_valid_addr_line(c):
                result.append(c)
            if re.search(r'\b\d{6}\b', line):
                break
        if result:
            return ', '.join(result)

    # Strategy 2: W/O or S/O address pattern (bank passbook)
    match = re.search(
        r'(?:Address|W/O|S/O|D/O|C/O)\s*[:\-]?\s*'
        r'([A-Za-z0-9\s,\-\/]+?\d{6})',
        text, re.IGNORECASE | re.DOTALL)
    if match:
        addr = clean_line(match.group(1))
        if addr:
            return addr

    # Strategy 3: text near a 6-digit pincode
    pin_match = re.search(r'(.{20,200}?\b\d{6}\b)', text, re.DOTALL)
    if pin_match:
        addr = re.sub(r'[^A-Za-z0-9,\s\-\/]', ' ', pin_match.group(1))
        addr = re.sub(r'(?<!\w)[A-Za-z]{1,2}(?!\w)', '', addr)
        addr = re.sub(r'\s+', ' ', addr).strip()
        if len(addr) > 10:
            return addr
    return ""


# ─────────────────────────────────────────────────────────────────
# AADHAAR
# ─────────────────────────────────────────────────────────────────
def _extract_aadhaar(text):
    # Spaced format: 1234 5678 9012
    match = re.search(r'\b(\d{4})\s(\d{4})\s(\d{4})\b', text)
    if match:
        return match.group(1) + match.group(2) + match.group(3)
    # Continuous 12 digits (not part of longer number)
    match = re.search(r'(?<!\d)(\d{12})(?!\d)', text)
    return match.group(1) if match else ""


# ─────────────────────────────────────────────────────────────────
# PAN
# ─────────────────────────────────────────────────────────────────
def _extract_pan(text):
    # Standard PAN format: 5 letters, 4 digits, 1 letter
    match = re.search(r'\b([A-Z]{5}[0-9]{4}[A-Z])\b', text.upper())
    if match:
        return match.group(1)
    # PAN card label then number (possibly on next line)
    match = re.search(
        r'(?:Permanent\s+Account\s+Number|PAN\s*(?:Number|No\.?|Card)?)'
        r'\s*[:\-]?\s*\n?\s*([A-Z]{5}[0-9]{4}[A-Z])',
        text.upper(), re.IGNORECASE)
    return match.group(1) if match else ""


# ─────────────────────────────────────────────────────────────────
# PHONE
# ─────────────────────────────────────────────────────────────────
def _extract_phone(text):
    # Indian mobile: 10 digits starting with 6-9
    match = re.search(r'\b([6-9]\d{9})\b', text)
    if match:
        return match.group(1)
    # With country code +91
    match = re.search(r'(?:\+91|0091)[\s\-]?([6-9]\d{9})\b', text)
    return match.group(1) if match else ""


# ─────────────────────────────────────────────────────────────────
# DOB
# ─────────────────────────────────────────────────────────────────
def _extract_dob(text):
    def try_parse(s):
        try:
            return date_parser.parse(s, dayfirst=True).strftime("%d/%m/%Y")
        except Exception:
            return None

    # Strategy 1: labelled DOB
    label_pat = (r'(?:DOB|D\.O\.B\.?|Date\s+of\s+Birth|Birth\s+Date|'
                 r'जन्म\s*(?:तिथि|दिनांक))\s*[:\-]?\s*'
                 r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})')
    match = re.search(label_pat, text, re.IGNORECASE)
    if match:
        result = try_parse(match.group(1))
        if result:
            return result

    # Strategy 2: DD/MM/YYYY or DD-MM-YYYY or DD.MM.YYYY
    for m in re.finditer(r'\b(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})\b', text):
        result = try_parse(m.group(1))
        if result:
            # Validate year is reasonable (1900-2015 for a person)
            year = int(result.split('/')[-1])
            if 1900 <= year <= 2015:
                return result

    # Strategy 3: DD Month YYYY
    match = re.search(
        r'\b(\d{1,2}\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|'
        r'May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|'
        r'Nov(?:ember)?|Dec(?:ember)?)\s+\d{4})\b',
        text, re.IGNORECASE)
    if match:
        result = try_parse(match.group(1))
        if result:
            return result

    # Strategy 4: YYYY-MM-DD (ISO format)
    match = re.search(r'\b(\d{4}[\/\-\.]\d{2}[\/\-\.]\d{2})\b', text)
    if match:
        result = try_parse(match.group(1))
        if result:
            return result
    return ""


# ─────────────────────────────────────────────────────────────────
# GENDER
# ─────────────────────────────────────────────────────────────────
def _extract_gender(text):
    t = text.upper()
    if re.search(r'\bFEMALE\b|\bमहिला\b|\bSMT\b|\bMRS\b', t):
        return "Female"
    if re.search(r'\bMALE\b|\bपुरुष\b|\bSHRI\b', t):
        return "Male"
    return ""


# ─────────────────────────────────────────────────────────────────
# BANK ACCOUNT
# ─────────────────────────────────────────────────────────────────
def _extract_account_no(text):
    # Label-based (highest confidence)
    match = re.search(
        r'(?:Account\s*(?:No\.?|Number)|A/C\s*(?:No\.?|Number))'
        r'\s*[:\-]?\s*(\d{9,18})',
        text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # CIF No is NOT account number — explicitly skip it
    # Find any 9-18 digit number that isn't 12 digits (Aadhaar length)
    # and isn't preceded by CIF/MICR/IFSC context
    for m in re.finditer(r'\b(\d{9,18})\b', text):
        val = m.group(1)
        if len(val) == 12:
            continue  # likely Aadhaar
        # Check context before the match
        start = max(0, m.start() - 30)
        context = text[start:m.start()].upper()
        if re.search(r'CIF|MICR|PHONE|MOBILE|PINCODE|PIN\s*CODE', context):
            continue
        return val
    return ""


# ─────────────────────────────────────────────────────────────────
# IFSC
# ─────────────────────────────────────────────────────────────────
def _extract_ifsc(text):
    # Label-based first
    match = re.search(
        r'(?:IFSC|IFS)\s*(?:Code)?\s*[:\-]?\s*([A-Z]{4}0[A-Z0-9]{6})',
        text.upper())
    if match:
        return match.group(1)
    # Raw pattern
    match = re.search(r'\b([A-Z]{4}0[A-Z0-9]{6})\b', text.upper())
    return match.group(1) if match else ""


# ─────────────────────────────────────────────────────────────────
# BANK NAME
# ─────────────────────────────────────────────────────────────────
def _extract_bank_name(text):
    # Ordered longest→shortest to avoid partial match of short names
    BANKS = [
        'State Bank of India',
        'Bank of Maharashtra',
        'Punjab National Bank',
        'Bank of Baroda',
        'Canara Bank',
        'Union Bank of India',
        'Central Bank of India',
        'Indian Overseas Bank',
        'Indian Bank',
        'UCO Bank',
        'IDBI Bank',
        'HDFC Bank',
        'ICICI Bank',
        'Axis Bank',
        'Kotak Mahindra Bank',
        'IndusInd Bank',
        'Yes Bank',
        'Federal Bank',
        'South Indian Bank',
        'Karnataka Bank',
        # Short forms last
        'SBI', 'HDFC', 'ICICI', 'PNB', 'BOB',
    ]
    text_lower = text.lower()
    for bank in BANKS:
        if bank.lower() in text_lower:
            return bank
    return ""


# ─────────────────────────────────────────────────────────────────
# BRANCH
# ─────────────────────────────────────────────────────────────────
def _extract_branch(text, doc_type=None):
    # Skip "Branch Manager", "Branch Code", "Branch Officer" — not branch names
    SKIP = r'\b(?:Manager|Code|Officer|No\.?|Number)\b'

    # Label-based: "Branch Name: Dasna" or "Branch: Hapur Road"
    match = re.search(
        r'Branch\s*(?:Name|Office)?\s*[:\-]\s*([A-Za-z][A-Za-z\s]{2,30}?)(?:\n|,|$)',
        text, re.IGNORECASE)
    if match:
        val = match.group(1).strip()
        if not re.search(SKIP, val, re.IGNORECASE) and not val.isdigit():
            return val.title()

    # Bank passbook: location line after bank name (ALL_CAPS place name)
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if re.search(r'State Bank|SBI|HDFC|ICICI|PNB|Bank of|Canara|Axis',
                     line, re.IGNORECASE):
            # Check next 1-2 lines for a place name
            for j in range(i + 1, min(i + 3, len(lines))):
                candidate = lines[j].strip()
                clean = re.sub(r'[^A-Za-z\s]', '', candidate).strip()
                words = clean.split()
                # Valid: 1-4 words, each 3+ chars, all uppercase (place names on passbooks)
                if (1 <= len(words) <= 4
                        and all(len(w) >= 3 for w in words)
                        and all(w.isupper() for w in words)
                        and not re.search(SKIP, clean, re.IGNORECASE)):
                    return clean.title()
    return ""


# ─────────────────────────────────────────────────────────────────
# PASSPORT
# ─────────────────────────────────────────────────────────────────
def _extract_passport_no(text):
    match = re.search(r'\b([A-Z][0-9]{7})\b', text.upper())
    return match.group(1) if match else ""

def _extract_passport_expiry(text):
    match = re.search(
        r'(?:Expiry|Date\s+of\s+Expiry|Valid\s+Until|Expiry\s+Date)'
        r'\s*[:\-]?\s*(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})',
        text, re.IGNORECASE)
    return match.group(1) if match else ""

def _extract_nationality(text):
    # Most Indian documents — default to Indian
    if re.search(r'\bINDIA\b|\bINDIAN\b|\bभारत\b', text.upper()):
        return "Indian"
    match = re.search(r'Nationality\s*[:\-]?\s*([A-Za-z]+)', text, re.IGNORECASE)
    return match.group(1).strip().title() if match else ""


# ─────────────────────────────────────────────────────────────────
# CASTE / CATEGORY
# ─────────────────────────────────────────────────────────────────
def _extract_category(text):
    t = text.upper()
    # Check full phrases first (more specific)
    if re.search(r'\bOTHER\s+BACKWARD\s+CLASS\b|\bOBC\b', t): return "OBC"
    if re.search(r'\bSCHEDULED\s+CASTE\b|\bS\.C\.\b|\bSC\b', t): return "SC"
    if re.search(r'\bSCHEDULED\s+TRIBE\b|\bS\.T\.\b|\bST\b', t): return "ST"
    if re.search(r'\bNOMADIC\s+TRIBE\b|\bD\.N\.T\b|\bNT\b', t): return "NT"
    if re.search(r'\bSPECIAL\s+BACKWARD\b|\bSBC\b', t): return "SBC"
    if re.search(r'\bVIMUKT\s+JATI\b|\bVJ\b', t): return "VJ"
    if re.search(r'\bGENERAL\b|\bOPEN\b|\bURGEN\b', t): return "General"
    return ""

def _extract_caste(text):
    # "belongs to the MALI Caste which is recognised as..."
    match = re.search(
        r'belongs\s+to\s+the\s+([A-Z][A-Za-z]+)\s+Caste',
        text, re.IGNORECASE)
    if match:
        val = match.group(1).strip()
        if val.lower() not in BAD_NAME_WORDS and len(val) >= 2:
            return val.title()
    # "Caste: Mali" or "Caste - Mali"
    match = re.search(
        r'(?:^|\n|\s)Caste\s*[:\-]\s*([A-Za-z]{2,30})',
        text, re.IGNORECASE | re.MULTILINE)
    if match:
        val = match.group(1).strip()
        if val.lower() not in BAD_NAME_WORDS:
            return val.title()
    return ""


# ─────────────────────────────────────────────────────────────────
# MARKSHEET FIELDS
# ─────────────────────────────────────────────────────────────────
def _extract_percentage(text):
    # Label-based: "Percentage  74.80" or "Percentage/टक्केवारी  50.67"
    match = re.search(
        r'(?:Percentage|टक्केवारी|PERCENTAGE|Per\s*Cent)'
        r'[/\s]*(?:टक्केवारी)?\s*[:\-]?\s*'
        r'(\d{2,3}(?:\.\d{1,2})?)',
        text, re.IGNORECASE)
    if match:
        val = float(match.group(1))
        if 30.0 <= val <= 100.0:
            return str(match.group(1)) + '%'

    # Any decimal in valid range (30.00-100.00)
    for m in re.finditer(r'\b(\d{2,3}\.\d{1,2})\b', text):
        val = float(m.group(1))
        if 30.0 <= val <= 100.0:
            # Make sure it's not a year or other number
            context = text[max(0, m.start()-20):m.start()].lower()
            if not re.search(r'year|code|no\.?|seat|roll', context):
                return m.group(1) + '%'

    # Integer percentage
    match = re.search(r'\b(\d{2,3})\s*%', text)
    if match and 30 <= int(match.group(1)) <= 100:
        return match.group(1) + '%'

    # CGPA
    match = re.search(r'(?:CGPA|GPA)\s*[:\-]?\s*(\d+\.\d{1,2})', text, re.IGNORECASE)
    if match:
        return match.group(1) + ' CGPA'
    return ""


def _extract_marks_obtained(text):
    # "Total Marks | 600 | 304" — second number is obtained
    match = re.search(
        r'(?:Total\s*Marks|एकूण\s*गुण)\s*[\|]?\s*(\d{3,4})\s*[\|]?\s*(\d{3,4})',
        text, re.IGNORECASE)
    if match:
        total, obtained = int(match.group(1)), int(match.group(2))
        if 0 < obtained <= total:
            return str(obtained)

    # "304  THREE HUNDRED AND FOUR" — number before word-form
    match = re.search(
        r'\b(\d{3,4})\s+'
        r'(?:ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE)\s+HUNDRED',
        text, re.IGNORECASE)
    if match:
        val = int(match.group(1))
        if 100 <= val <= 9000:
            return str(val)

    # Fraction: 374/500
    match = re.search(r'\b(\d{3,4})\s*/\s*\d{3,4}\b', text)
    if match:
        return match.group(1)

    # Explicit label
    match = re.search(
        r'(?:Marks\s+Obtained|Obtained\s+Marks|प्राप्त\s+गुण)\s*[:\-]?\s*(\d{3,4})',
        text, re.IGNORECASE)
    return match.group(1) if match else ""


def _extract_total_marks(text):
    # "Total Marks  600  304" — first is max
    match = re.search(
        r'(?:Total\s*Marks|एकूण\s*गुण)\s*[\|]?\s*(\d{3,4})\s*[\|]?\s*\d{3,4}',
        text, re.IGNORECASE)
    if match:
        return match.group(1)
    # Fraction: 374/500 — second is max
    match = re.search(r'\b\d{3,4}\s*/\s*(\d{3,4})\b', text)
    return match.group(1) if match else ""


def _extract_subjects(text):
    SUBJECT_LIST = [
        'English', 'Mathematics', 'Maths', 'Science', 'History', 'Geography',
        'Physics', 'Chemistry', 'Biology', 'Hindi', 'Marathi', 'Sanskrit',
        'Urdu', 'Computer Science', 'Economics', 'Accounts', 'Commerce',
        'Political Science', 'Sociology', 'Psychology', 'Philosophy',
        'Social Sciences', 'Information Technology', 'Environmental Science',
        'Home Science', 'Physical Education', 'Drawing', 'Music',
    ]
    found = []
    text_lower = text.lower()
    for sub in SUBJECT_LIST:
        if sub.lower() in text_lower and sub not in found:
            found.append(sub)
    # Deduplicate (e.g. "Maths" and "Mathematics")
    if 'Mathematics' in found and 'Maths' in found:
        found.remove('Maths')
    return ', '.join(found[:6]) if found else ""


def _extract_roll_no(text):
    # Label + value: "SEAT NO.  C022308" or "Roll No: 240-B"
    match = re.search(
        r'(?:Seat\s*No\.?|SEAT\s*NO\.?|Roll\s*No\.?|Roll\s*Number|'
        r'Reg(?:istration)?\s*No\.?|Admission\s*No\.?)\s*[:\-]?\s*'
        r'([A-Z]{0,3}\d{4,10}(?:[A-Z\-]\d*)?)',
        text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Standalone: letter + 6-9 digits (e.g. C022308, M064043)
    match = re.search(r'\b([A-Z]\d{6,9})\b', text)
    if match:
        return match.group(1)

    # Pure numeric: 6-10 digit roll number after label on next line
    match = re.search(
        r'(?:Seat|Roll|Reg|Admission)\s*(?:No\.?)?\s*\n\s*(\d{5,10})',
        text, re.IGNORECASE)
    return match.group(1) if match else ""


def _extract_board_name(text):
    BOARDS = [
        ('Maharashtra State Board',
         ['Maharashtra State Board', 'MSBSHSE', 'माध्यमिक व उच्च माध्यमिक',
          'Secondary and Higher Secondary']),
        ('CBSE', ['CBSE', 'Central Board of Secondary Education']),
        ('ICSE', ['ICSE', 'Council for the Indian School Certificate']),
        ('NIOS', ['NIOS', 'National Institute of Open Schooling']),
        ('SSC', ['SSC Board']),
        ('HSC', ['HSC Board']),
        ('Mumbai University', ['Mumbai University', 'University of Mumbai']),
        ('Pune University', ['Pune University', 'Savitribai Phule Pune University']),
        ('Delhi University', ['Delhi University', 'University of Delhi']),
    ]
    text_lower = text.lower()
    for board_name, keywords in BOARDS:
        for kw in keywords:
            if kw.lower() in text_lower:
                return board_name
    return ""


def _extract_passing_year(text, doc_type=None):
    # "MARCH-2016" or "FEBRUARY-2002" — most reliable for marksheets
    match = re.search(
        r'(?:JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|'
        r'SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s*[-–]\s*(20\d{2}|19\d{2})',
        text, re.IGNORECASE)
    if match:
        return match.group(1)

    # "Year of Passing: 2019" label
    match = re.search(
        r'(?:Year\s+of\s+Passing|Passing\s+Year)\s*[:\-]?\s*(20\d{2}|19\d{2})',
        text, re.IGNORECASE)
    if match:
        return match.group(1)

    # School leaving: "from 2016 to 2019" — take the TO year
    if doc_type == 'school_leaving':
        match = re.search(
            r'(?:from|remained)\s+(?:20\d{2}|19\d{2})\s+to\s+(20\d{2}|19\d{2})',
            text, re.IGNORECASE)
        if match:
            return match.group(1)

    # Last 4-digit year in a reasonable range
    years = re.findall(r'\b(20\d{2}|19\d{2})\b', text)
    valid = [y for y in years if 1980 <= int(y) <= 2030]
    return valid[-1] if valid else ""


def _extract_school_name(text, doc_type=None):
    TABLE_WORDS = {'seat', 'centre', 'dist', 'month', 'year', 'srno',
                   'statement', 'code', 'subject', 'marks', 'medium',
                   'max', 'figures', 'words', 'grade', 'no', 'stream',
                   'exam', 'examination', 'board'}

    # Marksheet: only extract Division city
    if doc_type in ('marksheet_10', 'marksheet_12'):
        match = re.search(r'Division\s*[:\-]?\s*([A-Za-z]{3,20})', text, re.IGNORECASE)
        if match:
            return match.group(1).strip().title() + ' Division'
        return ""

    # School leaving: look for school name in first 8 lines
    if doc_type == 'school_leaving':
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for line in lines[:8]:
            if re.search(
                r'\b(?:School|Public|High|Academy|Institute|Vidyalaya|Vidyapeeth|Madrasa)\b',
                    line, re.IGNORECASE):
                if not re.search(
                    r'\b(?:Leaving|Certificate|Board|Examination|Certified|that|No\.?)\b',
                        line, re.IGNORECASE):
                    clean = re.sub(r'[^A-Za-z\s]', ' ', line).strip()
                    clean = re.sub(r'\s+', ' ', clean).strip()
                    if 5 < len(clean) < 80:
                        return clean.title()
        return ""

    # General: first meaningful school/college line
    for line in text.split('\n'):
        line = line.strip()
        if re.search(
            r'\b(?:School|College|Institute|University|Vidyalaya)\b',
                line, re.IGNORECASE):
            if not re.search(
                r'\b(?:Leaving|Certificate|Board|Examination)\b',
                    line, re.IGNORECASE):
                clean = re.sub(r'[^A-Za-z\s]', ' ', line).strip()
                clean = re.sub(r'\s+', ' ', clean).strip()
                words_lower = clean.lower().split()
                if not any(w in TABLE_WORDS for w in words_lower):
                    if 5 < len(clean) < 80:
                        return clean.title()
    return ""


def _extract_income(text):
    # "Rs. 1,20,000" or "INR 120000" or "₹ 120000"
    match = re.search(
        r'(?:Rs\.?|INR|₹)\s*([\d,]+)',
        text, re.IGNORECASE)
    if match:
        return match.group(1).replace(',', '')
    # Label-based
    match = re.search(
        r'(?:Annual\s+Income|Total\s+Income|Income)\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+)',
        text, re.IGNORECASE)
    return match.group(1).replace(',', '') if match else ""


def _extract_birth_place(text):
    match = re.search(
        r'(?:Place\s+of\s+Birth|Birth\s+Place|Born\s+at|Place\s+of\s+Origin)'
        r'\s*[:\-]?\s*([A-Za-z][A-Za-z\s]{2,30}?)(?:\n|,|$)',
        text, re.IGNORECASE)
    if match:
        val = match.group(1).strip()
        if len(val) >= 3:
            return val.title()
    return ""


def _extract_father_name(text):
    match = re.search(
        r'(?:Father[\'s]*\s*(?:Name)?|S/O|Son\s+of)\s*[:\-]?\s*'
        r'(?:Mr\.?|Shri\.?)?\s*([A-Za-z][A-Za-z\s]{2,40}?)(?:\s{2,}|\n|,|$)',
        text, re.IGNORECASE)
    if match:
        name = _clean_name(match.group(1))
        if _is_valid_name(name):
            return name
    return ""


def _extract_mother_name(text):
    match = re.search(
        r'(?:Mother[\'s]*\s*(?:Name)?|D/O|Daughter\s+of|W/O|Wife\s+of)'
        r'\s*[:\-]?\s*(?:Mrs\.?|Smt\.?|Ms\.?)?\s*'
        r'([A-Za-z][A-Za-z\s]{2,40}?)(?:\s{2,}|\n|,|$)',
        text, re.IGNORECASE)
    if match:
        name = _clean_name(match.group(1))
        if _is_valid_name(name):
            return name
    return ""


def _extract_employer_name(text):
    match = re.search(
        r'(?:Employer|Employer[\'s]*\s*Name|Company|Organization|Firm|'
        r'Name\s+of\s+Employer)\s*[:\-]?\s*([A-Za-z][A-Za-z\s\.\,]{2,60}?)(?:\n|$)',
        text, re.IGNORECASE)
    if match:
        val = match.group(1).strip()
        if len(val) >= 3:
            return val.title()
    return ""