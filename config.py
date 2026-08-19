import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///pdf_to_anything.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload configuration
    MAX_UPLOAD_SIZE_MB = int(os.getenv('MAX_UPLOAD_SIZE_MB', 500))
    MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    MAX_FILES_PER_UPLOAD = int(os.getenv('MAX_FILES_PER_UPLOAD', 50))
    MAX_PDF_PAGES = int(os.getenv('MAX_PDF_PAGES', 5000))
    
    # Folders
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'outputs')
    TEMP_FOLDER = os.getenv('TEMP_FOLDER', 'temp')
    
    # File retention
    FILE_RETENTION_HOURS = int(os.getenv('FILE_RETENTION_HOURS', 2))
    FILE_RETENTION_DELTA = timedelta(hours=FILE_RETENTION_HOURS)
    
    # OCR
    OCR_ENABLED = os.getenv('OCR_ENABLED', 'True') == 'True'
    OCR_LANGUAGE = os.getenv('OCR_LANGUAGE', 'eng')
    
    # Cleanup
    CLEANUP_INTERVAL_MINUTES = int(os.getenv('CLEANUP_INTERVAL_MINUTES', 30))
    AUTO_CLEANUP = os.getenv('AUTO_CLEANUP', 'True') == 'True'
    
    # API
    API_RATE_LIMIT = int(os.getenv('API_RATE_LIMIT', 100))
    API_RATE_LIMIT_WINDOW = int(os.getenv('API_RATE_LIMIT_WINDOW', 3600))
    
    # Performance
    WORKER_THREADS = int(os.getenv('WORKER_THREADS', 4))
    CONVERSION_TIMEOUT_SECONDS = int(os.getenv('CONVERSION_TIMEOUT_SECONDS', 300))
    
    # Admin
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin-password-please-change')
    
    # PWA
    PWA_ENABLED = os.getenv('PWA_ENABLED', 'True') == 'True'
    APP_NAME = os.getenv('APP_NAME', 'PDF to Anything')
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

def get_config():
    env = os.getenv('FLASK_ENV', 'production')
    if env == 'development':
        return DevelopmentConfig
    elif env == 'testing':
        return TestingConfig
    return ProductionConfig