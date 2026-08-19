import os
import shutil
from datetime import datetime, timedelta
from models import db, ConversionJob, CleanupLog
from flask import current_app

class CleanupService:
    """Service for cleaning up expired files and jobs"""
    
    @staticmethod
    def cleanup_expired_jobs():
        """Delete expired jobs and their files"""
        try:
            now = datetime.utcnow()
            expired_jobs = ConversionJob.query.filter(
                ConversionJob.expires_at <= now
            ).all()
            
            files_deleted = 0
            jobs_deleted = 0
            space_freed = 0
            
            for job in expired_jobs:
                # Get total size before deletion
                job_size = job.file_size or 0
                
                # Delete output files
                for output in job.outputs:
                    if os.path.exists(output.output_file_path):
                        try:
                            size = os.path.getsize(output.output_file_path)
                            os.remove(output.output_file_path)
                            files_deleted += 1
                            space_freed += size
                        except Exception as e:
                            print(f"Error deleting {output.output_file_path}: {e}")
                
                # Delete input file
                if os.path.exists(job.input_file_path):
                    try:
                        size = os.path.getsize(job.input_file_path)
                        os.remove(job.input_file_path)
                        files_deleted += 1
                        space_freed += size
                    except Exception as e:
                        print(f"Error deleting {job.input_file_path}: {e}")
                
                # Delete ZIP if it exists
                if job.output_zip_path and os.path.exists(job.output_zip_path):
                    try:
                        size = os.path.getsize(job.output_zip_path)
                        os.remove(job.output_zip_path)
                        files_deleted += 1
                        space_freed += size
                    except Exception as e:
                        print(f"Error deleting {job.output_zip_path}: {e}")
                
                # Delete from database
                db.session.delete(job)
                jobs_deleted += 1
            
            db.session.commit()
            
            # Log cleanup operation
            log = CleanupLog(
                files_deleted=files_deleted,
                jobs_deleted=jobs_deleted,
                space_freed_bytes=space_freed,
                status='success',
                message=f'Deleted {jobs_deleted} jobs, {files_deleted} files, freed {space_freed} bytes'
            )
            db.session.add(log)
            db.session.commit()
            
            return {
                'success': True,
                'files_deleted': files_deleted,
                'jobs_deleted': jobs_deleted,
                'space_freed_bytes': space_freed
            }
        
        except Exception as e:
            log = CleanupLog(
                status='failed',
                message=f'Cleanup failed: {str(e)}'
            )
            db.session.add(log)
            db.session.commit()
            
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def cleanup_orphaned_files():
        """Clean up files that don't belong to any job"""
        try:
            space_freed = 0
            files_deleted = 0
            
            # Check upload folder
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if os.path.exists(upload_folder):
                for filename in os.listdir(upload_folder):
                    file_path = os.path.join(upload_folder, filename)
                    if os.path.isfile(file_path):
                        # Check if this file belongs to a job
                        job = ConversionJob.query.filter_by(
                            input_file_path=file_path
                        ).first()
                        
                        if not job:
                            try:
                                size = os.path.getsize(file_path)
                                os.remove(file_path)
                                files_deleted += 1
                                space_freed += size
                            except Exception as e:
                                print(f"Error deleting orphaned file {file_path}: {e}")
            
            # Check output folder
            output_folder = current_app.config['OUTPUT_FOLDER']
            if os.path.exists(output_folder):
                for filename in os.listdir(output_folder):
                    file_path = os.path.join(output_folder, filename)
                    if os.path.isfile(file_path):
                        # Check if this file belongs to a job
                        from models import ConversionOutput
                        output = ConversionOutput.query.filter_by(
                            output_file_path=file_path
                        ).first()
                        
                        if not output:
                            try:
                                size = os.path.getsize(file_path)
                                os.remove(file_path)
                                files_deleted += 1
                                space_freed += size
                            except Exception as e:
                                print(f"Error deleting orphaned file {file_path}: {e}")
            
            return {
                'success': True,
                'files_deleted': files_deleted,
                'space_freed_bytes': space_freed
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_storage_usage():
        """Get current storage usage"""
        total_size = 0
        
        for folder in [current_app.config['UPLOAD_FOLDER'], 
                       current_app.config['OUTPUT_FOLDER'],
                       current_app.config['TEMP_FOLDER']]:
            if os.path.exists(folder):
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            total_size += os.path.getsize(file_path)
                        except Exception:
                            pass
        
        return total_size
    
    @staticmethod
    def get_cleanup_logs(limit=50):
        """Get cleanup operation logs"""
        return CleanupLog.query.order_by(CleanupLog.timestamp.desc()).limit(limit).all()