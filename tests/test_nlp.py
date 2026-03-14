import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ocr_service import extract_text
from services.ai_service import process_ocr_text

# Step 1 — Extract text from real Aadhaar card
print("Step 1 - OCR on Aadhaar card:")
raw_text = extract_text("tests/sample1.png")
print(raw_text)

# Step 2 — Extract entities from that text
print("\nStep 2 - Extracted entities:")
entities = process_ocr_text(raw_text)
for key, value in entities.items():
    print(f"  {key}: {value}")
