from converters.base import BaseConverter
from services.pdf_service import PDFService

class TxtConverter(BaseConverter):
    name = 'Text (TXT)'
    output_format = 'txt'
    
    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        try:
            options = options or {}
            text = PDFService.extract_text(input_path)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            return True
        except Exception as e:
            print(f"Error converting to TXT: {e}")
            return False
