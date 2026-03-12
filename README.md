# FormAssist — AI Based Assisted Digital Form Automation System

FormAssist is an AI-powered web application that helps users automatically fill 
online forms by extracting information from uploaded documents like Aadhaar cards 
and PAN cards using OCR.

---

## Project Structure
```
AI-Form-Filling-Project/
├── models/
│   ├── ocr_engine.py        # Extracts text from images and PDFs
│   ├── nlp_processor.py     # Extracts structured info using regex
│   ├── autofill_model.py    # Maps extracted data to form fields
│   └── saved_models/
├── templates/               # HTML pages (Frontend)
├── static/                  # CSS, JS, images (Frontend)
├── routes/                  # Flask routes (Backend)
├── services/                # Business logic (Backend)
├── database/                # Database models (Backend)
├── tests/                   # Test files
├── uploads/                 # Uploaded documents (not committed)
├── outputs/                 # Processed output files (not committed)
├── app.py                   # Main Flask entry point
└── requirements.txt         # Python dependencies
```

---

## Team

| Role | Responsibility |
|------|---------------|
| Frontend | HTML, CSS, JavaScript, Flask templates |
| Backend | Python, Flask, Database, API routes |
| ML | OCR, NLP, Autofill models |

---

## Requirements

### 1. Python
This project requires **Python 3.11**.
Download from: https://www.python.org/downloads/release/python-3119/

> ⚠️ Python 3.14 is NOT supported due to spaCy compatibility issues.
> Use Python 3.11.

### 2. Tesseract OCR
Tesseract is required for the OCR engine. Install it separately:

- **Windows:** Download installer from https://github.com/UB-Mannheim/tesseract/wiki
  - Install with default settings
  - Default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
- **Mac:** 
```
  brew install tesseract
```
- **Linux / Docker:**
```
  sudo apt-get install tesseract-ocr
```

Verify installation:
```
tesseract --version
```

### 3. Python Libraries
All Python dependencies are listed in `requirements.txt`.

---

## Setup Instructions

### Step 1 — Clone the repository
```
git clone https://github.com/shyamdin-9925/AI-Form-Filling-Project.git
cd AI-Form-Filling-Project
```

### Step 2 — Create virtual environment
```
python -m venv venv
```

Activate it:
- **Windows:**
```
  venv\Scripts\activate
```
- **Mac/Linux:**
```
  source venv/bin/activate
```

### Step 3 — Install Python libraries
```
pip install -r requirements.txt
```

### Step 4 — Run the app
```
python app.py
```

Open browser at: http://localhost:5000

---

## ML Module

The ML module consists of 3 files in the `models/` folder:

### ocr_engine.py
Extracts raw text from uploaded documents.
```python
from models.ocr_engine import run_ocr
text = run_ocr("path/to/document.jpg")
```

### nlp_processor.py
Extracts structured information from raw OCR text.
```python
from models.nlp_processor import extract_entities
data = extract_entities(raw_text)
# Returns: { name, dob, aadhaar, pan, phone, address, account_no, ifsc }
```

### autofill_model.py
Maps extracted data to scholarship form field names.
```python
from models.autofill_model import predict_fields
fields = predict_fields(user_data)
# Returns: { full_name, dob, aadhaar_number, pan_number, ... }
```

---

## Running Tests
```
python tests/test_ocr.py
python tests/test_nlp.py
python tests/test_autofill.py
```

---

## Git Workflow

| Branch | Owner | Purpose |
|--------|-------|---------|
| main | All | Final working code only |
| feature/frontend | Frontend dev | HTML, CSS, JS files |
| feature/backend | Backend dev | Flask, database, routes |
| feature/ml | ML dev | OCR, NLP, autofill models |

Always work on your own branch and raise a Pull Request to merge into main.

---

## Important Notes

- Never commit the `venv/` folder
- Never commit the `.env` file
- Never commit files inside `uploads/` or `outputs/`
- Always run `pip freeze > requirements.txt` after installing new packages
- Always activate venv before working: `venv\Scripts\activate`

---


> This project is developed as a college project by students
