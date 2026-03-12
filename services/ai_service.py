from models.autofill_model import predict_fields
from models.nlp_processor import extract_entities


def get_autofill_suggestions(user_data: dict) -> dict:
    """
    Calls ML autofill model with user data from database.
    Input:  user_data dict from database
    Output: dict of { form_field_name: suggested_value }
    """
    return predict_fields(user_data)


def process_ocr_text(raw_text: str) -> dict:
    """
    Calls ML NLP processor with raw OCR text.
    Input:  raw text string from OCR
    Output: dict of extracted entities
    """
    return extract_entities(raw_text)