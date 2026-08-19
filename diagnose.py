#!/usr/bin/env python
"""Diagnostic script to check system dependencies"""

import sys
import shutil
from importlib import import_module

print("PDF to Anything - System Diagnostics")
print("====================================\n")

# Python version
print(f"Python: {sys.version}")

# Python packages
print("\nPython Packages:")
required_packages = [
    'flask',
    'flask_sqlalchemy',
    'sqlalchemy',
    'PyPDF2',
    'pdf2docx',
    'pdfplumber',
    'PIL',
    'docx',
    'openpyxl',
    'markdown',
    'yaml',
    'lxml',
    'ebooklib',
]

for package in required_packages:
    try:
        import_module(package if package != 'PIL' else 'PIL')
        print(f"  ✓ {package}")
    except ImportError:
        print(f"  ✗ {package} (MISSING)")

# System dependencies
print("\nSystem Dependencies:")
system_deps = [
    ('tesseract', 'Tesseract OCR'),
    ('libreoffice', 'LibreOffice'),
    ('ghostscript', 'Ghostscript'),
    ('pdftoppm', 'Poppler'),
    ('calibre', 'Calibre'),
]

for cmd, name in system_deps:
    if shutil.which(cmd):
        print(f"  ✓ {name}")
    else:
        print(f"  ✗ {name} (MISSING - optional)")

print("\n✓ Diagnostic complete")
