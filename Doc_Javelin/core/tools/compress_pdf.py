from pypdf import PdfReader, PdfWriter
import os

def compress_pdf(input_path, output_path, level=1):
    """
    Compress PDF by reducing redundancy and removing unused objects.
    Note: pypdf compression is lossless/structural. It doesn't down-sample images aggressively 
    like Ghostscript, but it optimizes the file structure.
    
    Args:
        input_path (str): Source file.
        output_path (str): Dest file.
        level (int): 0-9 (Though pypdf mostly just has 'compress_identical_objects')
    """
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
            
        # Optimization methods available in pypdf
        writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
        
        # If we wanted to downsample images, we'd need to iterate pages, find images, resize, replace.
        # That's complex for pure python without PIL+heavy logic. 
        # For now, structural compression is a safe "Optimize" start.
        
        with open(output_path, "wb") as f:
            writer.write(f)
            
        return True
    except Exception as e:
        print(f"Error compressing PDF: {e}")
        return False
