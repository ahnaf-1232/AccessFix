import asyncio
from io import BytesIO
import docx
from pdfminer.high_level import extract_text
from bs4 import BeautifulSoup

class FileExtractor:
    def extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF content."""
        try:
            return extract_text(BytesIO(content))  # Synchronous call
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
            
    def extract_text_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX content."""
        try:
            doc = docx.Document(BytesIO(content))
            return '\n'.join(paragraph.text for paragraph in doc.paragraphs)  # Synchronous call
        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX: {str(e)}")
            
    def extract_text_from_html(self, content: bytes) -> str:
        """Extract text from HTML content."""
        try:
            soup = BeautifulSoup(content.decode('utf-8'), 'html.parser')
            print("file read successfully")
            return str(soup)  # Synchronous call
        except Exception as e:
            raise ValueError(f"Failed to extract text from HTML: {str(e)}")