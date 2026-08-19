#!/bin/bash
# Quick PythonAnywhere deployment script
# Run this in PythonAnywhere bash console with your username

if [ -z "$1" ]; then
    echo "Usage: bash pythonanywhere_quick_setup.sh YOUR_USERNAME"
    exit 1
fi

USERNAME=$1
echo "Installing PDF to Anything for $USERNAME..."

# Change to home
cd /home/$USERNAME

# Clone if needed
if [ ! -d "pdf-to-anything" ]; then
    git clone https://github.com/$USERNAME/pdf-to-anything.git
fi

cd pdf-to-anything

# Create virtualenv if needed
if [ ! -d "/home/$USERNAME/.virtualenvs/pdf-to-anything" ]; then
    mkvirtualenv --python=/usr/bin/python3.10 pdf-to-anything
fi

# Activate and install
source /home/$USERNAME/.virtualenvs/pdf-to-anything/bin/activate
pip install -r requirements.txt

# Create .env
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env - you must edit this file!"
fi

# Init database
python initialize.py

# Create directories
mkdir -p uploads outputs temp

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next:"
echo "1. Edit .env file"
echo "2. Set up web app in dashboard (manual Python 3.10)"
echo "3. WSGI file: /home/$USERNAME/pdf-to-anything/pythonanywhere_wsgi.py"
echo "4. Virtualenv: /home/$USERNAME/.virtualenvs/pdf-to-anything"
echo "5. Static files: /static/ → /home/$USERNAME/pdf-to-anything/static"
echo "6. Click Reload"
