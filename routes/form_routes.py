import json
from flask import Blueprint, request, render_template, redirect, jsonify, session, url_for
from database.db import db
from database.user_model import User
from database.submission_model import Submission
from services.ai_service import get_autofill_suggestions
from services.form_mapping_service import get_form_fields, get_user_data
from services.validation_service import validate_step1
from services.document_mapping_service import get_required_documents

form_bp = Blueprint('form', __name__)


@form_bp.route('/select')
def select_form():
    """
    Shows all 9 form types as cards for user to choose.
    """
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    forms = [
        {'type': 'scholarship',         'label': 'Scholarship Form'},
        {'type': 'college_admission',   'label': 'College Admission'},
        {'type': 'visa_application',    'label': 'Visa Application'},
        {'type': 'kyc_verification',    'label': 'KYC Verification'},
        {'type': 'passport_application','label': 'Passport Application'},
        {'type': 'driving_licence',     'label': 'Driving Licence'},
        {'type': 'income_tax_return',   'label': 'Income Tax Return'},
        {'type': 'insurance_claim',     'label': 'Insurance Claim'},
        {'type': 'general_purpose',     'label': 'General Purpose'},
    ]
    return render_template('form_select.html', forms=forms)


@form_bp.route('/extracted')
def extracted():
    """
    Shows OCR extraction results per document.
    User reviews what was found before proceeding to form.
    """
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    extracted_results = session.get('extracted_data', {})
    form_type         = session.get('form_type', '')
    return render_template('extracted.html',
        extracted_results = extracted_results,
        form_type         = form_type)


@form_bp.route('/fill/<form_type>')
def fill_form(form_type):
    """
    Renders form with AI pre-filled values.
    Merges database user data with OCR extracted data.
    """
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user          = User.query.get(session['user_id'])
    form_fields   = get_form_fields(form_type)
    required_docs = get_required_documents(form_type)

    # Get user data from database
    user_dict  = get_user_data(user)

    # Get OCR extracted data from session
    extracted  = session.get('extracted_data', {})

    # Merge — OCR data takes priority over database data
    merged_data   = {**user_dict, **extracted}
    autofill_data = get_autofill_suggestions(merged_data)

    return render_template('form_fill.html',
        form_fields   = form_fields,
        autofill_data = autofill_data,
        form_type     = form_type,
        required_docs = required_docs,
        user          = user)


@form_bp.route('/ai/autofill', methods=['POST'])
def autofill():
    """
    JSON endpoint called by frontend autofill.js.
    Returns autofill suggestions for current user.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user       = User.query.get(session['user_id'])
    user_dict  = get_user_data(user)
    extracted  = session.get('extracted_data', {})
    merged     = {**user_dict, **extracted}
    suggestions = get_autofill_suggestions(merged)

    return jsonify({'fields': suggestions})


@form_bp.route('/submit', methods=['POST'])
def submit_form():
    """
    Handles final form submission.
    Validates data and saves to database.
    """
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    form_data = request.form.to_dict()
    form_type = form_data.get('form_type', 'general_purpose')
    errors    = validate_step1(form_data)

    if errors:
        form_fields   = get_form_fields(form_type)
        autofill_data = form_data
        return render_template('form_fill.html',
            form_fields   = form_fields,
            autofill_data = autofill_data,
            form_type     = form_type,
            errors        = errors)

    # Save submission to database
    new_submission = Submission(
        user_id   = session['user_id'],
        form_type = form_type,
        data_json = json.dumps(form_data)
    )
    db.session.add(new_submission)
    db.session.commit()

    # Save form data to session for result page
    session['last_submission'] = form_data

    return render_template('result.html', data=form_data)

