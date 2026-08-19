from converters.base import BaseConverter
from pdf2image import convert_from_path

class PngConverter(BaseConverter):
    name = 'PNG Image'
    output_format = 'png'
    
    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        try:
            options = options or {}
            
            images = convert_from_path(input_path, first_page=1, last_page=1)
            if images:
                images[0].save(output_path, 'PNG')
            return True
        except Exception as e:
            print(f"Error converting to PNG: {e}")
            return False
    
    @staticmethod
    def is_available() -> bool:
        try:
            import pdf2image
            return True
        except ImportError:
            return False
