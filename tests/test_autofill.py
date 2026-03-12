import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ocr_service import extract_text
from services.ai_service import process_ocr_text, get_autofill_suggestions
from services.form_mapping_service import get_form_fields

# Step 1 — OCR on Aadhaar card
print("Step 1 - OCR on Aadhaar card:")
raw_text = extract_text("tests/sample.jpg")
print(raw_text)

# Step 2 — Extract entities
print("\nStep 2 - Extracted entities:")
entities = process_ocr_text(raw_text)
for key, value in entities.items():
    print(f"  {key}: {value}")

# Step 3 — Get autofill suggestions
print("\nStep 3 - Autofill suggestions for form:")
suggestions = get_autofill_suggestions(entities)
for key, value in suggestions.items():
    print(f"  {key}: {value}")

# Step 4 — Get form fields
print("\nStep 4 - Scholarship form fields:")
fields = get_form_fields('scholarship')
for field in fields:
    filled_value = suggestions.get(field['name'], '')
    print(f"  {field['label']}: {filled_value}")
