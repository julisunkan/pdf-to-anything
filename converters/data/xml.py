from converters.base import BaseConverter
from services.pdf_service import PDFService
from lxml import etree
import PyPDF2

class XmlConverter(BaseConverter):
    name = 'XML Data'
    output_format = 'xml'
    
    def convert(self, input_path: str, output_path: str, options: dict = None) -> bool:
        try:
            options = options or {}
            
            root = etree.Element('document')
            
            # Add metadata
            metadata_elem = etree.SubElement(root, 'metadata')
            metadata = PDFService.get_metadata(input_path)
            for key, value in metadata.items():
                elem = etree.SubElement(metadata_elem, key)
                elem.text = str(value)
            
            # Add pages
            pages_elem = etree.SubElement(root, 'pages')
            
            with open(input_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                
                for i, page in enumerate(reader.pages):
                    page_elem = etree.SubElement(pages_elem, 'page', number=str(i + 1))
                    text = page.extract_text()
                    page_elem.text = text
            
            tree = etree.ElementTree(root)
            tree.write(output_path, encoding='utf-8', xml_declaration=True, pretty_print=True)
            
            return True
        except Exception as e:
            print(f"Error converting to XML: {e}")
            return False
