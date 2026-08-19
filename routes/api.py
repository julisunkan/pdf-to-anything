from flask import Blueprint, request, jsonify, current_app, send_file
from functools import wraps
from models import db, APIKey
import hashlib
import hmac
import os
import io
import zipfile
from services.job_service import JobService
from services.format_service import FormatService
from converters.conversion_engine import ConversionEngine
import threading

api_bp = Blueprint('api', __name__)

def verify_api_key(f):
    """Decorator to verify API key"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Hash the provided key and check against stored hash
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        api_key_obj = APIKey.query.filter_by(key_hash=key_hash, is_active=True).first()
        
        if not api_key_obj:
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@api_bp.route('/convert', methods=['POST'])
@verify_api_key
def convert():
    """Convert PDF via API"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        formats = request.form.getlist('formats')
        
        if not formats:
            return jsonify({'error': 'No formats specified'}), 400
        
        # Upload file
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        import uuid
        from werkzeug.utils import secure_filename
        
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        file_size = os.path.getsize(file_path)
        
        # Create job
        from services.pdf_service import PDFService
        page_count = PDFService.get_page_count(file_path)
        job = JobService.create_job(filename, file_path, file_size, formats, page_count)
        
        # Start conversion
        thread = threading.Thread(target=ConversionEngine.convert_pdf, args=(job.id, formats))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'job_id': job.id,
            'status': 'queued',
            'formats': formats
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/jobs/<job_id>', methods=['GET'])
@verify_api_key
def get_job(job_id):
    """Get job status"""
    try:
        job = JobService.get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify({
            'job_id': job.id,
            'status': job.status,
            'progress': job.progress_percent,
            'outputs': [{
                'format': o.format_name,
                'filename': o.output_filename,
                'status': o.status
            } for o in job.outputs],
            'created_at': job.created_at.isoformat(),
            'updated_at': job.updated_at.isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/jobs/<job_id>/download/<format_name>', methods=['GET'])
@verify_api_key
def download_format(job_id, format_name):
    """Download specific format"""
    try:
        job = JobService.get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        output = None
        for o in job.outputs:
            if o.format_name == format_name:
                output = o
                break
        
        if not output or not os.path.exists(output.output_file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(output.output_file_path, as_attachment=True, download_name=output.output_filename)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/jobs/<job_id>/download', methods=['GET'])
@verify_api_key
def download_all_formats(job_id):
    """Download all formats as ZIP"""
    try:
        job = JobService.get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        if not job.outputs:
            return jsonify({'error': 'No outputs available'}), 404
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for output in job.outputs:
                if os.path.exists(output.output_file_path):
                    zip_file.write(output.output_file_path, arcname=output.output_filename)
        
        zip_buffer.seek(0)
        return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name=f'conversion_{job_id}.zip')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/formats', methods=['GET'])
@verify_api_key
def list_formats():
    """List available formats"""
    try:
        formats = FormatService.get_available_formats()
        return jsonify(formats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
