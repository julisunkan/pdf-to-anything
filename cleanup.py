#!/usr/bin/env python
"""Run cleanup manually"""

import os
import sys
from app import create_app
from services.cleanup_service import CleanupService

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        print("Running cleanup...")
        result = CleanupService.cleanup_expired_jobs()
        
        if result['success']:
            print(f"✓ Cleanup complete")
            print(f"  Files deleted: {result['files_deleted']}")
            print(f"  Jobs deleted: {result['jobs_deleted']}")
            print(f"  Space freed: {result['space_freed_bytes'] / 1024 / 1024:.2f} MB")
        else:
            print(f"✗ Cleanup failed: {result['error']}")
            sys.exit(1)
