import os
from flask import Blueprint, request, jsonify, current_app, session
from werkzeug.utils import secure_filename
from services.ocr_service import extract_text
from services.ai_service import process_ocr_text
from services.compression_service import compress_file
from services.document_mapping_service import get_required_documents

upload_bp = Blueprint('upload', __name__)


def allowed_file(filename):
    allowed = {'pdf', 'jpg', 'jpeg', 'png'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


@upload_bp.route('/<form_type>', methods=['GET'])
def upload_page(form_type):
    """
    Shows upload page for selected form type.
    Passes required documents list to frontend.
    """
    from flask import render_template
    required_docs = get_required_documents(form_type)
    return render_template('upload.html',
        form_type     = form_type,
        required_docs = required_docs)


@upload_bp.route('/documents', methods=['POST'])
def upload_documents():
    """
    Handles multiple document uploads at once.
    Runs OCR on each document and combines all extracted data.
    """
    results          = {}
    combined_entities = {}
    compressed_files  = []

    # Loop through every file uploaded
    for field_name in request.files:
        file = request.files[field_name]

        if not file or file.filename == '':
            continue

        if not allowed_file(file.filename):
            results[field_name] = {'error': 'File type not allowed'}
            continue

        # Save file
        filename    = secure_filename(file.filename)
        upload_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        print(f"Saved: {upload_path}")

        # Run OCR on this document
        raw_text = extract_text(upload_path)
        print(f"OCR done for {field_name}: {raw_text[:80]}")

        # Extract structured entities from OCR text
        entities = process_ocr_text(raw_text)
        print(f"Entities for {field_name}: {entities}")

        # Compress the file
        compressed = compress_file(upload_path)
        compressed_files.append(compressed)

        # Store per document result
        results[field_name] = {
            'filename': filename,
            'raw_text': raw_text,
            'entities': entities
        }

        # Merge into combined entities
        # First value found wins — don't overwrite good data
        for key, value in entities.items():
            if value and not combined_entities.get(key):
                combined_entities[key] = value

    # Save to session for form filling later
    session['extracted_data']   = combined_entities
    session['compressed_files'] = compressed_files
    session['form_type']        = request.form.get('form_type', '')

    print(f"Combined entities: {combined_entities}")

    return jsonify({
        'success':           True,
        'results':           results,
        'combined_entities': combined_entities,
        'form_type':         session['form_type']
    })