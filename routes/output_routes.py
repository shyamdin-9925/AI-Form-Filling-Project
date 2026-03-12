import os
import json
from flask import Blueprint, request, jsonify, send_file, session, current_app
from services.pdf_service import generate_form_pdf
from services.zip_service import create_zip
from services.web_autofill_service import autofill_website
from services.ai_service import get_autofill_suggestions
from services.form_mapping_service import get_form_fields

output_bp = Blueprint('output', __name__)


@output_bp.route('/download/pdf', methods=['POST'])
def download_pdf():
    """
    Generates and downloads filled form as PDF.
    Called from result.html download button.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    # Get form data from request or session
    form_data = request.json
    if not form_data:
        form_data = session.get('last_submission', {})

    form_type   = form_data.get('form_type', 'general_purpose')
    output_path = os.path.join(
        current_app.config['OUTPUT_FOLDER'],
        f"{form_type}_filled.pdf"
    )

    # Generate the PDF
    generate_form_pdf(form_type, form_data, output_path)

    return send_file(
        output_path,
        as_attachment = True,
        download_name = f"{form_type}_filled_form.pdf"
    )


@output_bp.route('/download/zip', methods=['GET'])
def download_zip():
    """
    Bundles all compressed documents into ZIP and downloads.
    Called from result.html download button.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    compressed_files = session.get('compressed_files', [])

    if not compressed_files:
        return jsonify({'error': 'No documents found. Please upload documents first.'}), 400

    output_path = os.path.join(
        current_app.config['OUTPUT_FOLDER'],
        'compressed_documents.zip'
    )

    # Create the ZIP
    create_zip(compressed_files, output_path)

    return send_file(
        output_path,
        as_attachment = True,
        download_name = 'compressed_documents.zip'
    )


@output_bp.route('/web-autofill', methods=['POST'])
def web_autofill():
    """
    Opens URL in Chrome and autofills form fields using Selenium.
    Only used for scholarship form demo.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data      = request.json
    url       = data.get('url')
    form_data = data.get('form_data', {})

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    # Map form data keys to HTML field IDs on scholarship site
    field_mapping = {
        'full_name':       form_data.get('full_name',      ''),
        'dob':             form_data.get('dob',            ''),
        'mobile':          form_data.get('mobile',         ''),
        'email':           form_data.get('email',          ''),
        'aadhaar_number':  form_data.get('aadhaar_number', ''),
        'pan_number':      form_data.get('pan_number',     ''),
        'address':         form_data.get('address',        ''),
        'college_name':    form_data.get('college_name',   ''),
        'course_name':     form_data.get('course_name',    ''),
        'bank_account':    form_data.get('bank_account',   ''),
        'ifsc_code':       form_data.get('ifsc_code',      ''),
        'bank_name':       form_data.get('bank_name',      ''),
        'annual_income':   form_data.get('annual_income',  ''),
        'category':        form_data.get('category',       ''),
    }

    # Remove empty fields
    field_mapping = {k: v for k, v in field_mapping.items() if v}

    print(f"Starting web autofill for: {url}")
    print(f"Fields to fill: {list(field_mapping.keys())}")

    result = autofill_website(url, field_mapping)
    return jsonify(result)