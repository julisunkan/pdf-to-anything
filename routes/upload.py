from flask import Blueprint, request, jsonify, current_app, send_file
import os
import uuid
from werkzeug.utils import secure_filename
from services.job_service import JobService
from services.pdf_service import PDFService
from services.format_service import FormatService

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/file', methods=['POST'])
def upload_file():
    """Handle single file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Only PDF files allowed'}), 400
        
        # Check file size
        max_size = current_app.config['MAX_UPLOAD_SIZE_BYTES']
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > max_size:
            return jsonify({'success': False, 'error': f'File exceeds maximum size of {current_app.config["MAX_UPLOAD_SIZE_MB"]}MB'}), 400
        
        # Save file
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(upload_folder, unique_filename)
        
        file.save(file_path)
        
        # Analyze PDF
        page_count = PDFService.get_page_count(file_path)
        has_text = PDFService.has_text(file_path)
        
        return jsonify({
            'success': True,
            'file_path': file_path,
            'filename': filename,
            'file_size': file_size,
            'page_count': page_count,
            'has_text': has_text
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@upload_bp.route('/files', methods=['POST'])
def upload_files():
    """Handle bulk file upload"""
    try:
        if 'files' not in request.files:
            return jsonify({'success': False, 'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        max_files = current_app.config['MAX_FILES_PER_UPLOAD']
        
        if len(files) > max_files:
            return jsonify({'success': False, 'error': f'Maximum {max_files} files allowed'}), 400
        
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        uploaded = []
        errors = []
        
        for file in files:
            try:
                if not allowed_file(file.filename):
                    errors.append({'file': file.filename, 'error': 'Invalid file type'})
                    continue
                
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)
                
                max_size = current_app.config['MAX_UPLOAD_SIZE_BYTES']
                if file_size > max_size:
                    errors.append({'file': file.filename, 'error': 'File too large'})
                    continue
                
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file_path = os.path.join(upload_folder, unique_filename)
                
                file.save(file_path)
                
                page_count = PDFService.get_page_count(file_path)
                has_text = PDFService.has_text(file_path)
                
                uploaded.append({
                    'file_path': file_path,
                    'filename': filename,
                    'file_size': file_size,
                    'page_count': page_count,
                    'has_text': has_text
                })
            except Exception as e:
                errors.append({'file': file.filename, 'error': str(e)})
        
        return jsonify({
            'success': len(uploaded) > 0,
            'uploaded': uploaded,
            'errors': errors
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
