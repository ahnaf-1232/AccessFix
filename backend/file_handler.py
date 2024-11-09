import io
from docx import Document
import fitz


def extract_text_from_pdf(self, file_bytes):
        text = ""
        with fitz.open(stream=file_bytes, filetype="pdf") as pdf:
            for page in pdf:
                text += page.get_text()
        return text

def extract_text_from_docx(self, file_bytes):
        text = ""
        doc = Document(io.BytesIO(file_bytes))
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

def extract_text_from_html(self, file_bytes):
        return file_bytes.decode("utf-8")