import os
import uuid
from pathlib import Path

from PyPDF2 import PdfReader
from werkzeug.utils import secure_filename
from flask import current_app


class FileService:
    """Safe storage and validation helpers for uploaded PDF files."""

    @staticmethod
    def upload_root():
        return Path(current_app.config["UPLOAD_FOLDER"]).resolve()

    @staticmethod
    def output_root():
        return Path(current_app.config["OUTPUT_FOLDER"]).resolve()

    @staticmethod
    def is_within(path, root):
        try:
            Path(path).resolve().relative_to(Path(root).resolve())
            return True
        except ValueError:
            return False

    @staticmethod
    def resolve_upload(upload_id):
        """Resolve an opaque upload identifier without accepting a raw path."""
        if not upload_id or Path(str(upload_id)).name != str(upload_id):
            return None
        candidate = (FileService.upload_root() / str(upload_id)).resolve()
        if not FileService.is_within(candidate, FileService.upload_root()):
            return None
        return candidate if candidate.is_file() else None

    @staticmethod
    def save_pdf(file_storage):
        filename = secure_filename(file_storage.filename or "")
        if not filename or not filename.lower().endswith(".pdf"):
            raise ValueError("Only PDF files are allowed")

        max_size = current_app.config["MAX_UPLOAD_SIZE_BYTES"]
        file_storage.stream.seek(0, os.SEEK_END)
        file_size = file_storage.stream.tell()
        file_storage.stream.seek(0)
        if file_size > max_size:
            raise ValueError(
                f"File exceeds maximum size of "
                f"{current_app.config['MAX_UPLOAD_SIZE_MB']}MB"
            )

        upload_root = FileService.upload_root()
        upload_root.mkdir(parents=True, exist_ok=True)
        upload_id = f"{uuid.uuid4().hex}_{filename}"
        path = (upload_root / upload_id).resolve()
        if not FileService.is_within(path, upload_root):
            raise ValueError("Invalid upload path")
        file_storage.save(path)

        try:
            page_count = FileService.pdf_page_count(path)
        except Exception:
            path.unlink(missing_ok=True)
            raise ValueError("The uploaded file is not a readable PDF")

        if page_count > current_app.config["MAX_PDF_PAGES"]:
            path.unlink(missing_ok=True)
            raise ValueError(
                f"PDF exceeds the maximum of "
                f"{current_app.config['MAX_PDF_PAGES']} pages"
            )

        return {
            "upload_id": upload_id,
            "filename": filename,
            "file_size": file_size,
            "page_count": page_count,
            "path": path,
        }

    @staticmethod
    def pdf_page_count(path):
        with open(path, "rb") as source:
            return len(PdfReader(source).pages)

    @staticmethod
    def validate_pdf_path(path):
        path = Path(path).resolve()
        if not FileService.is_within(path, FileService.upload_root()):
            raise ValueError("Invalid upload reference")
        if not path.is_file():
            raise ValueError("Uploaded file not found")
        if path.stat().st_size > current_app.config["MAX_UPLOAD_SIZE_BYTES"]:
            raise ValueError("Uploaded file exceeds the maximum size")
        pages = FileService.pdf_page_count(path)
        if pages > current_app.config["MAX_PDF_PAGES"]:
            raise ValueError("PDF exceeds the maximum page count")
        return pages