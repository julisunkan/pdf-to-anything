from flask import Blueprint, render_template, request, jsonify, current_app, send_file
from services.pdf_service import PDFService
from services.file_service import FileService
import os
import uuid
import io
import zipfile
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

        input_paths = []
        for file in files:
            upload = FileService.save_pdf(file)
            input_paths.append(str(upload['path']))

        output_folder = FileService.output_root()
        output_folder.mkdir(parents=True, exist_ok=True)
        output_path = output_folder / f'merged_{uuid.uuid4().hex}.pdf'
        if not PDFService.merge_pdfs(input_paths, output_path):
            return jsonify({'success': False, 'error': 'The PDF files could not be merged'}), 500

        response = send_file(output_path, as_attachment=True, download_name='merged.pdf')
        response.call_on_close(lambda: [os.unlink(path) for path in input_paths if os.path.exists(path)])
        return response
    except ValueError as error:
        for path in input_paths:
            if os.path.exists(path):
                os.unlink(path)
        return jsonify({'success': False, 'error': str(error)}), 400
    except Exception:
        current_app.logger.exception('PDF merge failed')
        for path in input_paths:
            if os.path.exists(path):
                os.unlink(path)
        return jsonify({'success': False, 'error': 'The PDFs could not be merged'}), 500

@tools_bp.route('/split')
def split():
    """PDF split tool"""
    return render_template('tools/split.html')

@tools_bp.route('/split', methods=['POST'])
def split_file():
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({'success': False, 'error': 'No PDF file provided'}), 400
        upload = FileService.save_pdf(file)
        temp_dir = current_app.config['TEMP_FOLDER']
        os.makedirs(temp_dir, exist_ok=True)
        paths = PDFService.split_pdf(str(upload['path']), temp_dir)
        if not paths:
            return jsonify({'success': False, 'error': 'The PDF could not be split'}), 400
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in paths:
                archive.write(path, arcname=os.path.basename(path))
        for path in paths:
            os.remove(path)
        upload['path'].unlink(missing_ok=True)
        buffer.seek(0)
        return send_file(
            buffer, mimetype='application/zip', as_attachment=True,
            download_name='split_pages.zip'
        )
    except ValueError as error:
        return jsonify({'success': False, 'error': str(error)}), 400
    except Exception:
        current_app.logger.exception('PDF split failed')
        return jsonify({'success': False, 'error': 'The PDF could not be split'}), 500

@tools_bp.route('/extract')
def extract():
    """Extract text/images tool"""
    return render_template('tools/extract.html')

@tools_bp.route('/compress')
def compress():
    """PDF compress tool"""
    return render_template('tools/compress.html')

@tools_bp.route('/compress', methods=['POST'])
def compress_file():
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({'success': False, 'error': 'No PDF file provided'}), 400
        upload = FileService.save_pdf(file)
        output_path = FileService.output_root() / f'compressed_{uuid.uuid4().hex}.pdf'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if not PDFService.rewrite_pdf(str(upload['path']), str(output_path)):
            return jsonify({'success': False, 'error': 'The PDF could not be compressed'}), 500
        upload['path'].unlink(missing_ok=True)
        return send_file(output_path, as_attachment=True, download_name='compressed.pdf')
    except ValueError as error:
        return jsonify({'success': False, 'error': str(error)}), 400
    except Exception:
        current_app.logger.exception('PDF compression failed')
        return jsonify({'success': False, 'error': 'The PDF could not be compressed'}), 500

@tools_bp.route('/extract-text', methods=['POST'])
def extract_text():
    """Extract text from PDF"""
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({'success': False, 'error': 'No PDF file provided'}), 400
        upload = FileService.save_pdf(file)
        try:
            text = PDFService.extract_text(upload['path'])
        finally:
            upload['path'].unlink(missing_ok=True)
        
        return jsonify({
            'success': True,
            'text': text
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception:
        current_app.logger.exception('PDF text extraction failed')
        return jsonify({'success': False, 'error': 'The PDF text could not be extracted'}), 500
