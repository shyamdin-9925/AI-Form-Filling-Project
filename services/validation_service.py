import re


def validate_step1(data: dict) -> list:
    errors = []

    # Only validate if field exists and is not empty
    if data.get('full_name') == '':
        errors.append('Full name is required')

    if data.get('mobile') and not re.match(r'^[6-9]\d{9}$', data.get('mobile', '')):
        errors.append('Invalid mobile number')

    if data.get('email') and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', data.get('email', '')):
        errors.append('Invalid email address')

    if data.get('aadhaar_number') and not re.match(r'^\d{12}$', data.get('aadhaar_number', '')):
        errors.append('Aadhaar must be 12 digits')

    if data.get('pan_number') and not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', data.get('pan_number', '').upper()):
        errors.append('Invalid PAN number format')

    return errors


def validate_step3(data: dict) -> list:
    errors = []

    if data.get('bank_account') and data.get('bank_account_confirm'):
        if data.get('bank_account') != data.get('bank_account_confirm'):
            errors.append('Account numbers do not match')

    if data.get('ifsc_code') and not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', data.get('ifsc_code', '').upper()):
        errors.append('Invalid IFSC code format')

    if data.get('pincode') and not re.match(r'^\d{6}$', data.get('pincode', '')):
        errors.append('PIN code must be 6 digits')

    return errors