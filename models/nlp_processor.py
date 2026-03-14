import re
from dateutil import parser as date_parser


# ── Document type → which fields to extract ───────────────────────
DOC_FIELD_MAP = {
    'aadhaar_doc':    ['name', 'dob', 'aadhaar', 'address', 'gender'],
    'pan_doc':        ['name', 'pan', 'dob'],
    'marksheet_10':   ['name', 'percentage', 'board_name', 'passing_year',
                       'school_name', 'marks_obtained', 'total_marks',
                       'subjects', 'roll_no'],
    'marksheet_12':   ['name', 'percentage', 'board_name', 'passing_year',
                       'school_name', 'marks_obtained', 'total_marks',
                       'subjects', 'roll_no'],
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


def extract_entities(raw_text: str, doc_type: str = None) -> dict:
    """
    Main function — backend calls this.
    Input:  raw text string from OCR, doc_type string (e.g. 'aadhaar_doc')
    Output: dict with only the fields relevant to that document type
    """
    fields_to_extract = DOC_FIELD_MAP.get(doc_type, DEFAULT_FIELDS)

    all_extractors = {
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
        'branch':          _extract_branch,
        'passport_number': _extract_passport_no,
        'passport_expiry': _extract_passport_expiry,
        'nationality':     _extract_nationality,
        'birth_place':     _extract_birth_place,
        'category':        _extract_category,
        'caste':           _extract_caste,
        'percentage':      _extract_percentage,
        'board_name':      _extract_board_name,
        'passing_year':    _extract_passing_year,
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
        if field in all_extractors:
            result[field] = all_extractors[field](raw_text)
    return result


# ── Shared bad words ──────────────────────────────────────────────
BAD_NAME_WORDS = {
    'date', 'dob', 'of', 'birth', 'father', 'mother', 'gender',
    'male', 'female', 'card', 'aadhaar', 'india', 'government',
    'address', 'phone', 'mobile', 'unique', 'authority', 'name',
    'delhi', 'mumbai', 'pune', 'bangalore', 'hyderabad', 'chennai',
    'kolkata', 'new', 'bagh', 'nagar', 'road', 'street', 'block',
    'sector', 'district', 'state', 'village', 'post', 'pin',
    'pass', 'fail', 'result', 'board', 'exam', 'certificate',
    'division', 'arts', 'science', 'commerce', 'stream', 'seat',
    'centre', 'dist', 'school', 'month', 'year', 'srno', 'statement',
    'secondary', 'higher', 'education', 'maharashtra', 'candidate',
    'surname', 'first', 'full', 'leaving', 'admission', 'certified',
    'that', 'son', 'daughter', 'has', 'been', 'student', 'class',
    'the', 'and', 'for', 'reg', 'ref', 'std', 'div', 'no',
}


# ── FIX 2: Name — per-doc patterns + smart fallback ──────────────
def _clean_name(raw: str) -> str:
    """
    Post-process a raw extracted name:
    - Remove 1-2 char OCR noise tokens from start/end (e.g. 'Fw', 'I', 'K')
    - Stop at relational words (son, daughter, of, s/o, d/o)
    - Remove trailing bad words
    - Title-case result
    """
    # Stop at relational/noise words
    raw = re.split(r'\b(?:son|daughter|s/o|d/o|w/o|of|and)\b', raw, flags=re.IGNORECASE)[0]
    words = raw.strip().split()
    # Remove leading/trailing tokens that are 1-2 chars (OCR noise like Fw, I, K)
    while words and len(words[0]) <= 2:
        words.pop(0)
    while words and len(words[-1]) <= 2:
        words.pop()
    # Remove words that are in bad name words
    words = [w for w in words if w.lower() not in BAD_NAME_WORDS]
    # Keep only words that look like names (start with letter, mostly alpha)
    words = [w for w in words if re.match(r'^[A-Za-z][a-z]*$', w) or re.match(r'^[A-Z]+$', w)]
    if not words:
        return ""
    return ' '.join(words[:5]).title()


def _extract_name(text, doc_type=None):

    # ── MARKSHEET: "CANDIDATE'S FULL NAME" header → next non-empty line ──
    if doc_type in ('marksheet_10', 'marksheet_12'):
        match = re.search(
            r"CANDIDATE['\u2019]*S?\s+FULL\s+NAME[^\n]*\n\s*([^\n]{3,60})(?:\n|$)",
            text, re.IGNORECASE)
        if match:
            raw = match.group(1).strip()
            # Remove OCR noise: keep only alpha words of 2+ chars
            words = re.findall(r'\b[A-Za-z]{2,}\b', raw)
            words = [w for w in words if w.lower() not in BAD_NAME_WORDS]
            # Remove leading/trailing 1-2 char tokens
            while words and len(words[0]) <= 2:
                words.pop(0)
            while words and len(words[-1]) <= 2:
                words.pop()
            if words:
                return ' '.join(words[:5]).title()

    # ── CASTE CERT: "certify that Mrs/Mr/Shri/Smt X Y Z" ────────
    if doc_type == 'caste_cert':
        match = re.search(
            r'certify\s+that\s+(?:Mrs?\.?|Shri\.?|Smt\.?|Dr\.?)?\s*'
            r'([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,5})',
            text, re.IGNORECASE)
        if match:
            return _clean_name(match.group(1))

    # ── SCHOOL LEAVING: "Certified that X son/daughter of" ───────
    if doc_type == 'school_leaving':
        match = re.search(
            r'[Cc]ertified\s+that\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,4})'
            r'\s+(?:son|daughter|s/o|d/o)',
            text, re.IGNORECASE)
        if match:
            return _clean_name(match.group(1))

    # ── AADHAAR / PAN / GENERAL: Name label same line ────────────
    match = re.search(
        r'(?:^|\n)\s*(?:Name|NAME|नाम)\s*[:\-]?\s*'
        r'([A-Za-z][a-z]+(?:\s[A-Za-z][a-z]+){0,3})',
        text, re.MULTILINE)
    if match:
        return _clean_name(match.group(1))

    # Name on next line after Name: label (Aadhaar OCR noise)
    match = re.search(
        r'(?:Name|NAME|नाम)\s*[:\-]?\s*\n[^\w\n]*'
        r'([A-Za-z][a-z]+(?:\s[A-Za-z][a-z]+){0,3})',
        text)
    if match:
        return _clean_name(match.group(1))

    # ── Smart fallback: short line of 2-4 capitalized proper words ─
    for line in text.split('\n'):
        words = re.findall(r'\b[A-Za-z]{3,}\b', line)
        if 2 <= len(words) <= 4:
            clean = [w for w in words if w.lower() not in BAD_NAME_WORDS]
            if len(clean) == len(words) and all(w[0].isupper() for w in clean):
                # Extra check: all words should look like name words (not ALL_CAPS keywords)
                if all(not w.isupper() or len(w) <= 4 for w in clean):
                    return ' '.join(clean[:4]).title()
    return ""


# ── FIX 5: Address — strip all noise chars and stray tokens ──────
def _extract_address(text):
    def _clean_addr_line(line):
        # Strip non-ASCII
        clean = re.sub(r'[^A-Za-z0-9,\s\-\/]', '', line).strip()
        # Remove standalone 1-2 char tokens (e.g. 'w', 'clea' is short noise)
        clean = re.sub(r'\b[A-Za-z]{1,2}\b', '', clean)
        # Remove short noise words that aren't real (less than 3 chars after strip)
        # Keep known short but valid words
        tokens = clean.split()
        tokens = [t for t in tokens if len(t) >= 3 or t.isdigit()]
        clean = ' '.join(tokens)
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

    pattern = r'(?:Address|ADDRESS|पता)\s*[:\-]?\s*([\s\S]+?)(?:\n\s*\n|\Z)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        lines = [l.strip() for l in match.group(1).split('\n') if l.strip()]
        result_lines = []
        for line in lines[:6]:
            clean = _clean_addr_line(line)
            # Must have at least one real word of 3+ letters or a digit group
            real_words = re.findall(r'\b[A-Za-z]{3,}\b', clean)
            digits     = re.findall(r'\b\d{4,}\b', clean)
            if (real_words or digits) and len(clean) > 4:
                result_lines.append(clean)
            if re.search(r'\b\d{6}\b', line):
                break
        if result_lines:
            return ', '.join(result_lines)

    # Fallback — pincode-based
    pin_match = re.search(r'(.{20,200}?\b\d{6}\b)', text, re.DOTALL)
    if pin_match:
        addr = re.sub(r'[^A-Za-z0-9,\s\-\/]', ' ', pin_match.group(1))
        # Remove 1-2 char stray tokens
        addr = re.sub(r'\b[A-Za-z]{1,2}\b', '', addr)
        addr = re.sub(r'\s+', ' ', addr).strip()
        return addr
    return ""


# ── Basic extractors ──────────────────────────────────────────────
def _extract_aadhaar(text):
    match = re.search(r'\b\d{4}\s\d{4}\s\d{4}\b|\b\d{12}\b', text)
    return match.group().replace(" ", "") if match else ""

def _extract_pan(text):
    match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text.upper())
    return match.group() if match else ""

def _extract_phone(text):
    match = re.search(r'\b[6-9]\d{9}\b', text)
    return match.group() if match else ""

def _extract_dob(text):
    label_pat = r'(?:DOB|D\.O\.B|Date of Birth|Birth Date|जन्म तिथि)\s*[:\-]?\s*(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})'
    match = re.search(label_pat, text, re.IGNORECASE)
    if match:
        try:
            return date_parser.parse(match.group(1), dayfirst=True).strftime("%d/%m/%Y")
        except Exception:
            return match.group(1)
    for pat in [
        r'\b(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})\b',
        r'\b(\d{2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b',
        r'\b(\d{4}[\/\-\.]\d{2}[\/\-\.]\d{2})\b',
    ]:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            try:
                return date_parser.parse(match.group(1), dayfirst=True).strftime("%d/%m/%Y")
            except Exception:
                return match.group(1)
    return ""

def _extract_gender(text):
    if re.search(r'\bFEMALE\b|\bमहिला\b', text.upper()):
        return "Female"
    if re.search(r'\bMALE\b|\bपुरुष\b', text.upper()):
        return "Male"
    return ""

def _extract_account_no(text):
    match = re.search(r'\b(\d{9,11}|\d{13,18})\b', text)
    return match.group() if match else ""

def _extract_ifsc(text):
    match = re.search(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', text.upper())
    return match.group() if match else ""

def _extract_bank_name(text):
    banks = ['State Bank of India', 'SBI', 'HDFC Bank', 'HDFC',
             'ICICI Bank', 'ICICI', 'Bank of Maharashtra',
             'Punjab National Bank', 'PNB', 'Canara Bank',
             'Axis Bank', 'Bank of Baroda', 'BOB', 'Union Bank', 'Kotak']
    for bank in banks:
        if bank.lower() in text.lower():
            return bank
    return ""

def _extract_branch(text):
    match = re.search(r'(?:Branch|BRANCH)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|$)', text, re.IGNORECASE)
    return match.group(1).strip().title() if match else ""

def _extract_passport_no(text):
    match = re.search(r'\b[A-Z][0-9]{7}\b', text.upper())
    return match.group() if match else ""

def _extract_passport_expiry(text):
    match = re.search(r'(?:Expiry|Valid Until|Date of Expiry)\s*[:\-]?\s*(\d{2}[\/\-]\d{2}[\/\-]\d{4})', text, re.IGNORECASE)
    return match.group(1) if match else ""

def _extract_nationality(text):
    if 'indian' in text.lower() or 'india' in text.lower():
        return "Indian"
    match = re.search(r'(?:Nationality)\s*[:\-]?\s*([A-Za-z]+)', text, re.IGNORECASE)
    return match.group(1).strip().title() if match else ""

def _extract_category(text):
    t = text.upper()
    if re.search(r'\bOTHER BACKWARD CLASS\b|\bOBC\b', t): return "OBC"
    if re.search(r'\bSCHEDULED CASTE\b|\bSC\b', t):      return "SC"
    if re.search(r'\bSCHEDULED TRIBE\b|\bST\b', t):      return "ST"
    if re.search(r'\bNOMADIC TRIBE\b|\bNT\b', t):        return "NT"
    if re.search(r'\bSPECIAL BACKWARD\b|\bSBC\b', t):    return "SBC"
    if re.search(r'\bGENERAL\b|\bOPEN\b', t):            return "General"
    return ""

def _extract_caste(text):
    # "belongs to the MALI Caste"
    match = re.search(r'belongs\s+to\s+the\s+([A-Z][A-Za-z]+)\s+Caste', text, re.IGNORECASE)
    if match:
        return match.group(1).strip().title()
    match = re.search(r'(?:^|\s)Caste\s*[:\-]\s*([A-Za-z]+)', text, re.IGNORECASE | re.MULTILINE)
    if match:
        return match.group(1).strip().title()
    return ""

def _extract_percentage(text):
    # Label-based: "Percentage/टक्केवारी  74.80"
    match = re.search(
        r'(?:Percentage|टक्केवारी|PERCENTAGE)\s*[/\s]*(?:टक्केवारी)?\s*[:\-]?\s*(\d{2,3}\.\d{1,2})',
        text, re.IGNORECASE)
    if match:
        val = float(match.group(1))
        if 30 <= val <= 100:
            return str(match.group(1)) + '%'
    # Any decimal in 30-100 range
    for m in re.findall(r'\b(\d{2,3}\.\d{1,2})\b', text):
        if 30.0 <= float(m) <= 100.0:
            return m + '%'
    # Integer percentage
    match = re.search(r'\b(\d{2,3})\s*%', text)
    if match and 30 <= int(match.group(1)) <= 100:
        return match.group(1) + '%'
    return ""


# ── FIX 3: marks_obtained and total_marks ────────────────────────
def _extract_marks_obtained(text):
    # Maharashtra marksheet row: "Total Marks  600  304" or "Total Marks | 600 | 304"
    # Try with explicit Total Marks keyword — second number is obtained
    match = re.search(
        r'(?:Total\s*Marks|एकूण\s*गुण)\s*[\|]?\s*(\d{3,4})\s*[\|]?\s*(\d{3,4})',
        text, re.IGNORECASE)
    if match:
        total, obtained = int(match.group(1)), int(match.group(2))
        if obtained <= total:
            return str(obtained)

    # Maharashtra marksheet: last line before "THREE/FOUR HUNDRED..." in words
    # e.g. "304   THREE HUNDRED AND FOUR"
    match = re.search(
        r'\b(\d{3,4})\s+(?:ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE)\s+HUNDRED',
        text, re.IGNORECASE)
    if match:
        val = int(match.group(1))
        if 100 <= val <= 9000:
            return str(val)

    # Also try "PASS  74.80  Total Marks 500  374  THREE HUNDRED..."
    # Find last 3-4 digit number just before a word-form number
    match = re.search(
        r'(\d{3,4})\s+(?:THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|ONE|TWO)\s+HUNDRED\s+AND',
        text, re.IGNORECASE)
    if match:
        return match.group(1)

    # Fraction: 374/500
    match = re.search(r'\b(\d{3,4})\s*/\s*\d{3,4}\b', text)
    if match:
        return match.group(1)

    # Explicit label
    match = re.search(r'(?:Marks Obtained|Obtained Marks|प्राप्त गुण)\s*[:\-]?\s*(\d{3,4})', text, re.IGNORECASE)
    return match.group(1) if match else ""


def _extract_total_marks(text):
    # "Total Marks  600  304" — first number is max
    match = re.search(
        r'(?:Total\s*Marks|एकूण\s*गुण)\s*[\|]?\s*(\d{3,4})\s*[\|]?\s*\d{3,4}',
        text, re.IGNORECASE)
    if match:
        return match.group(1)
    # Fraction: 374/500 — second is total
    match = re.search(r'\b\d{3,4}\s*/\s*(\d{3,4})\b', text)
    return match.group(1) if match else ""


def _extract_subjects(text):
    subjects = []
    common = [
        'English', 'Mathematics', 'Science', 'History', 'Geography',
        'Physics', 'Chemistry', 'Biology', 'Hindi', 'Marathi', 'Sanskrit',
        'Urdu', 'Computer Science', 'Economics', 'Accounts', 'Commerce',
        'Political Science', 'Sociology', 'Psychology', 'Philosophy',
        'Social Sciences', 'Information Technology'
    ]
    for sub in common:
        if sub.lower() in text.lower():
            subjects.append(sub)
    return ', '.join(subjects[:6]) if subjects else ""


# ── FIX 4: roll_no — handle all seat/roll formats ────────────────
def _extract_roll_no(text):
    # Label + value on same line: "SEAT NO.   C022308"
    match = re.search(
        r'(?:Seat\s*No\.?|SEAT\s*NO\.?|Roll\s*No\.?|Roll\s*Number|'
        r'Reg\s*No\.?|Registration\s*No\.?|Admission\s*No\.?)\s*[:\-]?\s*'
        r'([A-Z]{0,2}\d{5,10})',
        text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Standalone: letter + 6-9 digits — e.g. C022308, M064043, S160795911
    match = re.search(r'\b([A-Z]\d{6,9})\b', text)
    if match:
        return match.group(1)

    # Pure numeric after seat/roll label on next line
    match = re.search(
        r'(?:Seat|Roll|Reg|Admission)\s*(?:No\.?)?\s*\n\s*(\d{5,10})',
        text, re.IGNORECASE)
    return match.group(1) if match else ""


# ── FIX 1: school_name — doc-specific, no table headers ──────────
def _extract_school_name(text, doc_type=None):

    # ── MARKSHEET: only extract Division city ─────────────────────
    if doc_type in ('marksheet_10', 'marksheet_12'):
        match = re.search(r'Division\s*[:\-]?\s*([A-Za-z]+)', text, re.IGNORECASE)
        if match:
            val = match.group(1).strip()
            if re.match(r'^[A-Za-z]{3,20}$', val):
                return val.title() + ' Division'
        return ""

    # ── SCHOOL LEAVING: school name from top lines ─────────────────
    if doc_type == 'school_leaving':
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for line in lines[:8]:
            if re.search(r'\b(?:School|Public|High|Academy|Institute|Vidyalaya|Vidyapeeth)\b', line, re.IGNORECASE):
                if not re.search(r'\b(?:Leaving|Certificate|Board|Examination|Certified|that)\b', line, re.IGNORECASE):
                    clean = re.sub(r'[^A-Za-z\s]', ' ', line).strip()
                    clean = re.sub(r'\s+', ' ', clean).strip()
                    if 5 < len(clean) < 80:
                        return clean.title()
        return ""

    # ── GENERAL: first meaningful line with school/college keyword ─
    TABLE_WORDS = {'seat', 'centre', 'dist', 'month', 'year', 'srno',
                   'statement', 'code', 'subject', 'marks', 'medium',
                   'max', 'figures', 'words', 'grade', 'no'}
    for line in text.split('\n'):
        line = line.strip()
        if re.search(r'\b(?:School|College|Institute|University|Vidyalaya)\b', line, re.IGNORECASE):
            if not re.search(r'\b(?:Leaving|Certificate|Board|Examination)\b', line, re.IGNORECASE):
                clean = re.sub(r'[^A-Za-z\s]', ' ', line).strip()
                clean = re.sub(r'\s+', ' ', clean).strip()
                if not any(w in TABLE_WORDS for w in clean.lower().split()):
                    if 5 < len(clean) < 80:
                        return clean.title()
    return ""

def _extract_board_name(text):
    boards = [
        ('Maharashtra State Board', ['Maharashtra State Board', 'MSBSHSE', 'माध्यमिक व उच्च माध्यमिक']),
        ('CBSE', ['CBSE', 'Central Board of Secondary']),
        ('ICSE', ['ICSE', 'Council for the Indian School']),
        ('SSC', ['SSC']),
        ('HSC', ['HSC']),
        ('Mumbai University', ['Mumbai University', 'University of Mumbai']),
        ('Pune University', ['Pune University', 'Savitribai Phule']),
    ]
    for board_name, keywords in boards:
        for kw in keywords:
            if kw.lower() in text.lower():
                return board_name
    return ""

def _extract_passing_year(text):
    # "MARCH-2016" or "FEBRUARY-2002"
    match = re.search(
        r'(?:JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)'
        r'\s*[-–]\s*(20\d{2}|19\d{2})',
        text, re.IGNORECASE)
    if match:
        return match.group(1)
    # "Year of Passing: 2019"
    match = re.search(r'(?:Year of Passing|Passing Year)\s*[:\-]?\s*(20\d{2}|19\d{2})', text, re.IGNORECASE)
    if match:
        return match.group(1)
    # School leaving: "from 2016 to 2019" — take the TO year
    match = re.search(r'from\s+(?:20\d{2}|19\d{2})\s+to\s+(20\d{2}|19\d{2})', text, re.IGNORECASE)
    if match:
        return match.group(1)
    # Last 4-digit year in document
    matches = re.findall(r'\b(20\d{2}|19\d{2})\b', text)
    return matches[-1] if matches else ""

def _extract_income(text):
    match = re.search(r'(?:Rs\.?|INR|/-|₹)\s*([\d,]+)', text, re.IGNORECASE)
    return match.group(1).replace(',', '') if match else ""

def _extract_birth_place(text):
    match = re.search(r'(?:Place of Birth|Birth Place|Born at)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|,|$)', text, re.IGNORECASE)
    return match.group(1).strip().title() if match else ""

def _extract_father_name(text):
    match = re.search(
        r'(?:son of|S/O|Father[\'s]*\s*Name|Father)\s*[:\-]?\s*'
        r'([A-Za-z]+(?:\s[A-Za-z]+){0,3})',
        text, re.IGNORECASE)
    if match:
        name = re.sub(r'[^A-Za-z\s]', '', match.group(1)).strip()
        words = [w for w in name.split() if w.lower() not in BAD_NAME_WORDS]
        if words:
            return ' '.join(words[:4]).title()
    return ""

def _extract_mother_name(text):
    match = re.search(
        r'(?:daughter of|D/O|Mother[\'s]*\s*Name|Mother)\s*[:\-]?\s*'
        r'([A-Za-z]+(?:\s[A-Za-z]+){0,3})',
        text, re.IGNORECASE)
    if match:
        name = re.sub(r'[^A-Za-z\s]', '', match.group(1)).strip()
        words = [w for w in name.split() if w.lower() not in BAD_NAME_WORDS]
        if words:
            return ' '.join(words[:4]).title()
    return ""

def _extract_employer_name(text):
    match = re.search(r'(?:Employer|Company|Organization|Firm)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|$)', text, re.IGNORECASE)
    return match.group(1).strip().title() if match else ""