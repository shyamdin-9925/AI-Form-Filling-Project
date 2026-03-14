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
def _extract_name(text, doc_type=None):

    # ── MARKSHEET: "CANDIDATE'S FULL NAME" header then name on next line ──
    if doc_type in ('marksheet_10', 'marksheet_12'):
        # All-caps next line after header: "SHAIKH RAHIL AHMED SHABBIR AHMED"
        match = re.search(
            r"CANDIDATE['\u2019]*S?\s+FULL\s+NAME[^\n]*\n\s*"
            r"([A-Z][A-Z\s]{4,50}?)(?:\n|$)",
            text, re.IGNORECASE)
        if match:
            name = match.group(1).strip().title()
            # Clean any trailing garbage
            name = re.sub(r'\s+', ' ', name).strip()
            if len(name) > 3:
                return name
        # Mixed case next line: "Mudashinge Vaishnavee Sanjay"
        match = re.search(
            r"CANDIDATE['\u2019]*S?\s+FULL\s+NAME[^\n]*\n\s*"
            r"([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,4})",
            text)
        if match:
            return match.group(1).strip()

    # ── CASTE CERT: "certify that Mrs/Mr X" ──────────────────────
    if doc_type == 'caste_cert':
        match = re.search(
            r'certify\s+that\s+(?:Mrs?\.?|Shri|Smt\.?)?\s*'
            r'([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,4})',
            text, re.IGNORECASE)
        if match:
            return match.group(1).strip().title()

    # ── SCHOOL LEAVING: "Certified that X son of / daughter of" ──
    if doc_type == 'school_leaving':
        match = re.search(
            r'[Cc]ertified\s+that\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+){0,3})'
            r'\s+(?:son|daughter)',
            text, re.IGNORECASE)
        if match:
            return match.group(1).strip().title()

    # ── AADHAAR / PAN / GENERAL: Name label ──────────────────────
    # Same line: "Name Alka" or "Name: Alka Sharma"
    match = re.search(
        r'(?:^|\n)\s*(?:Name|NAME|नाम)\s*[:\-]?\s*'
        r'([A-Za-z][a-z]+(?:\s[A-Za-z][a-z]+){0,3})',
        text, re.MULTILINE)
    if match:
        words = match.group(1).strip().split()
        clean = [w for w in words if w.lower() not in BAD_NAME_WORDS]
        if clean:
            return ' '.join(clean[:4]).title()

    # Next line after Name: (Aadhaar OCR noise case)
    match = re.search(
        r'(?:Name|NAME|नाम)\s*[:\-]?\s*\n[^\w\n]*'
        r'([A-Za-z][a-z]+(?:\s[A-Za-z][a-z]+){0,3})',
        text)
    if match:
        words = match.group(1).strip().split()
        clean = [w for w in words if w.lower() not in BAD_NAME_WORDS]
        if clean:
            return ' '.join(clean[:4]).title()

    # ── Smart fallback: short line of 1-3 capitalized words ──────
    for line in text.split('\n'):
        words = re.findall(r'\b[A-Za-z]{3,}\b', line)
        if 1 <= len(words) <= 4:
            clean = [w for w in words if w.lower() not in BAD_NAME_WORDS]
            if len(clean) >= 1 and len(clean) == len(words):
                if all(w[0].isupper() for w in clean):
                    return ' '.join(clean[:4]).title()
    return ""


# ── FIX 5: Address — strip all noise chars ────────────────────────
def _extract_address(text):
    pattern = r'(?:Address|ADDRESS|पता)\s*[:\-]?\s*([\s\S]+?)(?:\n\s*\n|\Z)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        lines = [l.strip() for l in match.group(1).split('\n') if l.strip()]
        result_lines = []
        for line in lines[:6]:
            # Strip all non-ASCII and special chars
            clean = re.sub(r'[^A-Za-z0-9,\s\-\/]', '', line).strip()
            clean = re.sub(r'\s+', ' ', clean).strip()
            # Only keep line if it has at least one real word (3+ letters)
            # AND is not a single stray letter or symbol
            real_words = re.findall(r'\b[A-Za-z]{3,}\b', clean)
            digits     = re.findall(r'\b\d{4,}\b', clean)
            # Skip very short lines like "w" or "="
            if (real_words or digits) and len(clean) > 3:
                result_lines.append(clean)
            if re.search(r'\b\d{6}\b', line):
                break
        if result_lines:
            return ', '.join(result_lines)

    # Fallback — grab text surrounding a 6-digit pincode
    pin_match = re.search(r'(.{20,150}?\b\d{6}\b)', text, re.DOTALL)
    if pin_match:
        addr = re.sub(r'[^A-Za-z0-9,\s\-\/]', ' ', pin_match.group(1))
        addr = re.sub(r'\b[A-Za-z]\b', '', addr)   # remove single letters
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
    # Maharashtra marksheet: "Total Marks | 600 | 304" or "500   374"
    # The pattern is: keyword, then max marks, then obtained marks
    match = re.search(
        r'(?:Total Marks|एकूण गुण|TOTAL)\s*[\|\s]*(\d{3,4})\s+(\d{3,4})',
        text, re.IGNORECASE)
    if match:
        # Validate: obtained <= total
        total = int(match.group(1))
        obtained = int(match.group(2))
        if obtained <= total:
            return str(obtained)

    # "THREE HUNDRED AND SEVENTY FOUR" style — use number in figures column
    # Look for last 3-4 digit number before "THREE HUNDRED" or similar
    match = re.search(
        r'(\d{3,4})\s+(?:THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|ONE|TWO)\s+HUNDRED',
        text, re.IGNORECASE)
    if match:
        return match.group(1)

    # Fraction format: 374/500
    match = re.search(r'\b(\d{3,4})\s*/\s*\d{3,4}\b', text)
    if match:
        return match.group(1)

    # Label
    match = re.search(r'(?:Marks Obtained|प्राप्त गुण)\s*[:\-]?\s*(\d{3,4})', text, re.IGNORECASE)
    return match.group(1) if match else ""

def _extract_total_marks(text):
    # "Total Marks  600  304" — 600 is max
    match = re.search(
        r'(?:Total Marks|एकूण गुण|TOTAL)\s*[\|\s]*(\d{3,4})\s+\d{3,4}',
        text, re.IGNORECASE)
    if match:
        return match.group(1)
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
    # Label-based: "SEAT NO.  C022308" or "Seat No: M064043"
    match = re.search(
        r'(?:Seat\s*No|SEAT\s*NO|Roll\s*No|Roll\s*Number|Reg\s*No|Registration\s*No)\s*[.:\-]?\s*([A-Z]?\d{5,10})',
        text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Standalone alphanumeric seat no: C022308, M064043, S160795911
    # Must start with a letter followed by 6-9 digits
    match = re.search(r'\b([A-Z]\d{6,9})\b', text)
    if match:
        return match.group(1)

    # Pure numeric roll no after label
    match = re.search(
        r'(?:Seat|Roll|Reg)\s*[.:\-]?\s*(\d{6,10})',
        text, re.IGNORECASE)
    return match.group(1) if match else ""


# ── FIX 1: school_name — doc-specific, no table headers ──────────
def _extract_school_name(text, doc_type=None):
    # School leaving cert: school name is in the circular top arc text
    # e.g. "AQSA PUBLIC SCHOOL RAJJAR CHARSADDA"
    # It appears as first or second line before "SCHOOL LEAVING CERTIFICATE"
    if doc_type == 'school_leaving':
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        for line in lines[:5]:
            # Must contain "School" and NOT contain "Leaving" or "Certificate"
            if re.search(r'\bSchool\b', line, re.IGNORECASE):
                if not re.search(r'leaving|certificate|board|examination', line, re.IGNORECASE):
                    clean = re.sub(r'[^A-Za-z\s]', '', line).strip()
                    clean = re.sub(r'\s+', ' ', clean).strip()
                    if len(clean) > 5:
                        return clean.title()
        return ""

    # Marksheet: board name is in the header, not a separate school field
    # For marksheets, school_name = division/centre — skip table header lines
    if doc_type in ('marksheet_10', 'marksheet_12'):
        # Skip any line that looks like a table header
        # Real school-related line would say "Division: MUMBAI"
        match = re.search(r'Division\s*[:\-]?\s*([A-Z][A-Za-z\s]+?)(?:\n|$)', text, re.IGNORECASE)
        if match:
            val = match.group(1).strip()
            if len(val) < 30:  # table headers are long
                return val.title()
        return ""

    # General: first line with School/College keyword, not a table header
    for line in text.split('\n'):
        line = line.strip()
        if re.search(r'\bSchool\b|\bCollege\b|\bInstitute\b', line, re.IGNORECASE):
            if not re.search(r'leaving|certificate|board|examination|seat|centre|dist|month|year|srno|statement|no\.|no\s', line, re.IGNORECASE):
                clean = re.sub(r'[^A-Za-z\s]', '', line).strip()
                clean = re.sub(r'\s+', ' ', clean).strip()
                # Reject if too long (likely a table header row)
                if 5 < len(clean) < 60:
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