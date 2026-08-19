#!/bin/bash
# PythonAnywhere deployment setup script
# Run this script in PythonAnywhere bash console

echo "PDF to Anything - PythonAnywhere Setup"
echo "======================================"

# Set username - change this to your PythonAnywhere username
USERNAME="julisunkan"
DOMAIN="${USERNAME}.pythonanywhere.com"
PROJECT_DIR="/home/${USERNAME}/pdf-to-anything"
VENV_DIR="/home/${USERNAME}/.virtualenvs/pdf-to-anything"

echo "Setting up for user: $USERNAME"
echo "Project directory: $PROJECT_DIR"
echo "Virtual env: $VENV_DIR"

# Step 1: Clone repository
echo ""
echo "[1/6] Cloning repository..."
cd /home/${USERNAME}
if [ ! -d "pdf-to-anything" ]; then
    git clone https://github.com/${USERNAME}/pdf-to-anything.git
else
    echo "Repository already cloned"
fi

cd ${PROJECT_DIR}

# Step 2: Create virtual environment
echo ""
echo "[2/6] Creating virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    mkvirtualenv --python=/usr/bin/python3.10 pdf-to-anything
else
    echo "Virtual environment already exists"
fi

# Step 3: Activate and install dependencies
echo ""
echo "[3/6] Installing dependencies..."
source ${VENV_DIR}/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Step 4: Create .env file
echo ""
echo "[4/6] Creating .env file..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env file - EDIT THIS FILE WITH YOUR SETTINGS!"
else
    echo ".env file already exists"
fi

# Step 5: Initialize database
echo ""
echo "[5/6] Initializing database..."
python initialize.py

# Step 6: Setup directories
echo ""
echo "[6/6] Creating required directories..."
mkdir -p uploads outputs temp
chmod 755 uploads outputs temp

echo ""
echo "✓ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration:"
echo "   nano .env"
echo ""
echo "2. Set up web app in PythonAnywhere dashboard:"
echo "   - Add new web app"
echo "   - Framework: Manual configuration (Python)"
echo "   - Python version: 3.10"
echo "   - WSGI file: /home/${USERNAME}/pdf-to-anything/pythonanywhere_wsgi.py"
echo ""
echo "3. Configure static files:"
echo "   URL: /static/"
echo "   Directory: /home/${USERNAME}/pdf-to-anything/static"
echo ""
echo "4. Reload web app in dashboard"
echo ""
echo "Access your app at: https://${DOMAIN}"
