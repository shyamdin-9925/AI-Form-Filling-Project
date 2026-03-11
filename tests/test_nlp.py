import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.nlp_processor import extract_entities

# Sample text simulating what OCR would extract from an Aadhaar card
sample_aadhaar_text = """
Government of India
Name: Rahul Sharma
Date of Birth: 15/08/1995
Male
Address: 123 MG Road, Pune, Maharashtra 411001
1234 5678 9012
"""

# Sample text simulating a PAN card
sample_pan_text = """
Income Tax Department
Permanent Account Number Card
Name: RAHUL SHARMA
Father's Name: SURESH SHARMA
Date of Birth: 15/08/1995
ABCDE1234F
"""

print("Testing Aadhaar text:")
result1 = extract_entities(sample_aadhaar_text)
for key, value in result1.items():
    print(f"  {key}: {value}")

print("\nTesting PAN text:")
result2 = extract_entities(sample_pan_text)
for key, value in result2.items():
    print(f"  {key}: {value}")

