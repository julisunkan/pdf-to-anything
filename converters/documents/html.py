from converters.base import BaseConverter
from services.pdf_service import PDFService
import PyPDF2

class HtmlConverter(BaseConverter):
    name = 'HTML Document'
    output_format = 'html'
    
    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        try:
            options = options or {}
            
            with open(input_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                
                html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Converted to HTML</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .page { page-break-after: always; margin: 20px 0; padding: 20px; border: 1px solid #ddd; }
        .page-number { color: #999; font-size: 0.9em; margin-bottom: 10px; }
    </style>
</head>
<body>
'''
                
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    html_content += f'<div class="page"><div class="page-number">Page {i+1}</div>'
                    for line in text.split('\n'):
                        if line.strip():
                            html_content += f'<p>{line.strip()}</p>'
                    html_content += '</div>'
                
                html_content += '</body></html>'
                
                with open(output_path, 'w', encoding='utf-8') as out:
                    out.write(html_content)
            
            return True
        except Exception as e:
            print(f"Error converting to HTML: {e}")
            return False
