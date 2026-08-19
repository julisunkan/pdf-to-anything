from converters.base import BaseConverter
from services.pdf_service import PDFService
import json
import PyPDF2

class JsonConverter(BaseConverter):
    name = 'JSON Data'
    output_format = 'json'
    
    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        try:
            options = options or {}
            
            data = {
                'metadata': PDFService.get_metadata(input_path),
                'pages': []
            }
            
            with open(input_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    data['pages'].append({
                        'number': i + 1,
                        'text': text,
                        'content_length': len(text)
                    })
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error converting to JSON: {e}")
            return False
