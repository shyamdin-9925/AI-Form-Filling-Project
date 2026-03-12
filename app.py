import os
from flask import Flask
from database.db import db
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp

# Backend Person 2 will add these imports later:
# from routes.form_routes import form_bp
# from routes.upload_routes import upload_bp

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize database
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

# Backend Person 2 will add these later:
# app.register_blueprint(form_bp, url_prefix='/form')
# app.register_blueprint(upload_bp, url_prefix='/upload')

# Create uploads and outputs folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database created successfully!")
    app.run(debug=True, port=5000)
