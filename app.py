import os
import json
from datetime import datetime
from functools import wraps
from werkzeug.utils import secure_filename

from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, g, jsonify, send_file)

from database.db import db
from database.user_model import User
from database.submission_model import Submission
from routes.output_routes import output_bp

app = Flask(__name__)
app.config.from_object('config.Config')
db.init_app(app)

app.register_blueprint(output_bp, url_prefix='/output')

os.makedirs('uploads/', exist_ok=True)
os.makedirs('outputs/', exist_ok=True)

# ── Form type definitions ──────────────────────────────────────────────────────
AVATAR_COLORS = ["#7c3aed","#db2777","#059669","#dc2626","#d97706","#2563eb","#0891b2"]

FORM_TYPES_LIST = [
    {"type": "scholarship",          "label": "Scholarship Form",     "icon": "🎓", "color": "#7c3aed", "desc": "Apply for university or college scholarships with AI-extracted document data"},
    {"type": "college_admission",    "label": "College Admission",    "icon": "🏫", "color": "#2563eb", "desc": "College and university admission applications with marksheet extraction"},
    {"type": "visa_application",     "label": "Visa Application",     "icon": "✈️", "color": "#0891b2", "desc": "Tourist, student and work visa applications worldwide"},
    {"type": "kyc_verification",     "label": "KYC Verification",     "icon": "🏦", "color": "#059669", "desc": "Bank and financial institution KYC with Aadhaar & PAN"},
    {"type": "passport_application", "label": "Passport Application", "icon": "📘", "color": "#d97706", "desc": "Fresh and renewal passport applications with photo upload"},
    {"type": "driving_licence",      "label": "Driving Licence",      "icon": "🚗", "color": "#0891b2", "desc": "DL application, renewal and address change forms"},
    {"type": "income_tax_return",    "label": "Income Tax Return",    "icon": "📊", "color": "#7c3aed", "desc": "File ITR with AI-powered pre-fill from Form 16"},
    {"type": "insurance_claim",      "label": "Insurance Claim",      "icon": "🛡", "color": "#dc2626", "desc": "Health, vehicle and general insurance claim forms"},
    {"type": "general_purpose",      "label": "General Purpose",      "icon": "📝", "color": "#64748b", "desc": "Custom form for any purpose — letters, applications, more"},
]

FORM_TYPES = {f["type"]: f for f in FORM_TYPES_LIST}

# ── Helpers ────────────────────────────────────────────────────────────────────
def now_str():
    return datetime.now().strftime("%d %b %Y, %I:%M %p")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf', 'jpg', 'jpeg', 'png', 'PNG', 'JPG', 'JPEG', 'PDF'}

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.before_request
def load_user():
    user_id = session.get('user_id')
    g.current_user = None
    if user_id:
        user = User.query.get(user_id)
        if user:
            user.avatar_color = AVATAR_COLORS[user.id % len(AVATAR_COLORS)]
            g.current_user = user

@app.context_processor
def inject_globals():
    return dict(
        current_user    = g.current_user,
        form_types      = FORM_TYPES,
        form_types_list = FORM_TYPES_LIST,
        unread_count    = 0,
    )

# ── Public routes ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    if g.current_user:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/login")
def login():
    if g.current_user:
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/signup")
def signup():
    if g.current_user:
        return redirect(url_for("dashboard"))
    return render_template("signup.html")

@app.route("/auth/login", methods=["POST"])
def auth_login():
    from werkzeug.security import check_password_hash
    email    = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    user     = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session['user_id']   = user.id
        session['user_name'] = user.name
        flash(f"Welcome back, {user.name}!", "success")
        return redirect(url_for("dashboard"))
    flash("Invalid email or password.", "error")
    return redirect(url_for("login"))

@app.route("/auth/signup", methods=["POST"])
def auth_signup():
    from werkzeug.security import generate_password_hash
    name     = request.form.get("name", "").strip()
    email    = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm  = request.form.get("confirm", "")
    if not all([name, email, password]):
        flash("All fields are required.", "error")
        return redirect(url_for("signup"))
    if password != confirm:
        flash("Passwords do not match.", "error")
        return redirect(url_for("signup"))
    if len(password) < 6:
        flash("Password must be at least 6 characters.", "error")
        return redirect(url_for("signup"))
    if User.query.filter_by(email=email).first():
        flash("Email already registered.", "error")
        return redirect(url_for("signup"))
    hashed   = generate_password_hash(password)
    new_user = User(name=name, email=email, password=hashed)
    db.session.add(new_user)
    db.session.commit()
    session['user_id']   = new_user.id
    session['user_name'] = new_user.name
    flash(f"Account created! Welcome, {name}!", "success")
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

# ── Dashboard ──────────────────────────────────────────────────────────────────
@app.route("/dashboard")
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    subs = Submission.query.filter_by(user_id=user.id).order_by(
        Submission.submitted_at.desc()).all()

    enriched = []
    for sub in subs:
        fi = FORM_TYPES.get(sub.form_type,
             {"label": sub.form_type, "icon": "📋", "color": "#64748b"})
        enriched.append({
            "id":           sub.id,
            "form_type":    sub.form_type,
            "form_name":    fi["label"],
            "form_icon":    fi["icon"],
            "form_color":   fi["color"],
            "status":       sub.status,
            "submitted_at": sub.submitted_at.strftime("%d %b %Y, %I:%M %p")
                            if sub.submitted_at else "",
            "data":         json.loads(sub.data_json) if sub.data_json else {},
        })

    stats = {
        "total":      len(enriched),
        "submitted":  sum(1 for s in enriched if s["status"] == "Submitted"),
        "draft":      sum(1 for s in enriched if s["status"] == "Draft"),
        "this_month": len(enriched),
    }

    return render_template("dashboard.html",
        user            = user,
        submissions     = enriched,
        stats           = stats,
        form_types_list = FORM_TYPES_LIST,
    )

# ── Form select ────────────────────────────────────────────────────────────────
@app.route("/form/select")
@login_required
def form_select():
    return render_template("form_select.html", forms=FORM_TYPES_LIST)

# ── Upload page ────────────────────────────────────────────────────────────────
@app.route("/form/upload/<form_type>")
@login_required
def upload_page(form_type):
    from services.document_mapping_service import get_required_documents
    fi            = FORM_TYPES.get(form_type,
                    {"label": form_type, "icon": "📋", "color": "#64748b"})
    required_docs = get_required_documents(form_type)
    return render_template("upload.html",
        form_type     = form_type,
        form_info     = fi,
        required_docs = required_docs,
    )

# ── Upload documents POST ──────────────────────────────────────────────────────
@app.route("/upload/documents", methods=["POST"])
@login_required
def upload_documents():
    from services.ocr_service import extract_text
    from services.ai_service import process_ocr_text
    from services.compression_service import compress_file

    results           = {}
    combined_entities = {}
    compressed_files  = []

    for field_name in request.files:
        file = request.files[field_name]
        if not file or file.filename == '':
            continue
        if not allowed_file(file.filename):
            continue
        filename    = secure_filename(file.filename)
        upload_path = os.path.join('uploads/', filename)
        file.save(upload_path)

        raw_text   = extract_text(upload_path)
        entities   = process_ocr_text(raw_text, doc_type=field_name)
        compressed = compress_file(upload_path)
        compressed_files.append(compressed)

        results[field_name] = {
            'filename': filename,
            'entities': entities,
        }
        for key, value in entities.items():
            if value and not combined_entities.get(key):
                combined_entities[key] = value

    session['extracted_data']   = combined_entities
    session['compressed_files'] = compressed_files
    session['form_type']        = request.form.get('form_type', '')
    session['upload_results']   = results

    return redirect(url_for('extracted_page'))

# ── Extracted data review ──────────────────────────────────────────────────────
@app.route("/form/extracted")
@login_required
def extracted_page():
    from services.document_mapping_service import get_required_documents
    form_type   = session.get('form_type', '')
    raw_results = session.get('upload_results', {})
    fi          = FORM_TYPES.get(form_type,
                  {"label": form_type, "icon": "📋", "color": "#64748b"})

    formatted = {}
    for doc_name, result in raw_results.items():
        formatted[doc_name] = {
            "ok":       True,
            "entities": result.get('entities', {}),
            "raw_text": "",
        }

    # Show required docs not uploaded as failed cards
    required = get_required_documents(form_type)
    for doc in required:
        if doc['name'] not in formatted:
            formatted[doc['label']] = {
                "ok": False, "entities": {}, "raw_text": ""}

    return render_template("extracted.html",
        extracted_results = formatted,
        form_type         = form_type,
        form_info         = fi,
    )

# ── Form fill ──────────────────────────────────────────────────────────────────
@app.route("/form/fill/<form_type>")
@login_required
def form_fill_get(form_type):
    from services.form_mapping_service import get_form_fields, get_user_data
    from services.ai_service import get_autofill_suggestions
    user          = User.query.get(session['user_id'])
    form_fields   = get_form_fields(form_type)
    fi            = FORM_TYPES.get(form_type,
                    {"label": form_type, "icon": "📋", "color": "#64748b"})
    user_dict     = get_user_data(user)
    extracted     = session.get('extracted_data', {})
    merged        = {**user_dict, **extracted}
    autofill_data = get_autofill_suggestions(merged)
    return render_template("form_fill.html",
        form_fields   = form_fields,
        autofill_data = autofill_data,
        form_type     = form_type,
        form_info     = fi,
        errors        = [],
    )

# ── Form submit ────────────────────────────────────────────────────────────────
@app.route("/form/submit", methods=["POST"])
@login_required
def form_submit():
    from services.form_mapping_service import get_form_fields
    from services.validation_service import validate_step1
    form_data = request.form.to_dict()
    form_type = form_data.get('form_type', 'general_purpose')
    fi        = FORM_TYPES.get(form_type,
                {"label": form_type, "icon": "📋", "color": "#64748b"})
    errors    = validate_step1(form_data)
    if errors:
        form_fields = get_form_fields(form_type)
        return render_template("form_fill.html",
            form_fields   = form_fields,
            autofill_data = form_data,
            form_type     = form_type,
            form_info     = fi,
            errors        = errors,
        )
    new_sub = Submission(
        user_id   = session['user_id'],
        form_type = form_type,
        data_json = json.dumps(form_data),
        status    = "Submitted",
    )
    db.session.add(new_sub)
    db.session.commit()

    # Store only the submission ID — avoids session cookie overflow
    session['last_submission_id'] = new_sub.id
    session['last_form_type']     = form_type
    flash("Form submitted successfully!", "success")
    return redirect(url_for("result"))

# ── Review ─────────────────────────────────────────────────────────────────────
@app.route("/form/review", methods=["GET", "POST"])
@login_required
def review_page():
    sub_id    = session.get('last_submission_id')
    form_type = session.get('last_form_type', 'general_purpose')
    fi        = FORM_TYPES.get(form_type,
                {"label": form_type, "icon": "📋", "color": "#64748b"})
    sub       = {}
    form_data = {}
    if sub_id:
        db_sub = Submission.query.get(sub_id)
        if db_sub:
            form_data = json.loads(db_sub.data_json) if db_sub.data_json else {}
            fi2 = FORM_TYPES.get(db_sub.form_type,
                  {"label": db_sub.form_type, "icon": "📋", "color": "#64748b"})
            sub = {
                "id":           db_sub.id,
                "form_type":    db_sub.form_type,
                "form_name":    fi2["label"],
                "form_icon":    fi2["icon"],
                "form_color":   fi2["color"],
                "status":       db_sub.status,
                "submitted_at": db_sub.submitted_at.strftime("%d %b %Y, %I:%M %p")
                                if db_sub.submitted_at else "",
                "data":         form_data,
            }
    if request.method == "POST":
        return redirect(url_for("result"))
    return render_template("review.html",
        data      = form_data,
        sub       = sub,
        form_type = form_type,
        form_info = fi,
    )

# ── Result ─────────────────────────────────────────────────────────────────────
@app.route("/result")
@login_required
def result():
    sub_id    = session.get('last_submission_id')
    form_type = session.get('last_form_type', 'general_purpose')
    sub       = {}
    form_data = {}
    if sub_id:
        db_sub = Submission.query.get(sub_id)
        if db_sub:
            form_data = json.loads(db_sub.data_json) if db_sub.data_json else {}
            fi = FORM_TYPES.get(db_sub.form_type,
                 {"label": db_sub.form_type, "icon": "📋", "color": "#64748b"})
            sub = {
                "id":           db_sub.id,
                "form_type":    db_sub.form_type,
                "form_name":    fi["label"],
                "form_icon":    fi["icon"],
                "form_color":   fi["color"],
                "status":       db_sub.status,
                "submitted_at": db_sub.submitted_at.strftime("%d %b %Y, %I:%M %p")
                                if db_sub.submitted_at else "",
                "data":         form_data,
            }
    return render_template("result.html",
        sub       = sub,
        form_type = form_type,
        data      = form_data,
    )

# ── AI autofill API ────────────────────────────────────────────────────────────
@app.route("/form/ai/autofill", methods=["POST"])
@login_required
def ai_autofill():
    from services.form_mapping_service import get_user_data
    from services.ai_service import get_autofill_suggestions
    user      = User.query.get(session['user_id'])
    user_dict = get_user_data(user)
    extracted = session.get('extracted_data', {})
    merged    = {**user_dict, **extracted}
    fields    = get_autofill_suggestions(merged)
    return jsonify({"fields": fields, "status": "ok", "source": "AI + OCR"})

# ── Download ZIP ───────────────────────────────────────────────────────────────
@app.route("/download/zip")
@login_required
def download_zip():
    from services.zip_service import create_zip
    compressed_files = session.get('compressed_files', [])
    output_path      = os.path.join('outputs/', 'compressed_documents.zip')
    create_zip(compressed_files, output_path)
    return send_file(output_path, as_attachment=True,
                     download_name='compressed_documents.zip')

# ── Download PDF ───────────────────────────────────────────────────────────────
@app.route("/download/pdf", methods=["POST"])
@login_required
def download_pdf():
    from services.pdf_service import generate_form_pdf

    payload = request.json or {}

    # If fields empty, load from DB
    if not payload.get('fields') or not any(payload.get('fields', {}).values()):
        sub_id = session.get('last_submission_id')
        if sub_id:
            db_sub = Submission.query.get(sub_id)
            if db_sub and db_sub.data_json:
                fi = FORM_TYPES.get(db_sub.form_type,
                     {"label": db_sub.form_type, "icon": "📋", "color": "#64748b"})
                payload = {
                    'form_type': db_sub.form_type,
                    'form_name': fi["label"],
                    'fields':    json.loads(db_sub.data_json),
                }

    form_type   = payload.get('form_type', 'general_purpose')
    output_path = os.path.join('outputs/', f'{form_type}_filled.pdf')
    generate_form_pdf(form_type, payload, output_path)
    return send_file(output_path, as_attachment=True,
                     download_name=f'{form_type}_filled_form.pdf')

# ── Web autofill ───────────────────────────────────────────────────────────────
@app.route("/web-autofill", methods=["POST"])
@app.route("/output/web-autofill", methods=["POST"])
@login_required
def web_autofill():
    from services.web_autofill_service import autofill_website
    data      = request.json or {}
    url       = data.get('url')
    form_data = data.get('form_data', {})

    if not url:
        return jsonify({'success': False, 'error': 'No URL provided'}), 400

    # If form_data is empty (session cookie overflow dropped it),
    # load from database using the last submission ID
    if not form_data or not any(str(v).strip() for v in form_data.values()):
        sub_id = session.get('last_submission_id')
        if sub_id:
            db_sub = Submission.query.get(sub_id)
            if db_sub and db_sub.data_json:
                form_data = json.loads(db_sub.data_json)
                print(f"Loaded form data from DB (submission #{sub_id})")

    print(f"Starting web autofill for: {url}")
    print(f"Fields available: {[k for k, v in form_data.items() if str(v).strip()]}")

    result = autofill_website(url, form_data)
    return jsonify(result)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database created successfully!")
    app.run(debug=True, port=5000)