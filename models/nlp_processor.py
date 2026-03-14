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
        'name':            _extract_name,
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
        'school_name':     _extract_school_name,
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


# ── Extractors ────────────────────────────────────────────────────

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

def _extract_name(text):
    BAD_WORDS = {'date', 'dob', 'of', 'birth', 'father', 'mother', 'gender',
                 'male', 'female', 'card', 'aadhaar', 'india', 'government',
                 'address', 'phone', 'mobile', 'unique', 'authority', 'name',
                 'delhi', 'mumbai', 'pune', 'bangalore', 'hyderabad', 'chennai',
                 'kolkata', 'new', 'bagh', 'nagar', 'road', 'street', 'block',
                 'sector', 'district', 'state', 'village', 'post', 'pin',
                 'pass', 'fail', 'result', 'board', 'exam', 'certificate',
                 'division', 'mumbai', 'arts', 'science', 'commerce'}

    # Marksheet format: "CANDIDATE'S FULL NAME (SURNAME FIRST)" on one line
    # then name on NEXT line e.g. "SHAIKH RAHIL AHMED SHABBIR AHMED"
    match = re.search(
        r"CANDIDATE['\u2019S]*S?\s+FULL\s+NAME[^\n]*\n\s*([A-Z][A-Za-z]+(?:\s[A-Z][A-Za-z]+){1,5})",
        text, re.IGNORECASE)
    if match:
        return match.group(1).strip().title()

    # Also: "CANDIDATE'S FULL NAME ... Mudashinge Vaishnavee Sanjay" on same/next line
    match = re.search(
        r"CANDIDATE['\u2019S]*S?\s+FULL\s+NAME[^\n]*\n?\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,4})",
        text)
    if match:
        return match.group(1).strip()

    # Standard label: "Name: Alka" or "Name Alka"
    match = re.search(r'(?:^|\n)\s*(?:Name|NAME|नाम)\s*[:\-]?\s*([A-Za-z][a-z]+(?:\s[A-Za-z][a-z]+){0,3})', text, re.MULTILINE)
    if match:
        words = match.group(1).strip().split()
        clean = [w for w in words if w.lower() not in BAD_WORDS]
        if clean:
            return " ".join(clean[:4]).title()

    # Name on next line after Name: label (Aadhaar OCR noise case)
    match = re.search(r'(?:Name|NAME|नाम)\s*[:\-]?\s*\n[^\w\n]*([A-Za-z][a-z]+(?:\s[A-Za-z][a-z]+){0,3})', text)
    if match:
        words = match.group(1).strip().split()
        clean = [w for w in words if w.lower() not in BAD_WORDS]
        if clean:
            return " ".join(clean[:4]).title()

    # Fallback: short line with 1-3 proper capitalized name words
    for line in text.split('\n'):
        words = re.findall(r'\b[A-Za-z]{3,}\b', line)
        if 1 <= len(words) <= 3:
            clean = [w for w in words if w.lower() not in BAD_WORDS]
            if len(clean) >= 1 and len(clean) == len(words):
                if all(w[0].isupper() for w in clean):
                    return ' '.join(clean).title()
    return ""

def _extract_address(text):
    pattern = r'(?:Address|ADDRESS|पता)\s*[:\-]?\s*([\s\S]+?)(?:\n\s*\n|\Z)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        lines = [l.strip() for l in match.group(1).split('\n') if l.strip()]
        result_lines = []
        for line in lines[:6]:
            # Strip non-ASCII noise characters
            clean_line = re.sub(r'[^A-Za-z0-9,\s\-\/]', '', line).strip()
            clean_line = re.sub(r'\s+', ' ', clean_line).strip()
            # Only keep lines with real content (3+ char words or digits)
            real_words = re.findall(r'\b[A-Za-z]{3,}\b', clean_line)
            digits     = re.findall(r'\b\d{3,}\b', clean_line)
            if real_words or digits:
                result_lines.append(clean_line)
            if re.search(r'\b\d{6}\b', line):
                break
        if result_lines:
            return ', '.join(result_lines)
    # Fallback — text near pincode
    pin_match = re.search(r'(.{30,150}?\b\d{6}\b)', text, re.DOTALL)
    if pin_match:
        addr = re.sub(r'[^A-Za-z0-9,\s\-\/]', ' ', pin_match.group(1))
        return re.sub(r'\s+', ' ', addr).strip()
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
    # OBC is in the caste cert body text e.g. "Other Backward Class"
    t = text.upper()
    if re.search(r'\bOTHER BACKWARD CLASS\b|\bOBC\b', t):
        return "OBC"
    if re.search(r'\bSCHEDULED CASTE\b|\b\bSC\b', t):
        return "SC"
    if re.search(r'\bSCHEDULED TRIBE\b|\bST\b', t):
        return "ST"
    if re.search(r'\bNOMADIC TRIBE\b|\bNT\b', t):
        return "NT"
    if re.search(r'\bSPECIAL BACKWARD\b|\bSBC\b', t):
        return "SBC"
    if re.search(r'\bGENERAL\b|\bOPEN\b', t):
        return "General"
    return ""

def _extract_caste(text):
    # Real caste cert format: "belongs to the MALI Caste" or "Caste: Mali"
    # Try "belongs to the X Caste" pattern first
    match = re.search(r'belongs\s+to\s+the\s+([A-Z][A-Za-z]+)\s+Caste', text, re.IGNORECASE)
    if match:
        return match.group(1).strip().title()
    # Try "Caste: X" label
    match = re.search(r'(?:^|\s)Caste\s*[:\-]\s*([A-Za-z]+)', text, re.IGNORECASE | re.MULTILINE)
    if match:
        return match.group(1).strip().title()
    return ""

def _extract_percentage(text):
    # Real marksheet format: "Percentage/टक्केवारी   50.67" or "74.80"
    # Try with Percentage label
    match = re.search(r'(?:Percentage|टक्केवारी|PERCENTAGE)\s*[/\s]*(?:टक्केवारी)?\s*[:\-]?\s*(\d{2,3}\.?\d{0,2})', text, re.IGNORECASE)
    if match:
        val = match.group(1)
        if 30 <= float(val) <= 100:
            return val + '%'
    # Fallback: any percentage number
    matches = re.findall(r'\b(\d{2,3}\.\d{1,2})\b', text)
    for m in matches:
        if 30.0 <= float(m) <= 100.0:
            return m + '%'
    match = re.search(r'\b(\d{2,3})\s*%', text)
    if match and 30 <= int(match.group(1)) <= 100:
        return match.group(1) + '%'
    return ""

def _extract_marks_obtained(text):
    # Real marksheet: "Total Marks  600  304" or "500  374"
    # Look for "Total Marks" followed by max then obtained
    match = re.search(r'(?:Total Marks|एकूण गुण)\s*[\|]?\s*(\d{3,4})\s+(\d{3,4})', text, re.IGNORECASE)
    if match:
        return match.group(2)  # second number is marks obtained
    # Fraction format 374/500
    match = re.search(r'\b(\d{3,4})\s*/\s*\d{3,4}\b', text)
    if match:
        return match.group(1)
    # Label based
    match = re.search(r'(?:Marks Obtained|Marks Scored|प्राप्त गुण)\s*[:\-]?\s*(\d{3,4})', text, re.IGNORECASE)
    if match:
        return match.group(1)
    return ""

def _extract_total_marks(text):
    # Real marksheet: "Total Marks  600  304" — 600 is total
    match = re.search(r'(?:Total Marks|एकूण गुण)\s*[\|]?\s*(\d{3,4})\s+\d{3,4}', text, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r'\b\d{3,4}\s*/\s*(\d{3,4})\b', text)
    return match.group(1) if match else ""

def _extract_subjects(text):
    subjects = []
    # Extended list matching real marksheets
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

def _extract_roll_no(text):
    # Real marksheet: "SEAT NO.  C022308" or "M064043"
    match = re.search(r'(?:Seat No|SEAT NO|Roll No|Roll Number|Reg No|Reg\. No|Registration)\s*[.:\-]?\s*([A-Z]?\d{5,10})', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Standalone seat number pattern like C022308 or M064043
    match = re.search(r'\b([A-Z]\d{6,8})\b', text)
    if match:
        return match.group(1)
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
    # Real marksheets: "MARCH-2016" or "FEBRUARY-2002"
    match = re.search(r'(?:MARCH|FEBRUARY|OCTOBER|NOVEMBER|APRIL|MAY|JUNE|JULY)\s*[-–]\s*(20\d{2}|19\d{2})', text, re.IGNORECASE)
    if match:
        return match.group(1)
    # "Year of Passing: 2019"
    match = re.search(r'(?:Year of Passing|Passing Year|year)\s*[:\-]?\s*(20\d{2}|19\d{2})', text, re.IGNORECASE)
    if match:
        return match.group(1)
    # School leaving: "from 2016 to 2019" — take last year
    matches = re.findall(r'\b(20\d{2}|19\d{2})\b', text)
    return matches[-1] if matches else ""

def _extract_income(text):
    match = re.search(r'(?:Rs\.?|INR|/-|₹)\s*([\d,]+)', text, re.IGNORECASE)
    return match.group(1).replace(',', '') if match else ""

def _extract_birth_place(text):
    match = re.search(r'(?:Place of Birth|Birth Place|Born at)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|,|$)', text, re.IGNORECASE)
    return match.group(1).strip().title() if match else ""

def _extract_school_name(text):
    # School leaving cert: school name is usually at top or after "Certified that X son of Y of"
    # Try top line — first line with School/Public/High in it
    for line in text.split('\n'):
        line = line.strip()
        if re.search(r'\bSchool\b|\bCollege\b|\bInstitute\b', line, re.IGNORECASE):
            # Skip generic lines
            if not re.search(r'leaving|certificate|board|examination', line, re.IGNORECASE):
                clean = re.sub(r'[^A-Za-z\s]', '', line).strip()
                if len(clean) > 5:
                    return clean.title()
    match = re.search(r'(?:School|Institution|College)\s*[:\-]\s*([A-Za-z\s]+?)(?:\n|$)', text, re.IGNORECASE)
    return match.group(1).strip().title() if match else ""

def _extract_father_name(text):
    # Real formats: "son of Raza Khan" or "S/O Raza Khan" or "Father: X"
    match = re.search(r'(?:son of|daughter of|S/O|D/O|Father[\'s]*\s*Name|Father)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\s{2,}|\n|,|$)', text, re.IGNORECASE)
    if match:
        name = re.sub(r'[^A-Za-z\s]', '', match.group(1)).strip()
        if len(name) > 2:
            return name.title()
    return ""

def _extract_mother_name(text):
    match = re.search(r'(?:Mother[\'s]*\s*Name|Mother|D/O|daughter of)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\s{2,}|\n|,|$)', text, re.IGNORECASE)
    if match:
        name = re.sub(r'[^A-Za-z\s]', '', match.group(1)).strip()
        if len(name) > 2:
            return name.title()
    return ""

def _extract_employer_name(text):
    match = re.search(r'(?:Employer|Company|Organization|Firm)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|$)', text, re.IGNORECASE)
    return match.group(1).strip().title() if match else ""