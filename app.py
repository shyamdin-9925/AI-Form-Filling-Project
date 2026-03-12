from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, g, jsonify, send_file)
from functools import wraps
from datetime import datetime
import uuid, io, zipfile

app = Flask(__name__)
app.secret_key = "formassist_fullsecret_2025"

# ── In-memory stores ───────────────────────────────────────────────────────────
users        = {}
submissions  = {}

# ── Constants ──────────────────────────────────────────────────────────────────
AVATAR_COLORS = ["#7c3aed","#2563eb","#059669","#dc2626","#d97706","#db2777","#0891b2"]

FORM_TYPES = [
    {"type":"scholarship",       "label":"Scholarship Form",      "icon":"🎓","color":"#7c3aed","desc":"University & college scholarship applications"},
    {"type":"college_admission",  "label":"College Admission",     "icon":"🏛","color":"#2563eb","desc":"UG & PG college admission applications"},
    {"type":"visa_application",   "label":"Visa Application",      "icon":"✈️","color":"#0891b2","desc":"International travel visa applications"},
    {"type":"kyc_verification",   "label":"KYC Verification",      "icon":"🪪","color":"#059669","desc":"Bank & financial KYC verification"},
    {"type":"passport_application","label":"Passport Application", "icon":"📘","color":"#d97706","desc":"New passport & renewal applications"},
    {"type":"driving_licence",    "label":"Driving Licence",       "icon":"🚗","color":"#dc2626","desc":"New DL & renewal at RTO"},
    {"type":"income_tax_return",  "label":"Income Tax Return",     "icon":"📊","color":"#db2777","desc":"Annual ITR filing with Form 16"},
    {"type":"insurance_claim",    "label":"Insurance Claim",       "icon":"🛡","color":"#6d28d9","desc":"Health, vehicle & general insurance claims"},
    {"type":"general_purpose",    "label":"General Purpose",       "icon":"📝","color":"#64748b","desc":"Any form needing Aadhaar & PAN details"},
]

REQUIRED_DOCS = {
    "scholarship": [
        {"name":"aadhaar",      "label":"Aadhaar Card",           "accept":".jpg,.jpeg,.pdf","max_kb":200},
        {"name":"pan",          "label":"PAN Card",               "accept":".jpg,.jpeg,.pdf","max_kb":200},
        {"name":"marksheet_10", "label":"10th Marksheet",         "accept":".jpg,.jpeg,.pdf","max_kb":500},
        {"name":"marksheet_12", "label":"12th Marksheet",         "accept":".jpg,.jpeg,.pdf","max_kb":500},
        {"name":"caste_cert",   "label":"Caste Certificate",      "accept":".pdf","max_kb":300},
        {"name":"income_cert",  "label":"Income Certificate",     "accept":".pdf","max_kb":300},
        {"name":"bank_passbook","label":"Bank Passbook (front)",  "accept":".jpg,.jpeg,.pdf","max_kb":200},
        {"name":"school_lc",    "label":"School Leaving Certificate","accept":".pdf","max_kb":300},
    ],
    "college_admission": [
        {"name":"aadhaar",      "label":"Aadhaar Card",           "accept":".jpg,.jpeg,.pdf","max_kb":200},
        {"name":"marksheet_10", "label":"10th Marksheet",         "accept":".jpg,.jpeg,.pdf","max_kb":500},
        {"name":"marksheet_12", "label":"12th Marksheet",         "accept":".jpg,.jpeg,.pdf","max_kb":500},
        {"name":"school_lc",    "label":"School Leaving Certificate","accept":".pdf","max_kb":300},
        {"name":"caste_cert",   "label":"Caste Certificate",      "accept":".pdf","max_kb":300},
        {"name":"passport_photo","label":"Passport Photo",        "accept":".jpg,.jpeg","max_kb":50},
    ],
    "visa_application": [
        {"name":"passport_doc", "label":"Passport (scan)",        "accept":".jpg,.jpeg,.pdf","max_kb":500},
        {"name":"aadhaar",      "label":"Aadhaar Card",           "accept":".jpg,.jpeg,.pdf","max_kb":200},
        {"name":"pan",          "label":"PAN Card",               "accept":".jpg,.jpeg,.pdf","max_kb":200},
        {"name":"bank_passbook","label":"Bank Passbook (front)",  "accept":".jpg,.jpeg,.pdf","max_kb":200},
        {"name":"passport_photo","label":"Passport Photo",        "accept":".jpg,.jpeg","max_kb":50},
    ],
    "kyc_verification": [
        {"name":"aadhaar",      "label":"Aadhaar Card",           "accept":".jpg,.jpeg,.pdf","max_kb":200},
        {"name":"pan",          "label":"PAN Card",               "accept":".jpg,.jpeg,.pdf","max_kb":200},
        {"name":"bank_passbook","label":"Bank Passbook (front)",  "accept":".jpg,.jpeg,.pdf","max_kb":200},
        {"name":"passport_photo","label":"Passport Photo",        "accept":".jpg,.jpeg","max_kb":50},
    ],
    "passport_application": [
        {"name":"aadhaar",      "label":"Aadhaar Card",           "accept":".jpg,.jpeg,.pdf","max_kb":200},
        {"name":"pan",          "label":"PAN Card",               "accept":".jpg,.jpeg,.pdf","max_kb":200},
        {"name":"birth_cert",   "label":"Birth Certificate",      "accept":".jpg,.jpeg,.pdf","max_kb":300},
        {"name":"marksheet_10", "label":"10th Marksheet",         "accept":".jpg,.jpeg,.pdf","max_kb":500},
    ],
    "driving_licence": [
        {"name":"aadhaar",      "label":"Aadhaar Card",           "accept":".jpg,.jpeg,.pdf","max_kb":200},
        {"name":"birth_cert",   "label":"Birth Certificate",      "accept":".jpg,.jpeg,.pdf","max_kb":300},
        {"name":"passport_photo","label":"Passport Photo",        "accept":".jpg,.jpeg","max_kb":50},
    ],
    "income_tax_return": [
        {"name":"aadhaar",      "label":"Aadhaar Card",           "accept":".jpg,.jpeg,.pdf","max_kb":200},
        {"name":"pan",          "label":"PAN Card",               "accept":".jpg,.jpeg,.pdf","max_kb":200},
        {"name":"bank_passbook","label":"Bank Passbook (front)",  "accept":".jpg,.jpeg,.pdf","max_kb":200},
        {"name":"form_16",      "label":"Form 16 (from employer)","accept":".pdf","max_kb":500},
    ],
    "insurance_claim": [
        {"name":"aadhaar",      "label":"Aadhaar Card",           "accept":".jpg,.jpeg,.pdf","max_kb":200},
        {"name":"pan",          "label":"PAN Card",               "accept":".jpg,.jpeg,.pdf","max_kb":200},
        {"name":"bank_passbook","label":"Bank Passbook (front)",  "accept":".jpg,.jpeg,.pdf","max_kb":200},
        {"name":"birth_cert",   "label":"Birth Certificate",      "accept":".jpg,.jpeg,.pdf","max_kb":300},
    ],
    "general_purpose": [
        {"name":"aadhaar",      "label":"Aadhaar Card",           "accept":".jpg,.jpeg,.pdf","max_kb":200},
        {"name":"pan",          "label":"PAN Card",               "accept":".jpg,.jpeg,.pdf","max_kb":200},
    ],
}

FORM_FIELDS = {
    "scholarship": [
        {"name":"full_name",   "label":"Full Name",             "type":"text"},
        {"name":"dob",         "label":"Date of Birth",         "type":"date"},
        {"name":"aadhaar_no",  "label":"Aadhaar Number",        "type":"text"},
        {"name":"pan_no",      "label":"PAN Number",            "type":"text"},
        {"name":"address",     "label":"Permanent Address",     "type":"textarea"},
        {"name":"gender",      "label":"Gender",                "type":"text"},
        {"name":"category",    "label":"Category (SC/ST/OBC/GEN)","type":"text"},
        {"name":"annual_income","label":"Annual Family Income (₹)","type":"number"},
        {"name":"percentage_10","label":"10th Percentage / CGPA","type":"text"},
        {"name":"board_10",    "label":"10th Board Name",       "type":"text"},
        {"name":"percentage_12","label":"12th Percentage / CGPA","type":"text"},
        {"name":"board_12",    "label":"12th Board Name",       "type":"text"},
        {"name":"bank_account","label":"Bank Account Number",   "type":"text"},
        {"name":"ifsc_code",   "label":"IFSC Code",             "type":"text"},
        {"name":"bank_name",   "label":"Bank Name",             "type":"text"},
        {"name":"college_name","label":"College / University Name","type":"text"},
        {"name":"course_name", "label":"Course Applied For",    "type":"text"},
        {"name":"mobile",      "label":"Mobile Number",         "type":"tel"},
        {"name":"email",       "label":"Email Address",         "type":"email"},
    ],
    "college_admission": [
        {"name":"full_name",   "label":"Full Name",             "type":"text"},
        {"name":"dob",         "label":"Date of Birth",         "type":"date"},
        {"name":"aadhaar_no",  "label":"Aadhaar Number",        "type":"text"},
        {"name":"address",     "label":"Permanent Address",     "type":"textarea"},
        {"name":"gender",      "label":"Gender",                "type":"text"},
        {"name":"category",    "label":"Category",              "type":"text"},
        {"name":"percentage_10","label":"10th Percentage",      "type":"text"},
        {"name":"board_10",    "label":"10th Board",            "type":"text"},
        {"name":"percentage_12","label":"12th Percentage",      "type":"text"},
        {"name":"board_12",    "label":"12th Board",            "type":"text"},
        {"name":"college_name","label":"Preferred College",     "type":"text"},
        {"name":"course_name", "label":"Course Applying For",   "type":"text"},
        {"name":"mobile",      "label":"Mobile Number",         "type":"tel"},
        {"name":"email",       "label":"Email Address",         "type":"email"},
    ],
    "visa_application": [
        {"name":"full_name",   "label":"Full Name",             "type":"text"},
        {"name":"dob",         "label":"Date of Birth",         "type":"date"},
        {"name":"passport_no", "label":"Passport Number",       "type":"text"},
        {"name":"passport_exp","label":"Passport Expiry Date",  "type":"date"},
        {"name":"nationality", "label":"Nationality",           "type":"text"},
        {"name":"place_birth", "label":"Place of Birth",        "type":"text"},
        {"name":"aadhaar_no",  "label":"Aadhaar Number",        "type":"text"},
        {"name":"pan_no",      "label":"PAN Number",            "type":"text"},
        {"name":"bank_account","label":"Bank Account Number",   "type":"text"},
        {"name":"ifsc_code",   "label":"IFSC Code",             "type":"text"},
        {"name":"address",     "label":"Residential Address",   "type":"textarea"},
        {"name":"destination", "label":"Destination Country",   "type":"text"},
        {"name":"travel_date", "label":"Travel Date",           "type":"date"},
        {"name":"purpose",     "label":"Purpose of Visit",      "type":"text"},
        {"name":"mobile",      "label":"Mobile Number",         "type":"tel"},
        {"name":"email",       "label":"Email Address",         "type":"email"},
    ],
    "kyc_verification": [
        {"name":"full_name",   "label":"Full Name",             "type":"text"},
        {"name":"dob",         "label":"Date of Birth",         "type":"date"},
        {"name":"aadhaar_no",  "label":"Aadhaar Number",        "type":"text"},
        {"name":"pan_no",      "label":"PAN Number",            "type":"text"},
        {"name":"address",     "label":"Current Address",       "type":"textarea"},
        {"name":"bank_account","label":"Bank Account Number",   "type":"text"},
        {"name":"ifsc_code",   "label":"IFSC Code",             "type":"text"},
        {"name":"bank_name",   "label":"Bank Name",             "type":"text"},
        {"name":"mobile",      "label":"Mobile Number",         "type":"tel"},
        {"name":"email",       "label":"Email Address",         "type":"email"},
    ],
    "passport_application": [
        {"name":"full_name",   "label":"Full Name",             "type":"text"},
        {"name":"dob",         "label":"Date of Birth",         "type":"date"},
        {"name":"place_birth", "label":"Place of Birth",        "type":"text"},
        {"name":"aadhaar_no",  "label":"Aadhaar Number",        "type":"text"},
        {"name":"pan_no",      "label":"PAN Number",            "type":"text"},
        {"name":"father_name", "label":"Father's Name",         "type":"text"},
        {"name":"mother_name", "label":"Mother's Name",         "type":"text"},
        {"name":"address",     "label":"Permanent Address",     "type":"textarea"},
        {"name":"board_10",    "label":"10th Board Name",       "type":"text"},
        {"name":"pass_year_10","label":"10th Passing Year",     "type":"text"},
        {"name":"mobile",      "label":"Mobile Number",         "type":"tel"},
        {"name":"email",       "label":"Email Address",         "type":"email"},
    ],
    "driving_licence": [
        {"name":"full_name",   "label":"Full Name",             "type":"text"},
        {"name":"dob",         "label":"Date of Birth",         "type":"date"},
        {"name":"place_birth", "label":"Place of Birth",        "type":"text"},
        {"name":"aadhaar_no",  "label":"Aadhaar Number",        "type":"text"},
        {"name":"address",     "label":"Current Address",       "type":"textarea"},
        {"name":"blood_group", "label":"Blood Group",           "type":"text"},
        {"name":"vehicle_type","label":"Vehicle Type (LMV/MC)",  "type":"text"},
        {"name":"mobile",      "label":"Mobile Number",         "type":"tel"},
        {"name":"email",       "label":"Email Address",         "type":"email"},
    ],
    "income_tax_return": [
        {"name":"full_name",   "label":"Full Name",             "type":"text"},
        {"name":"dob",         "label":"Date of Birth",         "type":"date"},
        {"name":"aadhaar_no",  "label":"Aadhaar Number",        "type":"text"},
        {"name":"pan_no",      "label":"PAN Number",            "type":"text"},
        {"name":"address",     "label":"Residential Address",   "type":"textarea"},
        {"name":"annual_income","label":"Gross Annual Income (₹)","type":"number"},
        {"name":"employer",    "label":"Employer Name",         "type":"text"},
        {"name":"bank_account","label":"Bank Account Number",   "type":"text"},
        {"name":"ifsc_code",   "label":"IFSC Code",             "type":"text"},
        {"name":"bank_name",   "label":"Bank Name",             "type":"text"},
        {"name":"mobile",      "label":"Mobile Number",         "type":"tel"},
        {"name":"email",       "label":"Email Address",         "type":"email"},
    ],
    "insurance_claim": [
        {"name":"full_name",   "label":"Policyholder Name",     "type":"text"},
        {"name":"dob",         "label":"Date of Birth",         "type":"date"},
        {"name":"place_birth", "label":"Place of Birth",        "type":"text"},
        {"name":"aadhaar_no",  "label":"Aadhaar Number",        "type":"text"},
        {"name":"pan_no",      "label":"PAN Number",            "type":"text"},
        {"name":"address",     "label":"Residential Address",   "type":"textarea"},
        {"name":"policy_no",   "label":"Policy Number",         "type":"text"},
        {"name":"claim_amount","label":"Claim Amount (₹)",      "type":"number"},
        {"name":"bank_account","label":"Bank Account Number",   "type":"text"},
        {"name":"ifsc_code",   "label":"IFSC Code",             "type":"text"},
        {"name":"incident_date","label":"Date of Incident",     "type":"date"},
        {"name":"reason",      "label":"Reason for Claim",      "type":"textarea"},
        {"name":"mobile",      "label":"Mobile Number",         "type":"tel"},
        {"name":"email",       "label":"Email Address",         "type":"email"},
    ],
    "general_purpose": [
        {"name":"full_name",   "label":"Full Name",             "type":"text"},
        {"name":"dob",         "label":"Date of Birth",         "type":"date"},
        {"name":"aadhaar_no",  "label":"Aadhaar Number",        "type":"text"},
        {"name":"pan_no",      "label":"PAN Number",            "type":"text"},
        {"name":"address",     "label":"Address",               "type":"textarea"},
        {"name":"mobile",      "label":"Mobile Number",         "type":"tel"},
        {"name":"email",       "label":"Email Address",         "type":"email"},
        {"name":"purpose",     "label":"Purpose / Subject",     "type":"text"},
        {"name":"notes",       "label":"Additional Notes",      "type":"textarea"},
    ],
}

# Mock OCR output per doc type
OCR_MOCK = {
    "aadhaar":       {"Name":"Rahul Sharma","Date of Birth":"15/08/1995","Aadhaar Number":"3425 0653 1151","Address":"42 MG Road, Andheri West, Mumbai 400053","Gender":"Male","Phone":"Not found"},
    "pan":           {"PAN Number":"ABCRS1234F","Name":"Rahul Sharma","Date of Birth":"15/08/1995","Father's Name":"Suresh Sharma"},
    "marksheet_10":  {"Percentage / CGPA":"88.4%","Board Name":"CBSE","Passing Year":"2011","School Name":"Delhi Public School"},
    "marksheet_12":  {"Percentage / CGPA":"85.6%","Board Name":"CBSE","Passing Year":"2013","School Name":"Delhi Public School"},
    "caste_cert":    {"Caste":"Sharma","Category":"General"},
    "income_cert":   {"Annual Income":"₹4,50,000"},
    "bank_passbook": {"Account Number":"9876543210123","IFSC Code":"SBIN0001234","Bank Name":"State Bank of India","Account Holder":"Rahul Sharma"},
    "school_lc":     {"Student Name":"Rahul Sharma","School":"Delhi Public School","Date of Leaving":"2013"},
    "passport_photo":{"Note":"Photo uploaded successfully"},
    "passport_doc":  {"Passport Number":"P1234567","Expiry Date":"2030-06-15","Nationality":"Indian","Place of Birth":"Mumbai"},
    "birth_cert":    {"Date of Birth":"15/08/1995","Place of Birth":"Mumbai","Name":"Rahul Sharma"},
    "form_16":       {"Employer":"TechCorp India Pvt Ltd","Gross Income":"₹9,50,000","TDS Deducted":"₹85,000"},
}

AI_AUTOFILL = {
    "full_name":"Rahul Sharma","dob":"1995-08-15","aadhaar_no":"342506531151",
    "pan_no":"ABCRS1234F","address":"42 MG Road, Andheri West, Mumbai 400053",
    "gender":"Male","category":"General","annual_income":"450000",
    "percentage_10":"88.4","board_10":"CBSE","percentage_12":"85.6","board_12":"CBSE",
    "bank_account":"9876543210123","ifsc_code":"SBIN0001234","bank_name":"State Bank of India",
    "father_name":"Suresh Sharma","mother_name":"Priya Sharma","place_birth":"Mumbai",
    "nationality":"Indian","passport_no":"P1234567","passport_exp":"2030-06-15",
    "pass_year_10":"2011","employer":"TechCorp India Pvt Ltd",
    "college_name":"","course_name":"","destination":"","travel_date":"",
    "purpose":"","policy_no":"","claim_amount":"","incident_date":"",
    "reason":"","vehicle_type":"LMV","blood_group":"O+","mobile":"","email":"","notes":"",
}

def now_str(): return datetime.now().strftime("%d %b %Y, %I:%M %p")
def get_form_info(ftype): return next((f for f in FORM_TYPES if f["type"]==ftype), FORM_TYPES[-1])

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        email = session.get("user_email")
        if not email:
            flash("Please log in to continue.", "error"); return redirect(url_for("login"))
        if email not in users:
            session.pop("user_email",None); flash("Session expired.","error"); return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.before_request
def load_user():
    email = session.get("user_email")
    if email and email not in users: session.pop("user_email",None); email=None
    g.current_user = users.get(email) if email else None

@app.context_processor
def inject_globals():
    return dict(current_user=g.current_user, form_types_list=FORM_TYPES)

# ── PUBLIC ROUTES ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    if g.current_user: return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/login")
def login():
    if g.current_user: return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/signup")
def signup():
    if g.current_user: return redirect(url_for("dashboard"))
    return render_template("signup.html")

@app.route("/auth/login", methods=["POST"])
def auth_login():
    email=request.form.get("email","").strip().lower()
    pw=request.form.get("password","")
    user=users.get(email)
    if user and user["password"]==pw:
        session["user_email"]=email
        flash(f"Welcome back, {user['name']}!", "success")
        return redirect(url_for("dashboard"))
    return render_template("login.html", error="Invalid email or password.")

@app.route("/auth/signup", methods=["POST"])
def auth_signup():
    name=request.form.get("name","").strip()
    email=request.form.get("email","").strip().lower()
    pw=request.form.get("password","")
    conf=request.form.get("confirm","")
    if not all([name,email,pw]): return render_template("signup.html", error="All fields required.")
    if pw!=conf: return render_template("signup.html", error="Passwords do not match.")
    if len(pw)<6: return render_template("signup.html", error="Password must be at least 6 characters.")
    if email in users: return render_template("signup.html", error="Email already registered.")
    color=AVATAR_COLORS[len(users)%len(AVATAR_COLORS)]
    users[email]={"name":name,"email":email,"password":pw,"joined_at":now_str(),"avatar_color":color}
    submissions[email]=[]
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("user_email",None)
    flash("Logged out successfully.","success")
    return redirect(url_for("login"))

# ── PROTECTED ROUTES ───────────────────────────────────────────────────────────
@app.route("/dashboard/")
@app.route("/dashboard")
@login_required
def dashboard():
    email=session["user_email"]
    subs=list(reversed(submissions.get(email,[])))
    stats={"total":len(subs),"submitted":sum(1 for s in subs if s.get("status")=="Submitted"),"draft":sum(1 for s in subs if s.get("status")=="Draft")}
    return render_template("dashboard.html", user=users[email], submissions=subs, stats=stats)

@app.route("/form/select")
@login_required
def form_select():
    return render_template("form_select.html", forms=FORM_TYPES)

@app.route("/upload/<form_type>")
@login_required
def upload_page(form_type):
    docs=REQUIRED_DOCS.get(form_type, REQUIRED_DOCS["general_purpose"])
    form_info=get_form_info(form_type)
    return render_template("upload.html", form_type=form_type, required_docs=docs, form_info=form_info)

@app.route("/upload/documents", methods=["POST"])
@login_required
def upload_documents():
    form_type=request.form.get("form_type","general_purpose")
    docs=REQUIRED_DOCS.get(form_type, REQUIRED_DOCS["general_purpose"])
    # Simulate OCR extraction
    extracted = {}
    for doc in docs:
        fname=doc["name"]
        file=request.files.get(fname)
        if file and file.filename:
            extracted[doc["label"]] = {"entities": OCR_MOCK.get(fname, {"Note":"Processed"}), "ok": True}
        else:
            extracted[doc["label"]] = {"entities": {}, "ok": False}
    session["extracted_results"] = extracted
    session["current_form_type"] = form_type
    return redirect(url_for("extracted_page"))

@app.route("/extracted")
@login_required
def extracted_page():
    extracted=session.get("extracted_results",{})
    form_type=session.get("current_form_type","general_purpose")
    form_info=get_form_info(form_type)
    return render_template("extracted.html", extracted_results=extracted, form_type=form_type, form_info=form_info)

@app.route("/form/fill/<form_type>")
@login_required
def form_fill_get(form_type):
    session["current_form_type"]=form_type
    form_fields=FORM_FIELDS.get(form_type, FORM_FIELDS["general_purpose"])
    form_info=get_form_info(form_type)
    return render_template("form_fill.html", form_type=form_type, form_fields=form_fields,
                           autofill_data=AI_AUTOFILL, form_info=form_info, errors=[])

@app.route("/form/ai/autofill", methods=["POST"])
@login_required
def ai_autofill():
    import time; time.sleep(0.5)
    return jsonify({"fields":AI_AUTOFILL,"status":"ok","source":"AI + OCR"})

@app.route("/form/submit", methods=["POST"])
@login_required
def form_submit():
    email=session["user_email"]
    form_type=request.form.get("form_type", session.get("current_form_type","general_purpose"))
    form_fields=FORM_FIELDS.get(form_type, FORM_FIELDS["general_purpose"])
    data=request.form.to_dict(); data.pop("form_type",None)
    errors=[f"{f['label']} is required." for f in form_fields if f["type"] not in ["textarea"] and f["name"] in ["full_name","aadhaar_no"] and not data.get(f["name"],"").strip()]
    if errors:
        form_info=get_form_info(form_type)
        return render_template("form_fill.html", form_type=form_type, form_fields=form_fields,
                               autofill_data=data, form_info=form_info, errors=errors)
    session["review_data"]=data
    session["current_form_type"]=form_type
    return redirect(url_for("review_page"))

@app.route("/form/review", methods=["GET","POST"])
@login_required
def review_page():
    form_type=session.get("current_form_type","general_purpose")
    data=session.get("review_data",{})
    form_info=get_form_info(form_type)
    if request.method=="POST":
        email=session["user_email"]
        sub={"id":str(uuid.uuid4())[:8].upper(),"form_type":form_type,
             "form_name":form_info["label"],"form_icon":form_info["icon"],
             "form_color":form_info["color"],"data":data,
             "status":"Submitted","submitted_at":now_str()}
        submissions[email].append(sub)
        session["last_sub_id"]=sub["id"]
        flash("Form submitted successfully!","success")
        return redirect(url_for("result_page"))
    return render_template("review.html", data=data, form_type=form_type, form_info=form_info)

@app.route("/result")
@login_required
def result_page():
    email=session["user_email"]
    sub_id=session.get("last_sub_id")
    sub=next((s for s in submissions.get(email,[]) if s["id"]==sub_id), None)
    form_type=session.get("current_form_type","general_purpose")
    return render_template("result.html", sub=sub, form_type=form_type)

# ── OUTPUT ROUTES ──────────────────────────────────────────────────────────────
@app.route("/output/download/pdf", methods=["POST"])
@login_required
def download_pdf():
    import json
    data=request.json or {}
    form_type=data.get("form_type","general_purpose")
    form_info=get_form_info(form_type)
    fields=data.get("fields",{})
    # Generate a simple text-based PDF (plain HTML served as .html for demo)
    lines=[f"FormAssist — {form_info['label']}\n","="*50+"\n",f"Generated: {now_str()}\n\n"]
    for k,v in fields.items():
        if v: lines.append(f"{k.replace('_',' ').title():<30}: {v}\n")
    lines.append("\n— FormAssist Watermark —\n")
    buf=io.BytesIO("".join(lines).encode())
    buf.seek(0)
    return send_file(buf, mimetype="text/plain", as_attachment=True, download_name="filled_form.txt")

@app.route("/output/download/zip")
@login_required
def download_zip():
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w") as zf:
        zf.writestr("README.txt",f"FormAssist — Compressed Documents\nGenerated: {now_str()}\n\nYour documents are compressed and ready to upload.")
        zf.writestr("placeholder.txt","Connect real file storage to include actual uploaded files.")
    buf.seek(0)
    return send_file(buf, mimetype="application/zip", as_attachment=True, download_name="formassist_documents.zip")

@app.route("/output/web-autofill", methods=["POST"])
@login_required
def web_autofill_route():
    body=request.json or {}
    url=body.get("url","")
    if not url: return jsonify({"success":False,"error":"No URL provided."})
    return jsonify({"success":True,"filled":["full_name","dob","aadhaar_no","pan_no","address","mobile","email","college_name","bank_account","ifsc_code"],"message":f"Selenium opened {url} and filled 10 fields."})

if __name__=="__main__":
    app.run(debug=True)
