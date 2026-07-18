"""
CV Parser Service — Extracts text from PDF files.
Refactored from the original main.py extract_text_from_pdf() function.
"""

import io
from pypdf import PdfReader


def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    """
    Extracts text from PDF file bytes (uploaded via API).
    
    Args:
        file_bytes: Raw bytes of the PDF file.
        
    Returns:
        Extracted text content as a string.
        
    Raises:
        ValueError: If no text could be extracted from the PDF.
    """
    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts = []

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text_parts.append(extracted)

    text = "\n".join(text_parts).strip()

    if not text:
        raise ValueError(
            "No text could be extracted from the PDF. "
            "The file may be image-based or empty."
        )

    return text


def extract_text_from_pdf_path(pdf_path: str) -> str:
    """
    Extracts text from a PDF file on disk (for CLI/testing compatibility).
    
    Args:
        pdf_path: Absolute or relative path to the PDF file.
        
    Returns:
        Extracted text content as a string.
    """
    with open(pdf_path, "rb") as f:
        return extract_text_from_pdf_bytes(f.read())
