import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY                     = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI        = 'sqlite:///formassist.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER                  = 'uploads/'
    OUTPUT_FOLDER                  = 'outputs/'
    MAX_CONTENT_LENGTH             = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS             = {'pdf', 'jpg', 'jpeg', 'png'}
