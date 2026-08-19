from converters.base import BaseConverter
from pdf2image import convert_from_path
from PIL import Image
import os

class JpgConverter(BaseConverter):
    name = 'JPEG Image'
    output_format = 'jpg'
    
    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        try:
            options = options or {}
            quality = options.get('quality', 85)
            
            images = convert_from_path(input_path, first_page=1, last_page=1)
            if images:
                images[0].save(output_path, 'JPEG', quality=quality)
            return True
        except Exception as e:
            print(f"Error converting to JPG: {e}")
            return False
    
    @staticmethod
    def is_available() -> bool:
        try:
            import pdf2image
            return True
        except ImportError:
            return False
