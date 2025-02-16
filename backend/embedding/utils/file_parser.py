import os
import re

# If you want to parse PDFs:
from pdfminer.high_level import extract_text
# If you want to parse DOCX:
import docx

def parse_file(file_path):
    """
    Parses a file at the given path (PDF, DOCX, or TXT) and returns the extracted text.
    """
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        return parse_pdf(file_path)
    elif extension in [".docx", ".doc"]:
        return parse_docx(file_path)
    elif extension == ".txt":
        return parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {extension}")

def parse_pdf(file_path):
    """
    Extract text from a PDF file using pdfminer.six
    """
    try:
        text = extract_text(file_path)
        return clean_text(text)
    except Exception as e:
        raise Exception(f"Error parsing PDF: {str(e)}")

def parse_docx(file_path):
    """
    Extract text from a DOCX file using python-docx
    """
    try:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            if para.text:
                full_text.append(para.text)
        return clean_text("\n".join(full_text))
    except Exception as e:
        raise Exception(f"Error parsing DOCX: {str(e)}")

def parse_txt(file_path):
    """
    Read text from a plain .txt file
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        return clean_text(text)
    except Exception as e:
        raise Exception(f"Error reading text file: {str(e)}")

def clean_text(text):
    """
    Clean up any extraneous whitespace or characters if needed.
    """
    # Basic cleaning example:
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r'\s+', ' ', text).strip()
    return text
