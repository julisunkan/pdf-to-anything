from converters.base import BaseConverter
from openpyxl import Workbook
from services.pdf_service import PDFService

class XlsxConverter(BaseConverter):
    name = 'Excel Spreadsheet'
    output_format = 'xlsx'
    
    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        try:
            options = options or {}
            
            wb = Workbook()
            ws = wb.active
            ws.title = "PDF Content"
            
            text = PDFService.extract_text(input_path)
            
            row = 1
            for line in text.split('\n'):
                if line.strip():
                    ws[f'A{row}'] = line.strip()
                    row += 1
            
            wb.save(output_path)
            return True
        except Exception as e:
            print(f"Error converting to XLSX: {e}")
            return False
