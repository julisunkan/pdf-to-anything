from flask import Blueprint, render_template, request, jsonify, current_app, send_file
from services.pdf_service import PDFService
import os
import uuid
from werkzeug.utils import secure_filename

tools_bp = Blueprint('tools', __name__, url_prefix='/tools')

@tools_bp.route('/merge')
def merge():
    """PDF merge tool"""
    return render_template('tools/merge.html')

@tools_bp.route('/merge', methods=['POST'])
def merge_files():
    """Merge uploaded PDF files in the order they were selected."""
    try:
        files = request.files.getlist('files')
        files = [file for file in files if file and file.filename]
        if len(files) < 2:
            return jsonify({'success': False, 'error': 'Select at least two PDF files'}), 400

        upload_folder = current_app.config['UPLOAD_FOLDER']
        output_folder = current_app.config['OUTPUT_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)

        input_paths = []
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                return jsonify({'success': False, 'error': 'Only PDF files are allowed'}), 400
            filename = secure_filename(file.filename)
            input_path = os.path.join(upload_folder, f'{uuid.uuid4().hex}_{filename}')
            file.save(input_path)
            input_paths.append(input_path)

        output_path = os.path.join(output_folder, f'merged_{uuid.uuid4().hex}.pdf')
        if not PDFService.merge_pdfs(input_paths, output_path):
            return jsonify({'success': False, 'error': 'The PDF files could not be merged'}), 500

        return send_file(output_path, as_attachment=True, download_name='merged.pdf')
    except Exception as e:
        current_app.logger.exception('PDF merge failed')
        return jsonify({'success': False, 'error': str(e)}), 500

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
