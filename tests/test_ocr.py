import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.ocr_engine import run_ocr

result = run_ocr("tests/sample.jpg")
print("Extracted text:")
print(result)
