from flask import Blueprint, request, jsonify, current_app
from services.pdf_service import PDFService
from services.file_service import FileService

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
        
        upload = FileService.save_pdf(file)
        has_text = PDFService.has_text(upload['path'])
        
        return jsonify({
            'success': True,
            'upload_id': upload['upload_id'],
            'filename': upload['filename'],
            'file_size': upload['file_size'],
            'page_count': upload['page_count'],
            'has_text': has_text
        })
    
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception:
        current_app.logger.exception('PDF upload failed')
        return jsonify({'success': False, 'error': 'The PDF could not be uploaded'}), 500

@upload_bp.route('/files', methods=['POST'])
def upload_files():
    """Handle bulk file upload"""
    try:
        if 'files' not in request.files:
            return jsonify({'success': False, 'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        max_files = current_app.config['MAX_FILES_PER_UPLOAD']
        
        if not files:
            return jsonify({'success': False, 'error': 'No files selected'}), 400
        if len(files) > max_files:
            return jsonify({'success': False, 'error': f'Maximum {max_files} files allowed'}), 400
        
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        uploaded = []
        errors = []
        
        for file in files:
            try:
                upload = FileService.save_pdf(file)
                has_text = PDFService.has_text(upload['path'])
                
                uploaded.append({
                    'upload_id': upload['upload_id'],
                    'filename': upload['filename'],
                    'file_size': upload['file_size'],
                    'page_count': upload['page_count'],
                    'has_text': has_text
                })
            except Exception as e:
                errors.append({'file': file.filename, 'error': str(e)})
        
        return jsonify({
            'success': len(uploaded) > 0,
            'uploaded': uploaded,
            'errors': errors
        })
    
    except Exception:
        current_app.logger.exception('Bulk PDF upload failed')
        return jsonify({'success': False, 'error': 'The PDFs could not be uploaded'}), 500
