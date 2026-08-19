from models import db, Setting
from datetime import datetime

class SettingsService:
    """Service for managing application settings"""
    
    DEFAULT_SETTINGS = {
        'app_name': ('PDF to Anything', 'string'),
        'app_description': ('Convert, edit, organize and extract data from PDF files.', 'string'),
        'max_upload_size_mb': ('500', 'int'),
        'max_files_per_upload': ('50', 'int'),
        'max_pdf_pages': ('5000', 'int'),
        'file_retention_hours': ('2', 'int'),
        'cleanup_interval_minutes': ('30', 'int'),
        'ocr_enabled': ('true', 'bool'),
        'ocr_language': ('eng', 'string'),
        'conversion_timeout_seconds': ('300', 'int'),
        'dark_mode_enabled': ('false', 'bool'),
    }
    
    @staticmethod
    def initialize_defaults():
        """Initialize default settings if they don't exist"""
        for key, (value, data_type) in SettingsService.DEFAULT_SETTINGS.items():
            if not Setting.query.filter_by(key=key).first():
                setting = Setting(key=key, value=value, data_type=data_type)
                db.session.add(setting)
        db.session.commit()
    
    @staticmethod
    def get(key, default=None):
        """Get a setting value"""
        setting = Setting.query.filter_by(key=key).first()
        if not setting:
            return default
        
        # Convert to appropriate type
        if setting.data_type == 'int':
            return int(setting.value) if setting.value else default
        elif setting.data_type == 'bool':
            return setting.value.lower() in ('true', '1', 'yes') if setting.value else default
        return setting.value
    
    @staticmethod
    def set(key, value, data_type='string', description=None):
        """Set a setting value"""
        setting = Setting.query.filter_by(key=key).first()
        if not setting:
            setting = Setting(key=key, value=str(value), data_type=data_type)
            db.session.add(setting)
        else:
            setting.value = str(value)
            setting.data_type = data_type
        
        if description:
            setting.description = description
        
        setting.updated_at = datetime.utcnow()
        db.session.commit()
        return setting
    
    @staticmethod
    def get_all():
        """Get all settings"""
        settings = Setting.query.all()
        return {s.key: s.value for s in settings}
    
    @staticmethod
    def delete(key):
        """Delete a setting"""
        setting = Setting.query.filter_by(key=key).first()
        if setting:
            db.session.delete(setting)
            db.session.commit()
            return True
        return False