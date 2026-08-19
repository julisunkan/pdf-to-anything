# PDF to Anything

A production-ready, modular web application for PDF processing and conversion.

## Features

- **25+ Output Formats**: DOCX, XLSX, PNG, JPEG, EPUB, HTML, JSON, XML, and more
- **Anonymous Processing**: No registration or login required
- **Bulk Conversion**: Convert multiple PDFs at once
- **Multiple Output Formats**: Convert one PDF to multiple formats simultaneously
- **PDF Tools**: Merge, split, extract, rotate, compress
- **OCR Support**: Convert scanned PDFs to searchable documents
- **Progressive Web App**: Installable on mobile and desktop
- **REST API**: Programmatic access to conversion services
- **Admin Dashboard**: Manage conversions, settings, and system health
- **Secure & Private**: Files are temporarily stored and automatically deleted

## Installation

### Prerequisites

- Python 3.8+
- pip
- Linux/macOS/Windows

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd pdf-to-anything
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` and set the admin password:
```
ADMIN_PASSWORD=your-secure-password
SECRET_KEY=your-secret-key
```

5. Initialize the database:
```bash
python -c "from app import create_app; app = create_app(); app.app_context().push()"
```

6. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Configuration

All settings can be configured via environment variables in `.env`:

### Upload Settings
- `MAX_UPLOAD_SIZE_MB`: Maximum file size (default: 500)
- `MAX_FILES_PER_UPLOAD`: Maximum files in one upload (default: 50)
- `MAX_PDF_PAGES`: Maximum pages per PDF (default: 5000)

### Storage Settings
- `FILE_RETENTION_HOURS`: How long to keep files (default: 2)
- `UPLOAD_FOLDER`: Upload directory (default: uploads)
- `OUTPUT_FOLDER`: Output directory (default: outputs)
- `TEMP_FOLDER`: Temporary directory (default: temp)

### Admin Settings
- `ADMIN_PASSWORD`: Admin panel password
- `SECRET_KEY`: Flask secret key

### Conversion Settings
- `CONVERSION_TIMEOUT_SECONDS`: Timeout for conversions (default: 300)
- `WORKER_THREADS`: Number of conversion threads (default: 4)
- `OCR_ENABLED`: Enable OCR (default: true)

## Admin Panel

Access the admin panel at `/admin`

### Features
- Dashboard with statistics
- Job management and monitoring
- Format enable/disable
- System settings
- Cleanup management
- Log viewing

## API Usage

### Authentication

Requests require an `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" https://api.example.com/api/v1/convert
```

### Endpoints

#### Convert PDF

```bash
curl -X POST -H "X-API-Key: key" \
  -F "file=@document.pdf" \
  -F "formats=docx,xlsx,json" \
  https://api.example.com/api/v1/convert
```

Response:
```json
{
  "job_id": "uuid",
  "status": "queued",
  "formats": ["docx", "xlsx", "json"]
}
```

#### Get Job Status

```bash
curl -H "X-API-Key: key" \
  https://api.example.com/api/v1/jobs/job-id
```

Response:
```json
{
  "job_id": "uuid",
  "status": "completed",
  "progress": 100,
  "outputs": [
    {"format": "docx", "filename": "doc.docx", "status": "completed"}
  ]
}
```

#### Download Output

```bash
curl -H "X-API-Key: key" \
  https://api.example.com/api/v1/jobs/job-id/download/docx \
  -o output.docx
```

## Deployment

### Replit

The application is configured to run on Replit with the `.replit` configuration file.

### Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
```

### Production

1. Use a production WSGI server (gunicorn, uwsgi)
2. Configure a reverse proxy (nginx, Apache)
3. Use HTTPS with a valid certificate
4. Set `DEBUG=False`
5. Use a production database (PostgreSQL recommended)
6. Configure environment variables securely

## Supported Formats

### Documents
- DOCX (Word)
- ODT (OpenDocument)
- RTF (Rich Text)
- TXT (Plain Text)
- HTML
- Markdown

### Ebooks
- EPUB
- MOBI (Kindle)

### Spreadsheets
- XLSX (Excel)
- CSV
- ODS (OpenDocument)

### Presentations
- PPTX (PowerPoint)
- ODP (OpenDocument)

### Images
- JPG/JPEG
- PNG
- WebP
- TIFF
- BMP
- SVG

### Structured Data
- JSON
- XML
- YAML

### PDF Tools
- Compressed PDF
- Optimized PDF
- PDF/A (Archival)
- Searchable PDF (OCR)

## Architecture

### Project Structure

```
pdf-to-anything/
├── app.py                 # Main application
├── config.py              # Configuration
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── .env.example           # Example environment file
├── converters/            # Modular converter system
│   ├── base.py           # Base converter class
│   ├── registry.py       # Converter registry
│   ├── conversion_engine.py  # Main conversion logic
│   ├── documents/        # Document converters
│   ├── images/           # Image converters
│   ├── spreadsheets/     # Spreadsheet converters
│   └── data/             # Data format converters
├── services/             # Business logic services
│   ├── job_service.py    # Job management
│   ├── pdf_service.py    # PDF operations
│   ├── format_service.py # Format management
│   ├── cleanup_service.py # Cleanup operations
│   └── settings_service.py # Settings management
├── routes/               # Flask blueprints
│   ├── main.py           # Main routes
│   ├── upload.py         # Upload routes
│   ├── convert.py        # Conversion routes
│   ├── tools.py          # Tool routes
│   ├── admin.py          # Admin routes
│   └── api.py            # API routes
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   └── admin/            # Admin templates
├── static/               # Static files
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript
│   ├── manifest.json     # PWA manifest
│   └── service-worker.js # Service worker
└── README.md             # This file
```

## Security Considerations

- Files are stored with random UUIDs (not sequential IDs)
- Input validation on all uploads
- File size and page count limits
- Automatic cleanup of expired files
- CSRF protection on forms
- Secure session cookies (HttpOnly, SameSite)
- No sensitive data in logs
- Admin panel authentication required

## Performance

- Threaded conversion engine
- Efficient PDF parsing with PyPDF2
- Image optimization
- Gzip compression for responses
- Lazy loading of components

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Creating a New Converter

1. Create a new file in the appropriate converter category
2. Inherit from `BaseConverter`
3. Implement the `convert()` method
4. Add to the converter registry in `converters/registry.py`

Example:

```python
from converters.base import BaseConverter

class MyConverter(BaseConverter):
    name = 'My Format'
    output_format = 'myformat'
    
    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        try:
            # Your conversion logic here
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
```

## Troubleshooting

### Missing Dependencies

If a format shows as unavailable, install system dependencies:

```bash
# Ubuntu/Debian
sudo apt-get install libreoffice tesseract-ocr ghostscript

# macOS
brew install libreoffice tesseract ghostscript
```

### Database Issues

Reset the database:

```bash
rm pdf_to_anything.db
python -c "from app import create_app; app = create_app(); app.app_context().push()"
```

## License

MIT

## Support

For issues and feature requests, use the GitHub issue tracker.
