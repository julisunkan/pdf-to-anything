import os
import uuid
from pathlib import Path
from converters.registry import get_converter
from services.job_service import JobService
from flask import current_app

class ConversionEngine:
    """Main conversion engine for processing PDF files"""
    
    @staticmethod
    def convert_pdf(job_id: str, formats: list) -> dict:
        """Convert PDF to multiple formats"""
        job = JobService.get_job(job_id)
        if not job:
            return {'success': False, 'error': 'Job not found'}
        
        try:
            JobService.update_job_status(job_id, 'processing', progress=5)
            
            results = {'success': True, 'outputs': [], 'failed': []}
            total_formats = len(formats)
            
            for idx, format_name in enumerate(formats):
                try:
                    # Get converter
                    converter = get_converter(format_name)
                    if not converter:
                        results['failed'].append({
                            'format': format_name,
                            'error': f'No converter available for {format_name}'
                        })
                        continue
                    
                    # Generate output filename
                    base_name = Path(job.original_filename).stem
                    extension = {
                        'pdf_compressed': 'pdf',
                        'pdf_optimized': 'pdf',
                        'pdf_a': 'pdf',
                        'pdf_searchable': 'pdf',
                    }.get(format_name, format_name)
                    output_filename = f"{base_name}.{extension}"
                    job_output_dir = os.path.join(
                        current_app.config['OUTPUT_FOLDER'], job.id
                    )
                    os.makedirs(job_output_dir, exist_ok=True)
                    output_path = os.path.join(job_output_dir, output_filename)
                    
                    # Convert
                    JobService.log(job_id, 'INFO', f'Converting to {format_name}...')
                    success = converter.convert(job.input_file_path, output_path)
                    
                    if success and os.path.exists(output_path):
                        file_size = os.path.getsize(output_path)
                        JobService.add_output(job_id, format_name, output_filename, output_path, file_size)
                        results['outputs'].append({
                            'format': format_name,
                            'filename': output_filename,
                            'path': output_path
                        })
                        JobService.log(job_id, 'INFO', f'Successfully converted to {format_name}')
                    else:
                        results['failed'].append({
                            'format': format_name,
                            'error': 'Conversion failed'
                        })
                        JobService.log(job_id, 'ERROR', f'Failed to convert to {format_name}')
                    
                    # Update progress
                    progress = 5 + int((idx + 1) / total_formats * 90)
                    JobService.update_job_status(job_id, 'processing', progress=progress)
                
                except Exception as e:
                    error_msg = f'Error converting to {format_name}: {str(e)}'
                    results['failed'].append({
                        'format': format_name,
                        'error': str(e)
                    })
                    JobService.log(job_id, 'ERROR', error_msg)
            
            # Update final status
            final_status = 'completed' if results['outputs'] else 'failed'
            error_msg = None if results['outputs'] else 'All conversions failed'
            JobService.update_job_status(job_id, final_status, error_msg, 100)
            
            return results
        
        except Exception as e:
            error_msg = f'Conversion engine error: {str(e)}'
            JobService.update_job_status(job_id, 'failed', error_msg)
            JobService.log(job_id, 'ERROR', error_msg)
            return {'success': False, 'error': str(e)}
