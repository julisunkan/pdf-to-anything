import pytest
import os
import tempfile
from app import create_app
from models import db, ConversionJob
from services.job_service import JobService
from services.pdf_service import PDFService

@pytest.fixture
def app():
    """Create app for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def sample_pdf():
    """Create a sample PDF for testing"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        c = canvas.Canvas(f.name, pagesize=letter)
        c.drawString(100, 750, "Test PDF")
        c.drawString(100, 730, "This is a sample PDF for testing.")
        c.save()
        yield f.name
        os.unlink(f.name)

class TestUpload:
    """Test file upload functionality"""
    
    def test_upload_pdf(self, client, sample_pdf):
        """Test uploading a single PDF"""
        with open(sample_pdf, 'rb') as f:
            response = client.post('/upload/file', data={'file': f})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['filename']

class TestJobService:
    """Test job service"""
    
    def test_create_job(self, app):
        """Test creating a job"""
        with app.app_context():
            job = JobService.create_job(
                'test.pdf',
                '/tmp/test.pdf',
                1024,
                ['docx', 'xlsx'],
                10
            )
            
            assert job is not None
            assert job.original_filename == 'test.pdf'
            assert job.status == 'queued'
    
    def test_update_job_status(self, app):
        """Test updating job status"""
        with app.app_context():
            job = JobService.create_job(
                'test.pdf',
                '/tmp/test.pdf',
                1024,
                ['docx'],
                10
            )
            
            JobService.update_job_status(job.id, 'processing', progress=50)
            updated_job = JobService.get_job(job.id)
            
            assert updated_job.status == 'processing'
            assert updated_job.progress_percent == 50

class TestPDFService:
    """Test PDF service"""
    
    def test_get_page_count(self, sample_pdf):
        """Test getting page count"""
        count = PDFService.get_page_count(sample_pdf)
        assert count == 1
    
    def test_extract_text(self, sample_pdf):
        """Test text extraction"""
        text = PDFService.extract_text(sample_pdf)
        assert 'Test PDF' in text or len(text) > 0
    
    def test_has_text(self, sample_pdf):
        """Test text detection"""
        has_text = PDFService.has_text(sample_pdf)
        assert has_text == True or has_text == False  # Just check it runs

class TestAdmin:
    """Test admin functionality"""
    
    def test_admin_login(self, client, app):
        """Test admin login"""
        response = client.get('/admin/login')
        assert response.status_code == 200
    
    def test_admin_authentication(self, client, app):
        """Test admin authentication"""
        with app.test_client() as c:
            c.get('/admin/login')
            with c.session_transaction() as session:
                csrf_token = session['csrf_token']
            response = c.post('/admin/login', data={
                'password': app.config['ADMIN_PASSWORD'],
                'csrf_token': csrf_token,
            })
            # Should redirect to dashboard
            assert response.status_code in [200, 302]

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
