from converters.base import BaseConverter
from services.pdf_service import PDFService

class MarkdownConverter(BaseConverter):
    name = 'Markdown'
    output_format = 'markdown'
    
    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        try:
            options = options or {}
            text = PDFService.extract_text(input_path)
            
            markdown_content = f"""# PDF Converted to Markdown

{text}
"""
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            return True
        except Exception as e:
            print(f"Error converting to Markdown: {e}")
            return False
