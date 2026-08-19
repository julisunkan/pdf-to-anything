# PythonAnywhere deployment configuration

# Path to Flask app
PATH = '/home/julisunkan/pdf-to-anything'

# Virtual environment
VIRTUAL_ENV_PATH = '/home/julisunkan/.virtualenvs/pdf-to-anything'

# WSGI application entry point
import sys
import os

# Add project directory to path
project_home = '/home/julisunkan/pdf-to-anything'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Load environment variables
os.chdir(project_home)
from dotenv import load_dotenv
load_dotenv(os.path.join(project_home, '.env'))

# Import and create Flask app
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
