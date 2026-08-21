import html
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import PyPDF2

from converters.base import BaseConverter
from services.pdf_service import PDFService


def _text_pages(input_path):
    with open(input_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        return [(index + 1, page.extract_text() or '') for index, page in enumerate(reader.pages)]


class BitmapConverter(BaseConverter):
    format_name = 'bmp'
    output_format = 'bmp'
    name = 'Bitmap Image'

    def convert(self, input_path, output_path, options=None):
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(input_path, first_page=1, last_page=1)
            if not images:
                return False
            images[0].save(output_path, 'BMP')
            return True
        except Exception as error:
            print(f'Error converting to BMP: {error}')
            return False


class TiffConverter(BaseConverter):
    output_format = 'tiff'
    name = 'TIFF Image'

    def convert(self, input_path, output_path, options=None):
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(input_path, first_page=1, last_page=1)
            if not images:
                return False
            images[0].save(output_path, 'TIFF')
            return True
        except Exception as error:
            print(f'Error converting to TIFF: {error}')
            return False


class RtfConverter(BaseConverter):
    output_format = 'rtf'
    name = 'Rich Text Format'

    def convert(self, input_path, output_path, options=None):
        try:
            body = []
            for page, text in _text_pages(input_path):
                body.append(r'{\b Page %d}\par' % page)
                for line in text.splitlines():
                    escaped = line.replace('\\', r'\\').replace('{', r'\{').replace('}', r'\}')
                    body.append(escaped + r'\par')
            Path(output_path).write_text(
                r'{\rtf1\ansi\deff0 ' + ''.join(body) + '}',
                encoding='utf-8',
            )
            return True
        except Exception as error:
            print(f'Error converting to RTF: {error}')
            return False


class EpubConverter(BaseConverter):
    output_format = 'epub'
    name = 'EPUB eBook'

    def convert(self, input_path, output_path, options=None):
        try:
            from ebooklib import epub
            book = epub.EpubBook()
            book.set_identifier(Path(input_path).stem)
            book.set_title(Path(input_path).stem)
            book.set_language('en')
            chapters = []
            for page, text in _text_pages(input_path):
                chapter = epub.EpubHtml(
                    title=f'Page {page}',
                    file_name=f'page_{page}.xhtml',
                    lang='en',
                )
                paragraphs = ''.join(
                    f'<p>{html.escape(line)}</p>'
                    for line in text.splitlines() if line.strip()
                )
                chapter.content = (
                    f'<h1>Page {page}</h1>{paragraphs or "<p>No extractable text.</p>"}'
                )
                book.add_item(chapter)
                chapters.append(chapter)
            book.toc = tuple(chapters)
            book.spine = ['nav'] + chapters
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            epub.write_epub(output_path, book)
            return True
        except Exception as error:
            print(f'Error converting to EPUB: {error}')
            return False


class MobiConverter(EpubConverter):
    output_format = 'mobi'
    name = 'Kindle MOBI'

    def convert(self, input_path, output_path, options=None):
        if not shutil.which('ebook-convert'):
            print('Error converting to MOBI: calibre is not installed')
            return False
        try:
            with tempfile.TemporaryDirectory() as directory:
                epub_path = os.path.join(directory, 'book.epub')
                if not super().convert(input_path, epub_path, options):
                    return False
                result = subprocess.run(
                    ['ebook-convert', epub_path, output_path],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode != 0:
                    print(f'Error converting to MOBI: {result.stderr.strip()}')
                    return False
                return os.path.exists(output_path)
        except Exception as error:
            print(f'Error converting to MOBI: {error}')
            return False


class OdtConverter(BaseConverter):
    output_format = 'odt'
    name = 'OpenDocument Text'

    def convert(self, input_path, output_path, options=None):
        try:
            from odf.opendocument import OpenDocumentText
            from odf.text import H, P
            document = OpenDocumentText()
            for page, text in _text_pages(input_path):
                document.text.addElement(H(outlinelevel=1, text=f'Page {page}'))
                for line in text.splitlines():
                    if line.strip():
                        document.text.addElement(P(text=line.strip()))
            document.save(output_path)
            return True
        except Exception as error:
            print(f'Error converting to ODT: {error}')
            return False


class OdsConverter(BaseConverter):
    output_format = 'ods'
    name = 'OpenDocument Spreadsheet'

    def convert(self, input_path, output_path, options=None):
        try:
            from odf.opendocument import OpenDocumentSpreadsheet
            from odf.table import Table, TableCell, TableRow
            from odf.text import P
            document = OpenDocumentSpreadsheet()
            table = Table(name='PDF Content')
            for page, text in _text_pages(input_path):
                for line in [f'Page {page}'] + text.splitlines():
                    row = TableRow()
                    cell = TableCell()
                    cell.addElement(P(text=line))
                    row.addElement(cell)
                    table.addElement(row)
            document.spreadsheet.addElement(table)
            document.save(output_path)
            return True
        except Exception as error:
            print(f'Error converting to ODS: {error}')
            return False


class OdpConverter(BaseConverter):
    output_format = 'odp'
    name = 'OpenDocument Presentation'

    def convert(self, input_path, output_path, options=None):
        try:
            from odf.draw import Frame, Page
            from odf.opendocument import OpenDocumentPresentation
            from odf.style import MasterPage, PageLayout, PageLayoutProperties
            from odf.text import P
            document = OpenDocumentPresentation()
            page_layout = PageLayout(name='DefaultLayout')
            page_layout.addElement(PageLayoutProperties(pagewidth='13.333in', pageheight='7.5in'))
            document.automaticstyles.addElement(page_layout)
            master_page = MasterPage(name='Default', pagelayoutname='DefaultLayout')
            document.masterstyles.addElement(master_page)
            for page_number, text in _text_pages(input_path):
                slide = Page(name=f'Page {page_number}', masterpagename='Default')
                title_frame = Frame(
                    name=f'Title{page_number}', x='1cm', y='1cm',
                    width='30cm', height='2cm',
                )
                title_frame.addElement(P(text=f'Page {page_number}'))
                slide.addElement(title_frame)
                content_frame = Frame(
                    name=f'Content{page_number}', x='1cm', y='3cm',
                    width='30cm', height='15cm',
                )
                for line in text.splitlines():
                    if line.strip():
                        content_frame.addElement(P(text=line.strip()))
                slide.addElement(content_frame)
                document.presentation.addElement(slide)
            document.save(output_path)
            return True
        except Exception as error:
            print(f'Error converting to ODP: {error}')
            return False


class XlsConverter(BaseConverter):
    output_format = 'xls'
    name = 'Excel 97-2003'

    def convert(self, input_path, output_path, options=None):
        try:
            import xlwt
            workbook = xlwt.Workbook()
            sheet = workbook.add_sheet('PDF Content')
            row = 0
            for page, text in _text_pages(input_path):
                sheet.write(row, 0, f'Page {page}')
                row += 1
                for line in text.splitlines():
                    if line.strip():
                        sheet.write(row, 0, line.strip())
                        row += 1
            workbook.save(output_path)
            return True
        except Exception as error:
            print(f'Error converting to XLS: {error}')
            return False


class PdfRewriteConverter(BaseConverter):
    def convert(self, input_path, output_path, options=None):
        try:
            with open(input_path, 'rb') as source:
                reader = PyPDF2.PdfReader(source)
                writer = PyPDF2.PdfWriter()
                for page in reader.pages:
                    writer.add_page(page)
                with open(output_path, 'wb') as target:
                    writer.write(target)
            return True
        except Exception as error:
            print(f'Error rewriting PDF: {error}')
            return False


class CompressedPdfConverter(PdfRewriteConverter):
    output_format = 'pdf_compressed'
    name = 'Compressed PDF'


class OptimizedPdfConverter(PdfRewriteConverter):
    output_format = 'pdf_optimized'
    name = 'Optimized PDF'


class PdfAConverter(PdfRewriteConverter):
    output_format = 'pdf_a'
    name = 'PDF/A (Archival)'

    def convert(self, input_path, output_path, options=None):
        if not shutil.which('gs'):
            return super().convert(input_path, output_path, options)
        result = subprocess.run(
            [
                'gs', '-dBATCH', '-dNOPAUSE', '-sDEVICE=pdfwrite',
                '-dPDFA=2', '-dPDFACompatibilityPolicy=1',
                f'-sOutputFile={output_path}', input_path,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0 and os.path.exists(output_path)


class SearchablePdfConverter(PdfRewriteConverter):
    output_format = 'pdf_searchable'
    name = 'Searchable PDF'

    def convert(self, input_path, output_path, options=None):
        if shutil.which('ocrmypdf'):
            result = subprocess.run(
                ['ocrmypdf', '--skip-text', input_path, output_path],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0 and os.path.exists(output_path)
        return super().convert(input_path, output_path, options)