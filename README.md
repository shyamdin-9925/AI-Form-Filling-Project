# FormAssist — AI Based Assisted Digital Form Automation System

FormAssist is an AI-powered web application that helps users automatically fill online forms by extracting information from uploaded documents (Aadhaar, PAN, marksheets, passbook, etc.) using OCR and NLP, then auto-filling form fields with the extracted data.

---

## Features

- **OCR Document Scanning** — Extracts text from JPG, PNG, and PDF documents using Tesseract
- **AI Entity Extraction** — Identifies name, DOB, Aadhaar, PAN, address, bank details, marks, and more
- **9 Form Types Supported** — Scholarship, College Admission, Visa, KYC, Passport, Driving Licence, ITR, Insurance Claim, General Purpose
- **Multiple Document Upload** — Upload Aadhaar + PAN + marksheet + passbook together in one go
- **AI Autofill** — Merges OCR data from all uploaded documents and pre-fills form fields
- **Download Filled Form PDF** — Generates a PDF of the completed form for reference or printing
- **Download Compressed Documents ZIP** — Compresses uploaded documents to meet government portal size limits
- **Selenium Web Autofill** — For scholarship forms, auto-fills a real website using Chrome (demo portal)
- **User Authentication** — Signup, login, logout with password hashing
- **Dashboard** — View all past form submissions with status and metadata
- **Validation** — Only validates fields that are present and filled in the form

---

## Project Structure

```
AI-Form-Filling-Project/
├── models/
│   ├── ocr_engine.py            # Tesseract OCR — extracts text from images and PDFs
│   ├── nlp_processor.py         # Regex NLP — extracts structured entities from OCR text
│   ├── autofill_model.py        # Maps extracted entities to all 9 form field sets
│   └── saved_models/
├── services/
│   ├── ocr_service.py           # OCR service wrapper
│   ├── ai_service.py            # AI autofill suggestions service
│   ├── form_mapping_service.py  # Form field definitions for all 9 form types
│   ├── document_mapping_service.py  # Required documents per form type
│   ├── pdf_service.py           # Generates filled form PDFs using ReportLab
│   ├── zip_service.py           # Creates ZIP of compressed uploaded documents
│   ├── web_autofill_service.py  # Selenium browser autofill for scholarship portal
│   ├── validation_service.py    # Form field validation
│   └── compression_service.py  # Compresses uploaded documents
├── routes/
│   └── output_routes.py         # Output download routes (PDF, ZIP, web autofill)
├── database/
│   ├── db.py                    # SQLAlchemy setup
│   ├── user_model.py            # User table
│   ├── form_model.py            # Form table
│   └── submission_model.py      # Submission table
├── templates/                   # Jinja2 HTML templates (Frontend)
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── form_select.html
│   ├── upload.html
│   ├── extracted.html
│   ├── form_fill.html
│   ├── review.html
│   └── result.html
├── static/                      # CSS, JS, images (Frontend)
│   ├── css/
│   └── js/
├── tests/
│   ├── test_ocr.py
│   ├── test_nlp.py
│   ├── test_autofill.py
│   └── sample.jpg               # Sample Aadhaar card for testing
├── uploads/                     # Uploaded documents at runtime (not committed)
├── outputs/                     # Generated PDFs and ZIPs at runtime (not committed)
├── app.py                       # Main Flask application entry point
├── config.py                    # Flask configuration
├── .env                         # Environment variables (not committed)
├── requirements.txt             # Python dependencies
└── .gitignore
```

---

## Team

| Role | Name | Responsibility |
|------|------|---------------|
| Frontend | Person 1 | HTML, CSS, JavaScript, Jinja2 templates (11 pages) |
| Backend Core | Person 2 | Flask app, SQLite database, auth, validation, compression |
| Backend AI Integration | Person 3 | Form routes, upload routes, ML bridges, output routes |
| ML | Person 4 | OCR engine, NLP processor, autofill model, tests |

---

## Supported Form Types

| Form Type | Description |
|-----------|-------------|
| Scholarship | University/college scholarship applications |
| College Admission | Admission forms with marksheet extraction |
| Visa Application | Tourist, student, and work visa forms |
| KYC Verification | Bank KYC with Aadhaar and PAN |
| Passport Application | Fresh and renewal passport applications |
| Driving Licence | DL application and renewal |
| Income Tax Return | ITR filing with Form 16 pre-fill |
| Insurance Claim | Health, vehicle, and general insurance claims |
| General Purpose | Custom form for any use |

---

## Requirements

### 1. Python
This project requires **Python 3.11 or higher** (developed and tested on Python 3.14).
Download from: https://www.python.org/downloads/

> ℹ️ This project uses **regex-based NLP** instead of spaCy, so it is fully compatible with Python 3.14 and above. No spaCy installation is required.

### 2. Tesseract OCR
Tesseract must be installed separately before running the app.

- **Windows:** Download installer from https://github.com/UB-Mannheim/tesseract/wiki
  - Install to default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
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

### 3. Google Chrome
Required for Selenium web autofill feature. ChromeDriver is managed automatically via `webdriver-manager`.

### 4. Python Libraries
All dependencies are in `requirements.txt`:
```
flask, flask-sqlalchemy, werkzeug, python-dotenv
pytesseract, Pillow, PyMuPDF
python-dateutil, reportlab
selenium, webdriver-manager
```

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
- **Windows (PowerShell):**
  ```
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
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

### Step 4 — Create .env file
Create a `.env` file in the project root:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///formassist.db
UPLOAD_FOLDER=uploads/
OUTPUT_FOLDER=outputs/
```

### Step 5 — Run the app
```
python app.py
```

Open browser at: **http://localhost:5000**

The SQLite database (`formassist.db`) is created automatically on first run.

---

## User Flow

```
1. Sign up / Log in
       ↓
2. Select a form type (9 available)
       ↓
3. Upload documents (Aadhaar, PAN, marksheet, passbook, etc.)
       ↓
4. OCR extracts text → NLP extracts entities → shown on Extracted Data page
       ↓
5. Form Fill page — all fields pre-filled by AI from extracted data
       ↓
6. Review and Submit
       ↓
7. Result page — three outputs available:
   ├── 📄 Download filled form as PDF
   ├── 📦 Download compressed documents as ZIP
   └── 🌐 Selenium web autofill (Scholarship form only)
```

---

## ML Module

### ocr_engine.py
Extracts raw text from uploaded images and PDFs using Tesseract.
```python
from models.ocr_engine import run_ocr
text = run_ocr("path/to/document.jpg")
```

### nlp_processor.py
Extracts structured entities from raw OCR text using regex patterns.
```python
from models.nlp_processor import extract_entities
data = extract_entities(raw_text)
# Returns: { name, dob, aadhaar, pan, phone, email, address,
#            account_no, ifsc, marks_10, marks_12, percentage, ... }
```

### autofill_model.py
Maps extracted entities to form fields for all 9 form types.
```python
from models.autofill_model import predict_fields
fields = predict_fields(user_data, form_type="scholarship")
# Returns: { full_name, dob, aadhaar_number, pan_number, ... }
```

---

## Running Tests
```
python tests/test_ocr.py
python tests/test_nlp.py
python tests/test_autofill.py
```

Tests run against `tests/sample.jpg` (a real Aadhaar card image).

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home / landing page |
| GET | `/login` | Login page |
| GET | `/signup` | Signup page |
| POST | `/auth/login` | Process login |
| POST | `/auth/signup` | Process signup |
| GET | `/logout` | Logout |
| GET | `/dashboard` | User dashboard |
| GET | `/form/select` | Choose form type |
| GET | `/form/upload/<form_type>` | Upload documents page |
| POST | `/upload/documents` | Process uploaded documents |
| GET | `/form/extracted` | View extracted OCR data |
| GET | `/form/fill/<form_type>` | Form fill page with autofill |
| POST | `/form/submit` | Submit filled form |
| GET/POST | `/form/review` | Review submission |
| GET | `/result` | Result and download page |
| POST | `/form/ai/autofill` | AJAX — get AI autofill suggestions |
| GET | `/download/zip` | Download compressed documents ZIP |
| POST | `/download/pdf` | Download filled form PDF |
| POST | `/web-autofill` | Trigger Selenium web autofill |

---

## Important Notes

- Never commit the `venv/` folder
- Never commit the `.env` file
- Never commit files inside `uploads/` or `outputs/` (already in `.gitignore`)
- Always activate venv before working
- Always run `pip freeze > requirements.txt` after installing new packages

---

## Git Workflow

| Branch | Owner | Purpose |
|--------|-------|---------|
| main | All | Final working code only |
| feature/frontend | Frontend dev | HTML, CSS, JS files |
| feature/backend | Backend dev | Flask, database, routes |
| feature/ml | ML dev | OCR, NLP, autofill models |

Always work on your own branch and raise a Pull Request to merge into `main`.

---

> This project is developed as a college project.
> **FormAssist** — AI Based Assisted Digital Form Automation System