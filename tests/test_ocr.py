import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.ocr_engine import run_ocr
from services.ocr_service import extract_text

# Test direct ML function
result1 = run_ocr("tests/sample1.png")
print("Testing OCR directly:")
print(result1)

# Test via service layer
result2 = extract_text("tests/sample1.png")
print("\nTesting via service layer:")
print(result2)
