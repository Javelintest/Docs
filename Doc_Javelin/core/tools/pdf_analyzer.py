"""
PDF Analyzer Tool
Extracts metadata and text coordinates from PDF pages for the frontend inspector.
"""

import fitz  # PyMuPDF
import os
import json

def analyze_pdf_text(pdf_path: str, page_num: int):
    """
    Extract text blocks with coordinates from a specific PDF page.
    
    Args:
        pdf_path: Path to the PDF file
        page_num: Page number (1-based)
        
    Returns:
        List of text block dictionaries or None if error
    """
    try:
        doc = fitz.open(pdf_path)
        
        # Validate page number
        if page_num < 1 or page_num > len(doc):
            return None
            
        page = doc[page_num - 1] # 0-indexed
        
        # Get text in dict format to retrieve coordinates and font info
        # Structure: block -> lines -> spans -> chars
        text_dict = page.get_text("dict")
        
        blocks_data = []
        
        for block in text_dict.get("blocks", []):
            if block.get("type") == 0: # 0 = text, 1 = image
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        # Extract span data
                        # bbox is [x0, y0, x1, y1]
                        # color is sRGB integer
                        
                        # Convert integer color to hex
                        color_int = span.get("color", 0)
                        hex_color = "#{:06x}".format(color_int) if isinstance(color_int, int) else "#000000"
                        
                        span_data = {
                            "text": span.get("text", "").strip(),
                            "bbox": span.get("bbox", []),
                            "size": span.get("size", 12),
                            "font": span.get("font", "Helvetica"),
                            "color": hex_color,
                            "origin": span.get("origin", []) # baseline origin
                        }
                        
                        if span_data["text"]: # Only add if has text
                            blocks_data.append(span_data)
                            
        doc.close()
        return blocks_data
        
    except Exception as e:
        print(f"Error analyzing PDF text: {e}")
        return None

if __name__ == "__main__":
    # Test
    # print(analyze_pdf_text("test.pdf", 1))
    pass
