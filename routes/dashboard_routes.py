from flask import Blueprint, render_template, session, redirect, url_for
from database.user_model import User
from database.submission_model import Submission

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user        = User.query.get(session['user_id'])
    submissions = Submission.query.filter_by(user_id=user.id).all()
    return render_template('dashboard.html',
        user        = user,
        submissions = submissions)

