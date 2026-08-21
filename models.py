from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class ConversionJob(db.Model):
    """Represents a PDF conversion job"""
    __tablename__ = 'conversion_jobs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Job metadata
    job_name = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='queued', nullable=False)  # queued, processing, completed, failed, cancelled
    progress_percent = db.Column(db.Integer, default=0)
    
    # File information
    original_filename = db.Column(db.String(255), nullable=False)
    input_file_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.Integer)  # in bytes
    page_count = db.Column(db.Integer, default=0)
    
    # Conversion options
    output_formats = db.Column(db.String(1000), nullable=False)  # CSV: docx,xlsx,json
    selected_pages = db.Column(db.String(1000), nullable=True)  # e.g., "1-5,10,15-20"
    
    # Results
    output_zip_path = db.Column(db.String(512), nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    
    # Expiration
    expires_at = db.Column(db.DateTime, nullable=False)
    
    outputs = db.relationship('ConversionOutput', backref='job', lazy=True, cascade='all, delete-orphan')
    logs = db.relationship('JobLog', backref='job', lazy=True, cascade='all, delete-orphan')

class ConversionOutput(db.Model):
    """Represents a single converted output file"""
    __tablename__ = 'conversion_outputs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = db.Column(db.String(36), db.ForeignKey('conversion_jobs.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # File information
    format_name = db.Column(db.String(50), nullable=False)  # docx, xlsx, json, etc.
    output_filename = db.Column(db.String(255), nullable=False)
    output_file_path = db.Column(db.String(512), nullable=False)
    file_size = db.Column(db.Integer)  # in bytes
    
    # Status
    status = db.Column(db.String(50), default='pending', nullable=False)  # pending, completed, failed
    error_message = db.Column(db.Text, nullable=True)

class JobLog(db.Model):
    """Logs for conversion jobs"""
    __tablename__ = 'job_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = db.Column(db.String(36), db.ForeignKey('conversion_jobs.id'), nullable=False)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    level = db.Column(db.String(20), nullable=False)  # DEBUG, INFO, WARNING, ERROR
    message = db.Column(db.Text, nullable=False)

class Setting(db.Model):
    """Application settings"""
    __tablename__ = 'settings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key = db.Column(db.String(255), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(500), nullable=True)
    data_type = db.Column(db.String(50), default='string')  # string, int, bool, json
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SecurityCredential(db.Model):
    """Bootstrap credentials kept separate from user-facing application settings."""
    __tablename__ = 'security_credentials'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class FormatSetting(db.Model):
    """Settings for individual conversion formats"""
    __tablename__ = 'format_settings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    format_name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    enabled = db.Column(db.Boolean, default=True)
    description = db.Column(db.String(500), nullable=True)
    
    # Dependency info
    dependencies = db.Column(db.String(500), nullable=True)  # e.g., "tesseract,libreoffice"
    is_available = db.Column(db.Boolean, default=True)
    availability_message = db.Column(db.String(500), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Preset(db.Model):
    """Conversion presets"""
    __tablename__ = 'presets'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    
    # Formats CSV
    output_formats = db.Column(db.String(1000), nullable=False)
    
    # Options
    icon = db.Column(db.String(50), nullable=True)
    category = db.Column(db.String(100), nullable=True)  # document, ebook, spreadsheet, image, data, pdf_tool
    
    is_system = db.Column(db.Boolean, default=False)  # System presets cannot be deleted
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SystemLog(db.Model):
    """System and application logs"""
    __tablename__ = 'system_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    level = db.Column(db.String(20), nullable=False)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    component = db.Column(db.String(100), nullable=False)  # cleanup, api, admin, converter, etc.
    message = db.Column(db.Text, nullable=False)

class APIKey(db.Model):
    """API keys for external access"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    key_hash = db.Column(db.String(255), unique=True, nullable=False, index=True)
    
    is_active = db.Column(db.Boolean, default=True)
    rate_limit = db.Column(db.Integer, default=100)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime, nullable=True)

class CleanupLog(db.Model):
    """Records of cleanup operations"""
    __tablename__ = 'cleanup_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    files_deleted = db.Column(db.Integer, default=0)
    jobs_deleted = db.Column(db.Integer, default=0)
    space_freed_bytes = db.Column(db.Integer, default=0)
    
    status = db.Column(db.String(50), default='success')  # success, partial, failed
    message = db.Column(db.Text, nullable=True)