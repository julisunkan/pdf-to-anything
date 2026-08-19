from converters.base import BaseConverter
from services.pdf_service import PDFService
import csv

class CsvConverter(BaseConverter):
    name = 'CSV Spreadsheet'
    output_format = 'csv'
    
    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        try:
            options = options or {}
            text = PDFService.extract_text(input_path)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                for line in text.split('\n'):
                    if line.strip():
                        writer.writerow([line.strip()])
            
            return True
        except Exception as e:
            print(f"Error converting to CSV: {e}")
            return False
