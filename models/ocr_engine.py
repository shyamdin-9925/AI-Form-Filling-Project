import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import os

# ── Tesseract path for Windows ──────────────────────────────
if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def run_ocr(file_path: str) -> str:
    """
    Main function — backend calls this.
    Input:  file path string (jpg, jpeg or pdf)
    Output: extracted text as plain string
    """
    file_path = file_path.lower()

    if file_path.endswith('.pdf'):
        return _ocr_pdf(file_path)
    elif file_path.endswith(('.jpg', '.jpeg', '.png')):
        return _ocr_image(file_path)
    else:
        return ""


def _ocr_image(path: str) -> str:
    """
    Reads text from an image file (jpg, jpeg, png)
    """
    try:
        img = Image.open(path)
        text = pytesseract.image_to_string(img, lang='eng')
        return text.strip()
    except Exception as e:
        print(f"Image OCR error: {e}")
        return ""


def _ocr_pdf(path: str) -> str:
    """
    Reads text from a PDF file
    """
    try:
        doc = fitz.open(path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()
        return full_text.strip()
    except Exception as e:
        print(f"PDF OCR error: {e}")
        return ""