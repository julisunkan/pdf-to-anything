# Production settings for PythonAnywhere
# Source this before deploying to ensure production configuration

import os
from pathlib import Path

print("PDF to Anything - Production Configuration Check")
print("================================================\n")

project_dir = Path(__file__).parent
env_file = project_dir / '.env'

if not env_file.exists():
    print("❌ .env file not found!")
    print(f"   Please create: {env_file}")
    exit(1)

print("✓ .env file found\n")

# Read environment
from dotenv import dotenv_values
config = dotenv_values(str(env_file))

# Check critical settings
print("Checking critical settings:\n")

checks = [
    ('FLASK_ENV', 'production', 'Environment'),
    ('DEBUG', 'False', 'Debug mode'),
    ('SECRET_KEY', None, 'Secret key'),
    ('ADMIN_PASSWORD', None, 'Admin password'),
]

issues = 0

for key, expected, description in checks:
    value = config.get(key, '')
    
    if not value:
        print(f"❌ {description}: NOT SET")
        issues += 1
    elif expected and value != expected:
        print(f"⚠️  {description}: {value} (expected: {expected})")
        issues += 1
    else:
        if key in ['SECRET_KEY', 'ADMIN_PASSWORD']:
            print(f"✓ {description}: Set (hidden)")
        else:
            print(f"✓ {description}: {value}")

# Check database location
db_location = config.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///pdf_to_anything.db')
if '/home/' not in db_location and 'sqlite' in db_location:
    print(f"⚠️  Database location might not persist: {db_location}")
    issues += 1
else:
    print(f"✓ Database location: {db_location[:50]}...")

# Check upload directories
print(f"\nChecking directories:\n")
for dir_name in ['uploads', 'outputs', 'temp']:
    dir_path = project_dir / dir_name
    if dir_path.exists():
        print(f"✓ {dir_name}: Exists")
    else:
        print(f"⚠️  {dir_name}: Missing (will be created on first use)")

print(f"\n{'='*50}\n")

if issues > 0:
    print(f"❌ {issues} issue(s) found. Please fix before deploying.")
    exit(1)
else:
    print("✅ All checks passed! Ready for deployment.")
