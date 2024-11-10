import asyncio
from io import BytesIO
import docx
from pdfminer.high_level import extract_text
from bs4 import BeautifulSoup

class FileExtractor:
    async def extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF content."""
        try:
            return await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: extract_text(BytesIO(content))
            )
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
            
    async def extract_text_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX content."""
        try:
            doc = docx.Document(BytesIO(content))
            return await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: '\n'.join(paragraph.text for paragraph in doc.paragraphs)
            )
        except Exception as e:
            raise ValueError(f"Failed to extract text from DOCX: {str(e)}")
            
    async def extract_text_from_html(self, content: bytes) -> str:
        """Extract text from HTML content."""
        try:
            soup = BeautifulSoup(content.decode('utf-8'), 'html.parser')
            return str(soup)
        except Exception as e:
            raise ValueError(f"Failed to extract text from HTML: {str(e)}")