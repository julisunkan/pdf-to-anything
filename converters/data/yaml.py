from converters.base import BaseConverter
from services.pdf_service import PDFService
import yaml
import PyPDF2

class YamlConverter(BaseConverter):
    name = 'YAML Data'
    output_format = 'yaml'
    
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
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
            
            return True
        except Exception as e:
            print(f"Error converting to YAML: {e}")
            return False
