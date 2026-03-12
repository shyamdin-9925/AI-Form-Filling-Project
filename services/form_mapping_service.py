def get_form_fields(form_type: str) -> list:
    """
    Returns list of field definitions for a given form type.
    Frontend uses this to build the form dynamically.
    """
    forms = {
        'scholarship': [
            {'name': 'full_name',       'label': 'Full Name',           'type': 'text'},
            {'name': 'dob',             'label': 'Date of Birth',       'type': 'date'},
            {'name': 'mobile',          'label': 'Mobile Number',       'type': 'tel'},
            {'name': 'email',           'label': 'Email Address',       'type': 'email'},
            {'name': 'aadhaar_number',  'label': 'Aadhaar Number',      'type': 'text'},
            {'name': 'pan_number',      'label': 'PAN Number',          'type': 'text'},
            {'name': 'address',         'label': 'Permanent Address',   'type': 'textarea'},
            {'name': 'college_name',    'label': 'College Name',        'type': 'text'},
            {'name': 'enrollment_no',   'label': 'Enrollment Number',   'type': 'text'},
            {'name': 'course_name',     'label': 'Course Name',         'type': 'text'},
            {'name': 'bank_account',    'label': 'Bank Account Number', 'type': 'text'},
            {'name': 'ifsc_code',       'label': 'IFSC Code',           'type': 'text'},
            {'name': 'bank_name',       'label': 'Bank Name',           'type': 'text'},
        ]
    }
    return forms.get(form_type, [])


def get_user_data(user) -> dict:
    """
    Converts a User database object to a plain dict
    that the ML autofill model can process.
    """
    return {
        'name':    user.name,
        'dob':     user.dob     or '',
        'phone':   user.phone   or '',
        'email':   user.email   or '',
        'address': user.address or '',
    }