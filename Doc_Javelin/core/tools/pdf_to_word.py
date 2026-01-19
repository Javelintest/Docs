"""
PDF to Word Converter - Convert PDF files to Word (.docx) format.
"""

import os
from typing import List, Optional
from docx import Document
from pypdf import PdfReader
import re


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as string
    """
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return ""


def pdf_to_word(pdf_path: str, output_file: str) -> bool:
    """
    Convert PDF file to Word (.docx) format.
    
    Note: This is a basic text extraction. For complex PDFs with formatting,
    images, and tables, consider using pdf2docx library or other advanced tools.
    
    Args:
        pdf_path: Path to the input PDF file
        output_file: Path to the output Word file (.docx)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if not pdf_path.lower().endswith('.pdf'):
            raise ValueError(f"Not a PDF file: {pdf_path}")
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path)
        
        if not text.strip():
            print("Warning: No text could be extracted from the PDF")
            return False
        
        # Create Word document
        doc = Document()
        
        # Split text into paragraphs (simple approach)
        paragraphs = text.split('\n\n')
        for para_text in paragraphs:
            if para_text.strip():
                # Clean up the text
                para_text = re.sub(r'\s+', ' ', para_text.strip())
                doc.add_paragraph(para_text)
        
        # Save document
        doc.save(output_file)
        
        return True
        
    except Exception as e:
        print(f"Error converting PDF to Word: {str(e)}")
        return False

