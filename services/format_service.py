from models import db, FormatSetting
import shutil

class FormatService:
    """Service for managing conversion formats"""
    
    AVAILABLE_FORMATS = {
        # Documents
        'docx': {'category': 'document', 'description': 'Word Document', 'icon': 'file-word'},
        'odt': {'category': 'document', 'description': 'OpenDocument Text', 'icon': 'file-text'},
        'rtf': {'category': 'document', 'description': 'Rich Text Format', 'icon': 'file-text'},
        'txt': {'category': 'document', 'description': 'Plain Text', 'icon': 'file-text'},
        'html': {'category': 'document', 'description': 'HTML', 'icon': 'code'},
        'markdown': {'category': 'document', 'description': 'Markdown', 'icon': 'markdown'},
        
        # Ebooks
        'epub': {'category': 'ebook', 'description': 'EPUB eBook', 'icon': 'book'},
        'mobi': {'category': 'ebook', 'description': 'Kindle MOBI', 'icon': 'book'},
        
        # Spreadsheets
        'xlsx': {'category': 'spreadsheet', 'description': 'Excel Spreadsheet', 'icon': 'file-excel'},
        'xls': {'category': 'spreadsheet', 'description': 'Excel 97-2003', 'icon': 'file-excel'},
        'csv': {'category': 'spreadsheet', 'description': 'CSV', 'icon': 'file-csv'},
        'ods': {'category': 'spreadsheet', 'description': 'OpenDocument Spreadsheet', 'icon': 'table'},
        
        # Presentations
        'pptx': {'category': 'presentation', 'description': 'PowerPoint', 'icon': 'presentation'},
        'odp': {'category': 'presentation', 'description': 'OpenDocument Presentation', 'icon': 'presentation'},
        
        # Images
        'jpg': {'category': 'image', 'description': 'JPEG Image', 'icon': 'image'},
        'png': {'category': 'image', 'description': 'PNG Image', 'icon': 'image'},
        'webp': {'category': 'image', 'description': 'WebP Image', 'icon': 'image'},
        'tiff': {'category': 'image', 'description': 'TIFF Image', 'icon': 'image'},
        'bmp': {'category': 'image', 'description': 'Bitmap Image', 'icon': 'image'},
        'svg': {'category': 'image', 'description': 'SVG Vector', 'icon': 'image'},
        
        # Structured Data
        'json': {'category': 'data', 'description': 'JSON', 'icon': 'code'},
        'xml': {'category': 'data', 'description': 'XML', 'icon': 'code'},
        'yaml': {'category': 'data', 'description': 'YAML', 'icon': 'code'},
        
        # PDF Tools
        'pdf_compressed': {'category': 'pdf_tool', 'description': 'Compressed PDF', 'icon': 'compress'},
        'pdf_optimized': {'category': 'pdf_tool', 'description': 'Optimized PDF', 'icon': 'optimize'},
        'pdf_a': {'category': 'pdf_tool', 'description': 'PDF/A (Archival)', 'icon': 'archive'},
        'pdf_searchable': {'category': 'pdf_tool', 'description': 'Searchable PDF', 'icon': 'search'},
    }
    
    @staticmethod
    def initialize_formats():
        """Initialize format settings if they don't exist"""
        for format_name, info in FormatService.AVAILABLE_FORMATS.items():
            if not FormatSetting.query.filter_by(format_name=format_name).first():
                # Check if dependencies are available
                is_available = FormatService.check_format_availability(format_name)
                
                fmt = FormatSetting(
                    format_name=format_name,
                    enabled=True,
                    description=info.get('description', ''),
                    is_available=is_available
                )
                db.session.add(fmt)
        db.session.commit()
    
    @staticmethod
    def check_format_availability(format_name):
        """Check if a format's dependencies are available"""
        dependencies = {
            'odt': ['libreoffice'],
            'rtf': ['libreoffice'],
            'mobi': ['calibre'],
            'odp': ['libreoffice'],
            'pdf_a': ['ghostscript'],
            'pdf_searchable': ['tesseract', 'ocrmypdf'],
        }
        
        required = dependencies.get(format_name, [])
        
        for dep in required:
            if not shutil.which(dep):
                return False
        
        return True
    
    @staticmethod
    def get_availability_message(format_name):
        """Get a message explaining format availability"""
        dependencies = {
            'odt': 'Requires LibreOffice',
            'rtf': 'Requires LibreOffice',
            'mobi': 'Requires Calibre',
            'odp': 'Requires LibreOffice',
            'pdf_a': 'Requires Ghostscript',
            'pdf_searchable': 'Requires Tesseract and OCRmyPDF',
        }
        
        if format_name in dependencies:
            if not FormatService.check_format_availability(format_name):
                return f"Not available: {dependencies[format_name]}"
        
        return "Available"
    
    @staticmethod
    def is_format_enabled(format_name):
        """Check if a format is enabled"""
        fmt = FormatSetting.query.filter_by(format_name=format_name).first()
        if not fmt:
            return True  # Default to enabled if not in database
        return fmt.enabled and fmt.is_available

    @staticmethod
    def get_format_settings():
        return {
            fmt.format_name: fmt
            for fmt in FormatSetting.query.order_by(FormatSetting.format_name).all()
        }
    
    @staticmethod
    def enable_format(format_name):
        """Enable a format"""
        fmt = FormatSetting.query.filter_by(format_name=format_name).first()
        if fmt:
            fmt.enabled = True
            db.session.commit()
    
    @staticmethod
    def disable_format(format_name):
        """Disable a format"""
        fmt = FormatSetting.query.filter_by(format_name=format_name).first()
        if fmt:
            fmt.enabled = False
            db.session.commit()
    
    @staticmethod
    def get_available_formats():
        """Get all available formats grouped by category"""
        enabled_formats = FormatSetting.query.filter_by(enabled=True).all()
        enabled_names = {f.format_name for f in enabled_formats if f.is_available}
        
        grouped = {}
        for format_name, info in FormatService.AVAILABLE_FORMATS.items():
            if format_name in enabled_names:
                category = info.get('category', 'other')
                if category not in grouped:
                    grouped[category] = []
                grouped[category].append({
                    'name': format_name,
                    'description': info.get('description', ''),
                    'icon': info.get('icon', 'file'),
                    'category': category
                })
        
        return grouped