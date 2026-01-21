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
        
        # If config is empty, assume we want all pages (maybe just for a passthrough or verification)
        if not pages_config:
            # Copy all pages if no config
            for i in range(total_pages):
                writer.add_page(reader.pages[i])
        else:
            # 1. Map config by page number (1-based from frontend) to internal 0-based index
            # The frontend sends a list of changes for specific pages. 
            # Pages NOT in the config should be included as-is (unless we only want to keep selected?)
            # Wait, the current logic assumes `pages_config` IS the new order.
            # BUT the frontend only sends changes for specific pages (rotate/delete).
            # We need to iterate through ALL original pages and apply changes or skip if deleted.
            
            # Create a lookup map for changes: page_num (1-based) -> config
            changes_map = { int(cfg['pageNum']): cfg for cfg in pages_config }
            
            for i in range(total_pages):
                page_num = i + 1 # 1-based
                cfg = changes_map.get(page_num)
                
                if cfg and cfg.get('deleted') == True:
                    continue # Skip deleted pages
                
                page = reader.pages[i]
                
                if cfg:
                    rotation = int(cfg.get('rotation', 0))
                    if rotation != 0:
                        page.rotate(rotation)
                
                writer.add_page(page)
        
        with open(output_path, "wb") as f_out:
            writer.write(f_out)
            
        return True
        
    except Exception as e:
        print(f"Error editing PDF: {str(e)}")
        return False
