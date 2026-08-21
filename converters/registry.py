from converters.documents.txt import TxtConverter
from converters.documents.html import HtmlConverter
from converters.documents.docx import DocxConverter
from converters.documents.markdown import MarkdownConverter
from converters.images.jpg import JpgConverter
from converters.images.png import PngConverter
from converters.images.webp import WebpConverter
from converters.images.svg import SvgConverter
from converters.spreadsheets.csv import CsvConverter
from converters.spreadsheets.xlsx import XlsxConverter
from converters.presentations.pptx import PptxConverter
from converters.missing import (
    BitmapConverter, TiffConverter, RtfConverter, EpubConverter, MobiConverter,
    OdtConverter, OdsConverter, OdpConverter, XlsConverter,
    CompressedPdfConverter, OptimizedPdfConverter, PdfAConverter,
    SearchablePdfConverter,
)
from converters.data.json import JsonConverter
from converters.data.xml import XmlConverter
from converters.data.yaml import YamlConverter

CONVERTERS = {
    'txt': TxtConverter(),
    'html': HtmlConverter(),
    'docx': DocxConverter(),
    'markdown': MarkdownConverter(),
    'jpg': JpgConverter(),
    'png': PngConverter(),
    'webp': WebpConverter(),
    'svg': SvgConverter(),
    'csv': CsvConverter(),
    'xlsx': XlsxConverter(),
    'pptx': PptxConverter(),
    'bmp': BitmapConverter(),
    'tiff': TiffConverter(),
    'rtf': RtfConverter(),
    'epub': EpubConverter(),
    'mobi': MobiConverter(),
    'odt': OdtConverter(),
    'ods': OdsConverter(),
    'odp': OdpConverter(),
    'xls': XlsConverter(),
    'pdf_compressed': CompressedPdfConverter(),
    'pdf_optimized': OptimizedPdfConverter(),
    'pdf_a': PdfAConverter(),
    'pdf_searchable': SearchablePdfConverter(),
    'json': JsonConverter(),
    'xml': XmlConverter(),
    'yaml': YamlConverter(),
}

def get_converter(format_name: str):
    """Get converter by format name"""
    return CONVERTERS.get(format_name)

def get_available_converters():
    """Get all available converters"""
    return {name: conv for name, conv in CONVERTERS.items() if conv.is_available()}
