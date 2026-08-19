from flask import Blueprint, render_template, request, jsonify, current_app
from services.pdf_service import PDFService
import os

tools_bp = Blueprint('tools', __name__, url_prefix='/tools')

@tools_bp.route('/merge')
def merge():
    """PDF merge tool"""
    return render_template('tools/merge.html')

@tools_bp.route('/split')
def split():
    """PDF split tool"""
    return render_template('tools/split.html')

@tools_bp.route('/extract')
def extract():
    """Extract text/images tool"""
    return render_template('tools/extract.html')

@tools_bp.route('/compress')
def compress():
    """PDF compress tool"""
    return render_template('tools/compress.html')

@tools_bp.route('/extract-text', methods=['POST'])
def extract_text():
    """Extract text from PDF"""
    try:
        file_path = request.form.get('file_path')
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found'}), 400
        
        text = PDFService.extract_text(file_path)
        
        return jsonify({
            'success': True,
            'text': text
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
