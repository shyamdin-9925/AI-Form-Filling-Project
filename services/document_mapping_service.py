def get_required_documents(form_type: str) -> list:
    """
    Returns list of required documents for each form type.
    Frontend uses this to show only relevant upload fields.
    """
    ALL = '.png,.jpg,.jpeg,.pdf'
    IMG = '.png,.jpg,.jpeg'

    docs = {
        'scholarship': [
            {'name': 'aadhaar_doc',    'label': 'Aadhaar Card',          'accept': ALL, 'max_kb': 10240},
            {'name': 'pan_doc',        'label': 'PAN Card',              'accept': ALL, 'max_kb': 10240},
            {'name': 'marksheet_10',   'label': '10th Marksheet',        'accept': ALL, 'max_kb': 10240},
            {'name': 'marksheet_12',   'label': '12th Marksheet',        'accept': ALL, 'max_kb': 10240},
            {'name': 'caste_cert',     'label': 'Caste Certificate',     'accept': ALL, 'max_kb': 10240},
            {'name': 'income_cert',    'label': 'Income Certificate',    'accept': ALL, 'max_kb': 10240},
            {'name': 'bank_passbook',  'label': 'Bank Passbook',         'accept': ALL, 'max_kb': 10240},
            {'name': 'school_leaving', 'label': 'School Leaving Cert',   'accept': ALL, 'max_kb': 10240},
        ],
        'college_admission': [
            {'name': 'aadhaar_doc',    'label': 'Aadhaar Card',          'accept': ALL, 'max_kb': 10240},
            {'name': 'marksheet_10',   'label': '10th Marksheet',        'accept': ALL, 'max_kb': 10240},
            {'name': 'marksheet_12',   'label': '12th Marksheet',        'accept': ALL, 'max_kb': 10240},
            {'name': 'school_leaving', 'label': 'School Leaving Cert',   'accept': ALL, 'max_kb': 10240},
            {'name': 'caste_cert',     'label': 'Caste Certificate',     'accept': ALL, 'max_kb': 10240},
            {'name': 'photo',          'label': 'Passport Photo',        'accept': IMG, 'max_kb': 10240},
        ],
        'visa_application': [
            {'name': 'passport_doc',   'label': 'Passport',              'accept': ALL, 'max_kb': 10240},
            {'name': 'aadhaar_doc',    'label': 'Aadhaar Card',          'accept': ALL, 'max_kb': 10240},
            {'name': 'pan_doc',        'label': 'PAN Card',              'accept': ALL, 'max_kb': 10240},
            {'name': 'bank_passbook',  'label': 'Bank Passbook',         'accept': ALL, 'max_kb': 10240},
            {'name': 'photo',          'label': 'Passport Photo',        'accept': IMG, 'max_kb': 10240},
        ],
        'kyc_verification': [
            {'name': 'aadhaar_doc',    'label': 'Aadhaar Card',          'accept': ALL, 'max_kb': 10240},
            {'name': 'pan_doc',        'label': 'PAN Card',              'accept': ALL, 'max_kb': 10240},
            {'name': 'bank_passbook',  'label': 'Bank Passbook',         'accept': ALL, 'max_kb': 10240},
            {'name': 'photo',          'label': 'Passport Photo',        'accept': IMG, 'max_kb': 10240},
        ],
        'passport_application': [
            {'name': 'aadhaar_doc',    'label': 'Aadhaar Card',          'accept': ALL, 'max_kb': 10240},
            {'name': 'pan_doc',        'label': 'PAN Card',              'accept': ALL, 'max_kb': 10240},
            {'name': 'birth_cert',     'label': 'Birth Certificate',     'accept': ALL, 'max_kb': 10240},
            {'name': 'marksheet_10',   'label': '10th Marksheet',        'accept': ALL, 'max_kb': 10240},
        ],
        'driving_licence': [
            {'name': 'aadhaar_doc',    'label': 'Aadhaar Card',          'accept': ALL, 'max_kb': 10240},
            {'name': 'birth_cert',     'label': 'Birth Certificate',     'accept': ALL, 'max_kb': 10240},
            {'name': 'photo',          'label': 'Passport Photo',        'accept': IMG, 'max_kb': 10240},
        ],
        'income_tax_return': [
            {'name': 'aadhaar_doc',    'label': 'Aadhaar Card',          'accept': ALL, 'max_kb': 10240},
            {'name': 'pan_doc',        'label': 'PAN Card',              'accept': ALL, 'max_kb': 10240},
            {'name': 'bank_passbook',  'label': 'Bank Passbook',         'accept': ALL, 'max_kb': 10240},
            {'name': 'form16',         'label': 'Form 16',               'accept': ALL, 'max_kb': 10240},
        ],
        'insurance_claim': [
            {'name': 'aadhaar_doc',    'label': 'Aadhaar Card',          'accept': ALL, 'max_kb': 10240},
            {'name': 'pan_doc',        'label': 'PAN Card',              'accept': ALL, 'max_kb': 10240},
            {'name': 'bank_passbook',  'label': 'Bank Passbook',         'accept': ALL, 'max_kb': 10240},
            {'name': 'birth_cert',     'label': 'Birth Certificate',     'accept': ALL, 'max_kb': 10240},
        ],
        'general_purpose': [
            {'name': 'aadhaar_doc',    'label': 'Aadhaar Card',          'accept': ALL, 'max_kb': 10240},
            {'name': 'pan_doc',        'label': 'PAN Card',              'accept': ALL, 'max_kb': 10240},
        ],
    }
    return docs.get(form_type, [])