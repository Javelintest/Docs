"""
PDF Merger Tool - Merge multiple PDF files into a single PDF.
"""

import os
from typing import List
from pypdf import PdfWriter, PdfReader


def merge_pdfs(input_files: List[str], output_file: str) -> bool:
    """
    Merge multiple PDF files into a single PDF.
    
    Args:
        input_files: List of paths to PDF files to merge
        output_file: Path to the output merged PDF file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not input_files:
            raise ValueError("No input files provided")
        
        # Validate all input files exist
        for file_path in input_files:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Input file not found: {file_path}")
            if not file_path.lower().endswith('.pdf'):
                raise ValueError(f"Not a PDF file: {file_path}")
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Merge PDFs
        merger = PdfWriter()
        
        for file_path in input_files:
            reader = PdfReader(file_path)
            for page in reader.pages:
                merger.add_page(page)
        
        # Write merged PDF
        with open(output_file, 'wb') as output:
            merger.write(output)
        
        return True
        
    except Exception as e:
        print(f"Error merging PDFs: {str(e)}")
        return False

