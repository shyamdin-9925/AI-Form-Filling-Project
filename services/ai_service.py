from models.nlp_processor import extract_entities
from models.autofill_model import predict_fields


def process_ocr_text(raw_text: str, doc_type: str = None) -> dict:
    """
    Called after OCR — extracts entities doc-specifically.
    Input:  raw OCR text, doc_type (e.g. 'aadhaar_doc', 'marksheet_10')
    Output: dict of extracted entities for that doc type only
    """
    return extract_entities(raw_text, doc_type=doc_type)


def get_autofill_suggestions(merged_data: dict) -> dict:
    """
    Called on form fill page — maps merged extracted data to form field names.
    Input:  merged dict of all extracted entities from all uploaded docs
    Output: dict mapped to exact HTML form field names
    """
    return predict_fields(merged_data)