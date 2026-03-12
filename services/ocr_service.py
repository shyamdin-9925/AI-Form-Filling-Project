from models.ocr_engine import run_ocr


def extract_text(file_path: str) -> str:
    """
    Calls ML person's OCR function.
    Input:  path to uploaded file (jpg, jpeg, pdf)
    Output: extracted text as plain string
    """
    return run_ocr(file_path)