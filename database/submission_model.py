from database.db import db
from datetime import datetime


class Submission(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('user.id'))
    form_type    = db.Column(db.String(50))
    data_json    = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    status       = db.Column(db.String(20), default='Submitted')

    def __repr__(self):
        return f'<Submission {self.id}>'


