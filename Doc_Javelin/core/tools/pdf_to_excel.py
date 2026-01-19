"""
PDF to Excel Converter - Extract tables from PDF and convert to Excel.
"""

import os
import re
from typing import List, Optional
import pandas as pd
from pypdf import PdfReader


def extract_tables_from_pdf(pdf_path: str) -> List[List[List[str]]]:
    """
    Extract tables from PDF file.
    
    This is a basic implementation. For better results, consider using
    libraries like tabula-py or camelot-py.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of tables, where each table is a list of rows (list of strings)
    """
    try:
        reader = PdfReader(pdf_path)
        tables = []
        
        for page in reader.pages:
            text = page.extract_text()
            if not text:
                continue
            
            # Simple table extraction - split by multiple spaces or tabs
            lines = text.split('\n')
            table = []
            
            for line in lines:
                # Try to detect table rows (multiple columns separated by spaces/tabs)
                cells = re.split(r'\s{2,}|\t+', line.strip())
                if len(cells) > 1:  # Likely a table row
                    table.append([cell.strip() for cell in cells if cell.strip()])
            
            if table:
                tables.append(table)
        
        return tables
        
    except Exception as e:
        print(f"Error extracting tables from PDF: {str(e)}")
        return []


def pdf_to_excel(pdf_path: str, output_file: str, sheet_name: str = "Sheet1") -> bool:
    """
    Convert PDF file to Excel (.xlsx) format by extracting tables.
    
    Args:
        pdf_path: Path to the input PDF file
        output_file: Path to the output Excel file (.xlsx)
        sheet_name: Name of the Excel sheet (default: "Sheet1")
        
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
        
        # Extract tables from PDF
        tables = extract_tables_from_pdf(pdf_path)
        
        if not tables:
            print("Warning: No tables found in PDF. Creating empty Excel file.")
            # Create empty Excel file
            df = pd.DataFrame()
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            return True
        
        # Write to Excel - use first table or merge all tables
        if len(tables) == 1:
            # Single table
            df = pd.DataFrame(tables[0])
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
        else:
            # Multiple tables - create multiple sheets
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                for i, table in enumerate(tables):
                    df = pd.DataFrame(table)
                    sheet = f"{sheet_name}_{i+1}" if i > 0 else sheet_name
                    df.to_excel(writer, sheet_name=sheet, index=False, header=False)
        
        return True
        
    except Exception as e:
        print(f"Error converting PDF to Excel: {str(e)}")
        return False

