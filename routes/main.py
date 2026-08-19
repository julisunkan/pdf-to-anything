from flask import Blueprint, render_template, current_app
from services.format_service import FormatService
from services.job_service import JobService

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page"""
    available_formats = FormatService.get_available_formats()
    return render_template('index.html', formats=available_formats)

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@main_bp.route('/privacy')
def privacy():
    """Privacy page"""
    return render_template('privacy.html')

@main_bp.route('/faq')
def faq():
    """FAQ page"""
    return render_template('faq.html')
