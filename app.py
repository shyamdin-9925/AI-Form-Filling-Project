import os
from flask import Flask
from database.db import db
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.form_routes import form_bp
from routes.upload_routes import upload_bp
from routes.output_routes import output_bp

app = Flask(__name__)
app.config.from_object('config.Config')

db.init_app(app)

app.register_blueprint(auth_bp,      url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(form_bp,      url_prefix='/form')
app.register_blueprint(upload_bp,    url_prefix='/upload')
app.register_blueprint(output_bp,    url_prefix='/output')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database created successfully!")
    app.run(debug=True, port=5000)
