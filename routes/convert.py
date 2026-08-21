from flask import Blueprint, request, jsonify, current_app
from services.job_service import JobService
from services.format_service import FormatService
from converters.conversion_engine import ConversionEngine
import os
import threading
import zipfile

convert_bp = Blueprint('convert', __name__, url_prefix='/convert')

def run_conversion(app, job_id, formats):
    """Run conversion in background"""
    with app.app_context():
        ConversionEngine.convert_pdf(job_id, formats)

@convert_bp.route('/start', methods=['POST'])
def start_conversion():
    """Start a conversion job"""
    try:
        data = request.get_json()
        
        file_path = data.get('file_path')
        filename = data.get('filename')
        file_size = data.get('file_size')
        output_formats = data.get('formats', [])
        page_count = data.get('page_count', 0)
        
        # Validate
        if not file_path or not filename or not output_formats:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'File not found'}), 400
        
        # Check formats are enabled
        for fmt in output_formats:
            if not FormatService.is_format_enabled(fmt):
                return jsonify({'success': False, 'error': f'Format {fmt} is not available'}), 400
        
        # Create job
        job = JobService.create_job(filename, file_path, file_size, output_formats, page_count)
        
        # Start conversion in background
        app = current_app._get_current_object()
        thread = threading.Thread(target=run_conversion, args=(app, job.id, output_formats))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'job_id': job.id,
            'status': job.status
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@convert_bp.route('/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get job status"""
    try:
        job = JobService.get_job(job_id)
        if not job:
            return jsonify({'success': False, 'error': 'Job not found'}), 404
        
        return jsonify({
            'success': True,
            'job_id': job.id,
            'status': job.status,
            'progress': job.progress_percent,
            'outputs': [{
                'format': o.format_name,
                'filename': o.output_filename,
                'status': o.status
            } for o in job.outputs],
            'error': job.error_message
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@convert_bp.route('/download/<job_id>/<format_name>', methods=['GET'])
def download_output(job_id, format_name):
    """Download a single converted file"""
    try:
        from flask import send_file
        
        job = JobService.get_job(job_id)
        if not job:
            return jsonify({'success': False, 'error': 'Job not found'}), 404
        
        output = None
        for o in job.outputs:
            if o.format_name == format_name:
                output = o
                break
        
        if not output or not os.path.exists(output.output_file_path):
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        return send_file(output.output_file_path, as_attachment=True, download_name=output.output_filename)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@convert_bp.route('/download-zip/<job_id>', methods=['GET'])
def download_all(job_id):
    """Download all outputs as ZIP"""
    try:
        from flask import send_file
        import io
        
        job = JobService.get_job(job_id)
        if not job:
            return jsonify({'success': False, 'error': 'Job not found'}), 404
        
        if not job.outputs:
            return jsonify({'success': False, 'error': 'No outputs available'}), 404
        
        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for output in job.outputs:
                if os.path.exists(output.output_file_path):
                    zip_file.write(output.output_file_path, arcname=output.output_filename)
        
        zip_buffer.seek(0)
        return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name=f'conversion_{job_id}.zip')
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
