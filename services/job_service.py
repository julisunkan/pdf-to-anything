from models import db, ConversionJob, ConversionOutput, JobLog
from datetime import datetime, timedelta
import uuid
import os
from flask import current_app

class JobService:
    """Service for managing conversion jobs"""
    
    @staticmethod
    def create_job(filename, file_path, file_size, output_formats, page_count=0, selected_pages=None):
        """Create a new conversion job"""
        job_id = str(uuid.uuid4())
        
        # Calculate expiration time
        retention_hours = current_app.config['FILE_RETENTION_HOURS']
        expires_at = datetime.utcnow() + timedelta(hours=retention_hours)
        
        # Convert formats list to CSV string
        if isinstance(output_formats, list):
            formats_str = ','.join(output_formats)
        else:
            formats_str = output_formats
        
        job = ConversionJob(
            id=job_id,
            original_filename=filename,
            input_file_path=file_path,
            file_size=file_size,
            page_count=page_count,
            output_formats=formats_str,
            selected_pages=selected_pages,
            expires_at=expires_at,
            status='queued'
        )
        
        db.session.add(job)
        db.session.commit()
        
        JobService.log(job_id, 'INFO', f'Job created: {filename} -> {formats_str}')
        
        return job
    
    @staticmethod
    def get_job(job_id):
        """Get a job by ID"""
        return ConversionJob.query.filter_by(id=job_id).first()
    
    @staticmethod
    def update_job_status(job_id, status, error_message=None, progress=0):
        """Update job status"""
        job = JobService.get_job(job_id)
        if job:
            job.status = status
            job.progress_percent = progress
            if error_message:
                job.error_message = error_message
            job.updated_at = datetime.utcnow()
            db.session.commit()
            return job
        return None
    
    @staticmethod
    def add_output(job_id, format_name, output_filename, output_path, file_size=0):
        """Add a converted output to a job"""
        output = ConversionOutput(
            job_id=job_id,
            format_name=format_name,
            output_filename=output_filename,
            output_file_path=output_path,
            file_size=file_size,
            status='completed'
        )
        
        db.session.add(output)
        db.session.commit()
        return output
    
    @staticmethod
    def mark_output_failed(job_id, format_name, error_message):
        """Mark an output as failed"""
        output = ConversionOutput.query.filter_by(
            job_id=job_id,
            format_name=format_name
        ).first()
        
        if output:
            output.status = 'failed'
            output.error_message = error_message
            db.session.commit()
    
    @staticmethod
    def log(job_id, level, message):
        """Log a message for a job"""
        log = JobLog(
            job_id=job_id,
            level=level,
            message=message
        )
        db.session.add(log)
        db.session.commit()
    
    @staticmethod
    def get_job_logs(job_id):
        """Get all logs for a job"""
        return JobLog.query.filter_by(job_id=job_id).order_by(JobLog.timestamp).all()
    
    @staticmethod
    def get_active_jobs(limit=50):
        """Get active/queued jobs"""
        return ConversionJob.query.filter(
            ConversionJob.status.in_(['queued', 'processing'])
        ).order_by(ConversionJob.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_recent_jobs(limit=50):
        """Get recent jobs"""
        return ConversionJob.query.order_by(ConversionJob.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_failed_jobs(limit=50):
        """Get failed jobs"""
        return ConversionJob.query.filter_by(status='failed').order_by(
            ConversionJob.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def count_jobs_by_status():
        """Count jobs by status"""
        from sqlalchemy import func
        
        results = db.session.query(
            ConversionJob.status,
            func.count(ConversionJob.id).label('count')
        ).group_by(ConversionJob.status).all()
        
        return {status: count for status, count in results}
    
    @staticmethod
    def get_total_size_processed():
        """Get total size of all processed files in bytes"""
        from sqlalchemy import func
        
        result = db.session.query(
            func.sum(ConversionJob.file_size).label('total')
        ).filter(ConversionJob.status == 'completed').first()
        
        return result.total or 0 if result else 0
    
    @staticmethod
    def delete_job(job_id):
        """Delete a job and its files"""
        job = JobService.get_job(job_id)
        if not job:
            return False
        
        # Delete output files
        for output in job.outputs:
            if os.path.exists(output.output_file_path):
                try:
                    os.remove(output.output_file_path)
                except Exception as e:
                    print(f"Error deleting {output.output_file_path}: {e}")
        
        # Delete input file
        if os.path.exists(job.input_file_path):
            try:
                os.remove(job.input_file_path)
            except Exception as e:
                print(f"Error deleting {job.input_file_path}: {e}")
        
        # Delete ZIP if it exists
        if job.output_zip_path and os.path.exists(job.output_zip_path):
            try:
                os.remove(job.output_zip_path)
            except Exception as e:
                print(f"Error deleting {job.output_zip_path}: {e}")
        
        # Delete from database
        db.session.delete(job)
        db.session.commit()
        
        return True