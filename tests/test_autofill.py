import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.autofill_model import predict_fields

# Simulating data that would come from nlp_processor
sample_data = {
    "name":         "Rahul Sharma",
    "dob":          "15/08/1995",
    "phone":        "9876543210",
    "email":        "rahul@email.com",
    "aadhaar":      "123456789012",
    "pan":          "ABCDE1234F",
    "address":      "123 MG Road, Pune, Maharashtra",
    "account_no":   "9876543210123",
    "ifsc":         "SBIN0001234",
    "bank_name":    "State Bank of India",
    "college_name": "Mumbai University",
    "enrollment_no":"MU2021001234",
    "course_name":  "B.Sc Computer Science",
}

result = predict_fields(sample_data)

print("Autofill output:")
for key, value in result.items():
    print(f"  {key}: {value}")
