from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from functools import wraps
from services.settings_service import SettingsService
from services.security_service import SecurityService
from services.job_service import JobService
from services.format_service import FormatService
from services.cleanup_service import CleanupService
from models import db, ConversionJob, SystemLog, FormatSetting
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def require_admin(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_authenticated'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def require_csrf():
    expected = session.get('csrf_token')
    supplied = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
    if not expected or not supplied or not __import__('hmac').compare_digest(expected, supplied):
        return jsonify({'success': False, 'error': 'Invalid security token'}), 403
    return None

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    if request.method == 'POST':
        csrf_error = require_csrf()
        if csrf_error:
            return csrf_error
        password = request.form.get('password')
        if SecurityService.verify_admin_password(
            password,
            current_app.config.get('ADMIN_PASSWORD'),
        ):
            session['admin_authenticated'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            return render_template('admin/login.html', error='Invalid password')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    session.pop('admin_authenticated', None)
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@require_admin
def dashboard():
    """Admin dashboard"""
    from sqlalchemy import func
    
    # Get statistics
    jobs_by_status = JobService.count_jobs_by_status()
    total_jobs = ConversionJob.query.count()
    completed_jobs = ConversionJob.query.filter_by(status='completed').count()
    failed_jobs = ConversionJob.query.filter_by(status='failed').count()
    
    # Storage usage
    storage_used = CleanupService.get_storage_usage()
    
    # Recent jobs
    recent_jobs = JobService.get_recent_jobs(limit=10)
    
    return render_template('admin/dashboard.html',
        jobs_by_status=jobs_by_status,
        total_jobs=total_jobs,
        completed_jobs=completed_jobs,
        failed_jobs=failed_jobs,
        storage_used=storage_used,
        recent_jobs=recent_jobs
    )

@admin_bp.route('/jobs')
@require_admin
def jobs():
    """Job management"""
    page = request.args.get('page', 1, type=int)
    jobs = ConversionJob.query.paginate(page=page, per_page=50)
    return render_template('admin/jobs.html', jobs=jobs)

@admin_bp.route('/jobs/<job_id>')
@require_admin
def job_detail(job_id):
    """Job detail page"""
    job = JobService.get_job(job_id)
    if not job:
        return render_template('admin/error.html', error='Job not found'), 404
    
    logs = JobService.get_job_logs(job_id)
    return render_template('admin/job_detail.html', job=job, logs=logs)

@admin_bp.route('/jobs/<job_id>/delete', methods=['POST'])
@require_admin
def delete_job(job_id):
    """Delete a job"""
    csrf_error = require_csrf()
    if csrf_error:
        return csrf_error
    JobService.delete_job(job_id)
    return redirect(url_for('admin.jobs'))

@admin_bp.route('/formats')
@require_admin
def formats():
    """Format management"""
    formats = FormatService.AVAILABLE_FORMATS
    format_settings = {}
    
    for fmt_name in formats.keys():
        fmt_setting = FormatSetting.query.filter_by(format_name=fmt_name).first()
        format_settings[fmt_name] = fmt_setting
    
    return render_template('admin/formats.html', formats=formats, format_settings=format_settings)

@admin_bp.route('/formats/<format_name>/toggle', methods=['POST'])
@require_admin
def toggle_format(format_name):
    """Toggle format availability"""
    csrf_error = require_csrf()
    if csrf_error:
        return csrf_error
    if format_name not in FormatService.AVAILABLE_FORMATS:
        return jsonify({'success': False, 'error': 'Unknown format'}), 404
    enabled = request.form.get('enabled') == 'true'
    
    if enabled:
        FormatService.enable_format(format_name)
    else:
        FormatService.disable_format(format_name)
    
    return jsonify({'success': True})

@admin_bp.route('/settings')
@require_admin
def settings():
    """Settings management"""
    settings = SettingsService.get_all()
    return render_template('admin/settings.html', settings=settings)

@admin_bp.route('/settings/update', methods=['POST'])
@require_admin
def update_settings():
    """Update settings"""
    try:
        csrf_error = require_csrf()
        if csrf_error:
            return csrf_error
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({'success': False, 'error': 'JSON object required'}), 400
        
        for key, value in data.items():
            SettingsService.set(key, value)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/cleanup/run', methods=['POST'])
@require_admin
def run_cleanup():
    """Run cleanup"""
    csrf_error = require_csrf()
    if csrf_error:
        return csrf_error
    result = CleanupService.cleanup_expired_jobs()
    return jsonify(result)

@admin_bp.route('/cleanup/logs')
@require_admin
def cleanup_logs():
    """View cleanup logs"""
    logs = CleanupService.get_cleanup_logs()
    return render_template('admin/cleanup_logs.html', logs=logs)

@admin_bp.route('/logs')
@require_admin
def view_logs():
    """View system logs"""
    page = request.args.get('page', 1, type=int)
    logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).paginate(page=page, per_page=100)
    return render_template('admin/logs.html', logs=logs)
