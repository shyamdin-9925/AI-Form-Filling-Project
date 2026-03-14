import pytesseract
from PIL import Image, ImageFilter, ImageEnhance
import fitz  # PyMuPDF
import os

# ── Tesseract path for Windows ──────────────────────────────
if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Tesseract config — psm 6 = assume uniform block of text
TESS_CONFIG = '--oem 3 --psm 6'


def run_ocr(file_path: str) -> str:
    """
    Main function — backend calls this.
    Input:  file path string (jpg, jpeg, png or pdf)
    Output: extracted text as plain string
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.pdf':
        return _ocr_pdf(file_path)
    elif ext in ('.jpg', '.jpeg', '.png'):
        return _ocr_image(file_path)
    else:
        return ""


def _preprocess(img: Image.Image) -> Image.Image:
    """
    Improves OCR accuracy by preprocessing the image:
    - Convert to RGB if needed
    - Resize if too small
    - Sharpen
    - Increase contrast
    """
    # Convert to RGB
    if img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')

    # Upscale if image is small — Tesseract works better on larger images
    w, h = img.size
    if w < 1000:
        scale = 1000 / w
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    # Convert to greyscale for OCR
    img = img.convert('L')

    # Sharpen
    img = img.filter(ImageFilter.SHARPEN)

    # Increase contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)

    return img


def _ocr_image(path: str) -> str:
    """
    Reads text from an image file (jpg, jpeg, png)
    with preprocessing for better accuracy
    """
    try:
        img = Image.open(path)
        img = _preprocess(img)
        # Try English + Hindi for Aadhaar cards
        try:
            text = pytesseract.image_to_string(img, lang='eng+hin', config=TESS_CONFIG)
        except Exception:
            text = pytesseract.image_to_string(img, lang='eng', config=TESS_CONFIG)
        return text.strip()
    except Exception as e:
        print(f"Image OCR error: {e}")
        return ""


def _ocr_pdf(path: str) -> str:
    """
    Reads text from a PDF file.
    First tries direct text extraction (for digital PDFs),
    then falls back to OCR (for scanned PDFs).
    """
    try:
        doc = fitz.open(path)
        full_text = ""
        for page in doc:
            # Try direct text extraction first
            page_text = page.get_text()
            if page_text.strip():
                full_text += page_text
            else:
                # Scanned PDF — render page as image and OCR it
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                pix = page.get_pixmap(matrix=mat)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img = _preprocess(img)
                page_text = pytesseract.image_to_string(img, lang='eng', config=TESS_CONFIG)
                full_text += page_text
        doc.close()
        return full_text.strip()
    except Exception as e:
        print(f"PDF OCR error: {e}")
        return ""