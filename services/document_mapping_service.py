def get_required_documents(form_type: str) -> list:
    """
    Returns list of required documents for each form type.
    Frontend uses this to show only relevant upload fields.
    """
    docs = {
        'scholarship': [
            {'name': 'aadhaar_doc',    'label': 'Aadhaar Card',          'accept': '.jpg,.jpeg,.pdf', 'max_kb': 200},
            {'name': 'pan_doc',        'label': 'PAN Card',              'accept': '.jpg,.jpeg,.pdf', 'max_kb': 200},
            {'name': 'marksheet_10',   'label': '10th Marksheet',        'accept': '.jpg,.jpeg,.pdf', 'max_kb': 500},
            {'name': 'marksheet_12',   'label': '12th Marksheet',        'accept': '.jpg,.jpeg,.pdf', 'max_kb': 500},
            {'name': 'caste_cert',     'label': 'Caste Certificate',     'accept': '.pdf',            'max_kb': 300},
            {'name': 'income_cert',    'label': 'Income Certificate',    'accept': '.pdf',            'max_kb': 300},
            {'name': 'bank_passbook',  'label': 'Bank Passbook',         'accept': '.jpg,.jpeg',      'max_kb': 200},
            {'name': 'school_leaving', 'label': 'School Leaving Cert',   'accept': '.pdf',            'max_kb': 300},
        ],
        'college_admission': [
            {'name': 'aadhaar_doc',    'label': 'Aadhaar Card',          'accept': '.jpg,.jpeg,.pdf', 'max_kb': 200},
            {'name': 'marksheet_10',   'label': '10th Marksheet',        'accept': '.jpg,.jpeg,.pdf', 'max_kb': 500},
            {'name': 'marksheet_12',   'label': '12th Marksheet',        'accept': '.jpg,.jpeg,.pdf', 'max_kb': 500},
            {'name': 'school_leaving', 'label': 'School Leaving Cert',   'accept': '.pdf',            'max_kb': 300},
            {'name': 'caste_cert',     'label': 'Caste Certificate',     'accept': '.pdf',            'max_kb': 300},
            {'name': 'photo',          'label': 'Passport Photo',        'accept': '.jpg',            'max_kb': 50},
        ],
        'visa_application': [
            {'name': 'passport_doc',   'label': 'Passport',              'accept': '.jpg,.jpeg,.pdf', 'max_kb': 500},
            {'name': 'aadhaar_doc',    'label': 'Aadhaar Card',          'accept': '.jpg,.jpeg,.pdf', 'max_kb': 200},
            {'name': 'pan_doc',        'label': 'PAN Card',              'accept': '.jpg,.jpeg,.pdf', 'max_kb': 200},
            {'name': 'bank_passbook',  'label': 'Bank Passbook',         'accept': '.jpg,.jpeg',      'max_kb': 200},
            {'name': 'photo',          'label': 'Passport Photo',        'accept': '.jpg',            'max_kb': 50},
        ],
        'kyc_verification': [
            {'name': 'aadhaar_doc',    'label': 'Aadhaar Card',          'accept': '.jpg,.jpeg,.pdf', 'max_kb': 200},
            {'name': 'pan_doc',        'label': 'PAN Card',              'accept': '.jpg,.jpeg,.pdf', 'max_kb': 200},
            {'name': 'bank_passbook',  'label': 'Bank Passbook',         'accept': '.jpg,.jpeg',      'max_kb': 200},
            {'name': 'photo',          'label': 'Passport Photo',        'accept': '.jpg',            'max_kb': 50},
        ],
        'passport_application': [
            {'name': 'aadhaar_doc',    'label': 'Aadhaar Card',          'accept': '.jpg,.jpeg,.pdf', 'max_kb': 200},
            {'name': 'pan_doc',        'label': 'PAN Card',              'accept': '.jpg,.jpeg,.pdf', 'max_kb': 200},
            {'name': 'birth_cert',     'label': 'Birth Certificate',     'accept': '.pdf',            'max_kb': 300},
            {'name': 'marksheet_10',   'label': '10th Marksheet',        'accept': '.jpg,.jpeg,.pdf', 'max_kb': 500},
        ],
        'driving_licence': [
            {'name': 'aadhaar_doc',    'label': 'Aadhaar Card',          'accept': '.jpg,.jpeg,.pdf', 'max_kb': 200},
            {'name': 'birth_cert',     'label': 'Birth Certificate',     'accept': '.pdf',            'max_kb': 300},
            {'name': 'photo',          'label': 'Passport Photo',        'accept': '.jpg',            'max_kb': 50},
        ],
        'income_tax_return': [
            {'name': 'aadhaar_doc',    'label': 'Aadhaar Card',          'accept': '.jpg,.jpeg,.pdf', 'max_kb': 200},
            {'name': 'pan_doc',        'label': 'PAN Card',              'accept': '.jpg,.jpeg,.pdf', 'max_kb': 200},
            {'name': 'bank_passbook',  'label': 'Bank Passbook',         'accept': '.jpg,.jpeg',      'max_kb': 200},
            {'name': 'form16',         'label': 'Form 16',               'accept': '.pdf',            'max_kb': 500},
        ],
        'insurance_claim': [
            {'name': 'aadhaar_doc',    'label': 'Aadhaar Card',          'accept': '.jpg,.jpeg,.pdf', 'max_kb': 200},
            {'name': 'pan_doc',        'label': 'PAN Card',              'accept': '.jpg,.jpeg,.pdf', 'max_kb': 200},
            {'name': 'bank_passbook',  'label': 'Bank Passbook',         'accept': '.jpg,.jpeg',      'max_kb': 200},
            {'name': 'birth_cert',     'label': 'Birth Certificate',     'accept': '.pdf',            'max_kb': 300},
        ],
        'general_purpose': [
            {'name': 'aadhaar_doc',    'label': 'Aadhaar Card',          'accept': '.jpg,.jpeg,.pdf', 'max_kb': 200},
            {'name': 'pan_doc',        'label': 'PAN Card',              'accept': '.jpg,.jpeg,.pdf', 'max_kb': 200},
        ],
    }
    return docs.get(form_type, [])


