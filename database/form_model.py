from database.db import db


class Form(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    form_type   = db.Column(db.String(50), nullable=False)
    form_name   = db.Column(db.String(100))
    description = db.Column(db.String(300))

    def __repr__(self):
        return f'<Form {self.form_type}>'