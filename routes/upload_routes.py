import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from services.ocr_service import extract_text
from services.ai_service import process_ocr_text
from services.compression_service import compress_file

upload_bp = Blueprint('upload', __name__)


def allowed_file(filename):
    allowed = {'pdf', 'jpg', 'jpeg', 'png'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


@upload_bp.route('/document', methods=['POST'])
def upload_document():
    # Check if file is in request
    if 'document' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['document']

    # Check if file is selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Check if file type is allowed
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    # Save file to uploads folder
    filename    = secure_filename(file.filename)
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(upload_path)
    print(f"File saved: {upload_path}")

    # Call ML OCR to extract text
    raw_text = extract_text(upload_path)
    print(f"OCR extracted: {raw_text[:100]}")

    # Extract structured entities from OCR text
    entities = process_ocr_text(raw_text)
    print(f"Entities found: {entities}")

    # Compress the uploaded file
    compressed_path = compress_file(upload_path)
    print(f"File compressed: {compressed_path}")

    return jsonify({
        'success':   True,
        'ocr_text':  raw_text,
        'entities':  entities,
        'filename':  filename
    })