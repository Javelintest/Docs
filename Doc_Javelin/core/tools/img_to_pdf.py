"""
Image to PDF Converter - Convert one or more images to PDF.
"""

import os
from typing import List, Optional
from PIL import Image


def img_to_pdf(image_paths: List[str], output_file: str, 
               single_pdf_per_image: bool = False) -> bool:
    """
    Convert one or more images to PDF.
    
    Args:
        image_paths: List of paths to image files
        output_file: Path to the output PDF file (or directory if single_pdf_per_image=True)
        single_pdf_per_image: If True, create separate PDF for each image
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not image_paths:
            raise ValueError("No image files provided")
        
        # Validate all input files exist
        supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        for file_path in image_paths:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Image file not found: {file_path}")
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in supported_formats:
                raise ValueError(f"Unsupported image format: {ext}")
        
        if single_pdf_per_image:
            # Create separate PDF for each image
            output_dir = output_file if os.path.isdir(output_file) else os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            for img_path in image_paths:
                base_name = os.path.splitext(os.path.basename(img_path))[0]
                pdf_path = os.path.join(output_dir, f"{base_name}.pdf")
                
                image = Image.open(img_path)
                # Convert RGBA to RGB if necessary
                if image.mode == 'RGBA':
                    rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                    rgb_image.paste(image, mask=image.split()[3])
                    image = rgb_image
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                image.save(pdf_path, 'PDF', resolution=100.0)
        else:
            # Create single PDF with all images
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            images = []
            for img_path in image_paths:
                image = Image.open(img_path)
                # Convert RGBA to RGB if necessary
                if image.mode == 'RGBA':
                    rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                    rgb_image.paste(image, mask=image.split()[3])
                    image = rgb_image
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                images.append(image)
            
            if images:
                images[0].save(
                    output_file,
                    'PDF',
                    resolution=100.0,
                    save_all=True,
                    append_images=images[1:] if len(images) > 1 else []
                )
        
        return True
        
    except Exception as e:
        print(f"Error converting images to PDF: {str(e)}")
        return False

