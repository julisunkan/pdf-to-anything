import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import get_config
from models import db
from datetime import timedelta

def create_app():
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(get_config())
    
    # Initialize database
    db.init_app(app)
    
    # Create upload directories
    for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], app.config['TEMP_FOLDER']]:
        os.makedirs(folder, exist_ok=True)
    
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Initialize default settings
        from services.settings_service import SettingsService
        SettingsService.initialize_defaults()
        
        # Initialize format settings
        from services.format_service import FormatService
        FormatService.initialize_formats()
    
    # Register blueprints
    from routes.main import main_bp
    from routes.upload import upload_bp
    from routes.convert import convert_bp
    from routes.tools import tools_bp
    from routes.admin import admin_bp
    from routes.api import api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(convert_bp)
    app.register_blueprint(tools_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Setup session
    app.permanent_session_lifetime = app.config['PERMANENT_SESSION_LIFETIME']
    
    @app.before_request
    def before_request():
        from flask import session
        session.permanent = True
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def server_error(e):
        return {'error': 'Server error'}, 500
    
    # Context processors
    @app.context_processor
    def inject_config():
        return {
            'app_name': app.config.get('APP_NAME', 'PDF to Anything'),
            'pwa_enabled': app.config.get('PWA_ENABLED', True)
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')