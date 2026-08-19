#!/bin/bash
# Scheduled cleanup script for PythonAnywhere
# Add this as a PythonAnywhere scheduled task

USERNAME="julisunkan"
PROJECT_DIR="/home/${USERNAME}/pdf-to-anything"
VENV_DIR="/home/${USERNAME}/.virtualenvs/pdf-to-anything"

cd ${PROJECT_DIR}
source ${VENV_DIR}/bin/activate

# Run cleanup
python cleanup.py

# Log cleanup execution
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cleanup executed" >> cleanup_log.txt
