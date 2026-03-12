from flask import Blueprint, request, render_template, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import db
from database.user_model import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name     = request.form.get('name')
        email    = request.form.get('email')
        password = request.form.get('password')
        existing = User.query.filter_by(email=email).first()
        if existing:
            return render_template('signup.html', error='Email already registered')
        hashed   = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')
        user     = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id']   = user.id
            session['user_name'] = user.name
            return redirect(url_for('dashboard.index'))
        return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))