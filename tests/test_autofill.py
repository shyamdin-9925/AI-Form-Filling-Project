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
    if value:
        print(f"  {key}: {value}")

# Step 3 — Get autofill suggestions
print("\nStep 3 - Autofill suggestions:")
suggestions = get_autofill_suggestions(entities)
for key, value in suggestions.items():
    if value:
        print(f"  {key}: {value}")

# Step 4 — Test all 9 form types
print("\nStep 4 - Testing all form types:")
form_types = [
    'scholarship', 'college_admission', 'visa_application',
    'kyc_verification', 'passport_application', 'driving_licence',
    'income_tax_return', 'insurance_claim', 'general_purpose'
]
for form_type in form_types:
    fields = get_form_fields(form_type)
    filled = sum(1 for f in fields if suggestions.get(f['name']))
    total  = len(fields)
    print(f"  {form_type}: {filled}/{total} fields filled")
