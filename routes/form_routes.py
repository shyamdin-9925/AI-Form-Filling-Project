import json
from flask import Blueprint, request, render_template, redirect, jsonify, session, url_for
from database.db import db
from database.user_model import User
from database.submission_model import Submission
from services.ai_service import get_autofill_suggestions
from services.form_mapping_service import get_form_fields, get_user_data
from services.validation_service import validate_step1

form_bp = Blueprint('form', __name__)


@form_bp.route('/fill/<form_type>')
def fill_form(form_type):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user          = User.query.get(session['user_id'])
    form_fields   = get_form_fields(form_type)
    user_dict     = get_user_data(user)
    autofill_data = get_autofill_suggestions(user_dict)
    return render_template('form_fill.html',
        form_fields   = form_fields,
        autofill_data = autofill_data,
        form_type     = form_type,
        user          = user)


@form_bp.route('/ai/autofill', methods=['POST'])
def autofill():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    user         = User.query.get(session['user_id'])
    user_dict    = get_user_data(user)
    suggestions  = get_autofill_suggestions(user_dict)
    return jsonify({'fields': suggestions})


@form_bp.route('/submit', methods=['POST'])
def submit_form():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    form_data = request.form.to_dict()
    errors    = validate_step1(form_data)
    if errors:
        form_fields = get_form_fields(form_data.get('form_type', 'scholarship'))
        return render_template('form_fill.html',
            form_fields   = form_fields,
            autofill_data = form_data,
            errors        = errors)
    new_submission = Submission(
        user_id   = session['user_id'],
        form_type = form_data.get('form_type', 'scholarship'),
        data_json = json.dumps(form_data)
    )
    db.session.add(new_submission)
    db.session.commit()
    return render_template('result.html', data=form_data)