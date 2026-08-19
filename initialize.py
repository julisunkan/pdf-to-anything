#!/usr/bin/env python
"""Initialize the application and database"""

import os
import sys
from app import create_app
from models import db
from services.settings_service import SettingsService
from services.format_service import FormatService

if __name__ == '__main__':
    print("Initializing PDF to Anything...")
    
    # Create app
    app = create_app()
    
    with app.app_context():
        # Create database
        print("Creating database tables...")
        db.create_all()
        
        # Initialize settings
        print("Initializing settings...")
        SettingsService.initialize_defaults()
        
        # Initialize formats
        print("Checking available formats...")
        FormatService.initialize_formats()
        
        print("\n✓ Initialization complete!")
        print("\nNext steps:")
        print("1. Configure .env with admin password")
        print("2. Run: python app.py")
        print("3. Access: http://localhost:5000")
        print("4. Admin panel: http://localhost:5000/admin")
