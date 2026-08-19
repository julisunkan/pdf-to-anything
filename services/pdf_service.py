import PyPDF2
import json
from pathlib import Path

class PDFService:
    """Service for PDF analysis and manipulation"""
    
    @staticmethod
    def get_page_count(pdf_path):
        """Get the number of pages in a PDF"""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                return len(reader.pages)
        except Exception as e:
            print(f"Error getting page count: {e}")
            return 0
    
    @staticmethod
    def get_metadata(pdf_path):
        """Extract metadata from PDF"""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                metadata = reader.metadata or {}
                
                return {
                    'title': metadata.get('/Title', 'Unknown'),
                    'author': metadata.get('/Author', 'Unknown'),
                    'subject': metadata.get('/Subject', ''),
                    'creator': metadata.get('/Creator', ''),
                    'producer': metadata.get('/Producer', ''),
                    'creation_date': metadata.get('/CreationDate', ''),
                    'modification_date': metadata.get('/ModDate', ''),
                    'pages': len(reader.pages)
                }
        except Exception as e:
            print(f"Error getting metadata: {e}")
            return {}
    
    @staticmethod
    def has_text(pdf_path):
        """Check if PDF has extractable text"""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                
                if len(reader.pages) == 0:
                    return False
                
                # Check first few pages for text
                for i, page in enumerate(reader.pages[:min(3, len(reader.pages))]):
                    text = page.extract_text()
                    if text and len(text.strip()) > 50:
                        return True
                
                return False
        except Exception as e:
            print(f"Error checking for text: {e}")
            return False
    
    @staticmethod
    def extract_text(pdf_path, pages=None):
        """Extract text from PDF"""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                
                page_list = pages if pages else range(len(reader.pages))
                
                for page_num in page_list:
                    if page_num < len(reader.pages):
                        page = reader.pages[page_num]
                        text += f"\n--- Page {page_num + 1} ---\n"
                        text += page.extract_text()
                
                return text
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""
    
    @staticmethod
    def merge_pdfs(pdf_paths, output_path):
        """Merge multiple PDFs"""
        try:
            merger = PyPDF2.PdfMerger()
            
            for pdf_path in pdf_paths:
                merger.append(pdf_path)
            
            with open(output_path, 'wb') as output_file:
                merger.write(output_file)
            
            merger.close()
            return True
        except Exception as e:
            print(f"Error merging PDFs: {e}")
            return False
    
    @staticmethod
    def split_pdf(pdf_path, output_dir, page_range=None):
        """Split PDF into individual pages"""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                output_files = []
                
                pages = page_range if page_range else range(len(reader.pages))
                
                for page_num in pages:
                    if page_num < len(reader.pages):
                        writer = PyPDF2.PdfWriter()
                        writer.add_page(reader.pages[page_num])
                        
                        output_path = Path(output_dir) / f'page_{page_num + 1}.pdf'
                        
                        with open(output_path, 'wb') as output_file:
                            writer.write(output_file)
                        
                        output_files.append(str(output_path))
                
                return output_files
        except Exception as e:
            print(f"Error splitting PDF: {e}")
            return []
    
    @staticmethod
    def extract_pages(pdf_path, output_path, pages):
        """Extract specific pages from PDF"""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                writer = PyPDF2.PdfWriter()
                
                for page_num in pages:
                    if page_num < len(reader.pages):
                        writer.add_page(reader.pages[page_num])
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                return True
        except Exception as e:
            print(f"Error extracting pages: {e}")
            return False
    
    @staticmethod
    def rotate_pages(pdf_path, output_path, pages, rotation):
        """Rotate specific pages in a PDF"""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                writer = PyPDF2.PdfWriter()
                
                for i, page in enumerate(reader.pages):
                    if i in pages:
                        page.rotate(rotation)
                    writer.add_page(page)
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                return True
        except Exception as e:
            print(f"Error rotating pages: {e}")
            return False
    
    @staticmethod
    def delete_pages(pdf_path, output_path, pages_to_delete):
        """Delete specific pages from PDF"""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                writer = PyPDF2.PdfWriter()
                
                for i, page in enumerate(reader.pages):
                    if i not in pages_to_delete:
                        writer.add_page(page)
                
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                return True
        except Exception as e:
            print(f"Error deleting pages: {e}")
            return False
