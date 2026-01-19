from pypdf import PdfReader, PdfWriter
import os

def edit_pdf(input_path, output_path, pages_config):
    """
    Edit a PDF file by reordering, rotating, or selecting specific pages.
    
    Args:
        input_path (str): Path to the source PDF file.
        output_path (str): Path to save the resulting PDF.
        pages_config (list): A list of dictionaries defining the new page structure.
                             Each dict should have:
                             - 'index': int (original 0-based page index)
                             - 'rotate': int (0, 90, 180, 270) (optional, cumulative to existing rotation)
                             
                             The order of items in this list determines the order in the output PDF.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        total_pages = len(reader.pages)
        
        for page_cfg in pages_config:
            original_index = int(page_cfg.get('index'))
            
            if 0 <= original_index < total_pages:
                page = reader.pages[original_index]
                
                # Apply rotation if specified
                rotation = int(page_cfg.get('rotate', 0))
                if rotation % 90 == 0 and rotation != 0:
                    page.rotate(rotation)
                
                writer.add_page(page)
        
        with open(output_path, "wb") as f_out:
            writer.write(f_out)
            
        return True
        
    except Exception as e:
        print(f"Error editing PDF: {str(e)}")
        return False
