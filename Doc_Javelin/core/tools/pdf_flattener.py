"""
PDF Flattener Tool
Merges annotation layers (text, drawings, highlights) onto a PDF using PyMuPDF (fitz).
"""

import fitz  # PyMuPDF
import os
import json


def flatten_pdf_with_layers(input_pdf_path: str, layers: list, output_pdf_path: str) -> bool:
    """
    Flatten layers onto a PDF file.
    
    Args:
        input_pdf_path: Path to the original PDF file
        layers: List of layer dictionaries with type, position, and properties
        output_pdf_path: Path where the flattened PDF will be saved
        
    Returns:
        True if successful, False otherwise
    """
    try:
        doc = fitz.open(input_pdf_path)
        
        for layer in layers:
            page_num = layer.get('pageNum', 1) - 1  # Convert to 0-indexed
            if page_num < 0 or page_num >= len(doc):
                continue
                
            page = doc[page_num]
            layer_type = layer.get('type', '')
            
            if layer_type == 'text' or layer_type == 'i-text':
                _add_text_layer(page, layer)
            elif layer_type == 'path':
                _add_path_layer(page, layer)
            elif layer_type == 'rect':
                _add_rect_layer(page, layer)
            elif layer_type == 'image':
                _add_image_layer(page, layer)
        
        doc.save(output_pdf_path)
        doc.close()
        return True
        
    except Exception as e:
        print(f"Error flattening PDF: {e}")
        return False


def _add_text_layer(page, layer: dict):
    """Add text annotation to page."""
    text = layer.get('text', '')
    if not text:
        return
        
    x = layer.get('left', 0)
    y = layer.get('top', 0)
    font_size = layer.get('fontSize', 12)
    color_hex = layer.get('fill', '#000000')
    
    # Convert hex to RGB tuple (0-1 range)
    color = hex_to_rgb(color_hex)
    
    # Apply scale factors if present
    scale_x = layer.get('scaleX', 1)
    scale_y = layer.get('scaleY', 1)
    font_size = font_size * scale_y
    
    # Insert text
    point = fitz.Point(x, y + font_size)  # fitz uses bottom-left for text
    page.insert_text(
        point,
        text,
        fontsize=font_size,
        color=color,
        fontname="helv"  # Helvetica
    )


def _add_path_layer(page, layer: dict):
    """Add freehand drawing path to page."""
    path_data = layer.get('path', [])
    if not path_data:
        return
        
    stroke_hex = layer.get('stroke', '#000000')
    stroke_width = layer.get('strokeWidth', 2)
    color = hex_to_rgb(stroke_hex)
    
    # Convert Fabric.js path to PyMuPDF shape
    # Fabric.js path format: [["M", x, y], ["L", x, y], ...]
    shape = page.new_shape()
    
    for cmd in path_data:
        if not cmd or len(cmd) < 3:
            continue
        op = cmd[0]
        if op == 'M':
            shape.draw_line(fitz.Point(cmd[1], cmd[2]), fitz.Point(cmd[1], cmd[2]))
        elif op == 'L':
            # Draw line from previous point
            pass  # Complex path handling would go here
        elif op == 'Q':
            # Quadratic curve
            pass
    
    # For simplicity, just draw points as small circles for now
    shape.commit(color=color, fill=None, width=stroke_width)


def _add_rect_layer(page, layer: dict):
    """Add rectangle shape to page."""
    x = layer.get('left', 0)
    y = layer.get('top', 0)
    width = layer.get('width', 50) * layer.get('scaleX', 1)
    height = layer.get('height', 50) * layer.get('scaleY', 1)
    
    fill_hex = layer.get('fill', None)
    stroke_hex = layer.get('stroke', '#000000')
    
    rect = fitz.Rect(x, y, x + width, y + height)
    
    fill_color = hex_to_rgb(fill_hex) if fill_hex and fill_hex != 'transparent' else None
    stroke_color = hex_to_rgb(stroke_hex)
    
    shape = page.new_shape()
    shape.draw_rect(rect)
    shape.finish(color=stroke_color, fill=fill_color)
    shape.commit()


def _add_image_layer(page, layer: dict):
    """Add image to page from Base64 or bytes."""
    src = layer.get('src', '')
    if not src:
        return
        
    x = layer.get('left', 0)
    y = layer.get('top', 0)
    width = layer.get('width', 100)
    height = layer.get('height', 100)
    
    # Handle Base64
    import base64
    image_data = None
    
    if src.startswith('data:image'):
        # Extract base64 part
        try:
            base64_str = src.split(',')[1]
            image_data = base64.b64decode(base64_str)
        except Exception as e:
            print(f"Error decoding image: {e}")
            return
    elif src.startswith('http'):
        # Pass (not handling remote URLs yet for security)
        return
        
    if image_data:
        rect = fitz.Rect(x, y, x + width, y + height)
        try:
            page.insert_image(rect, stream=image_data)
        except Exception as e:
            print(f"Error inserting image: {e}")


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple (0-1 range)."""
    if not hex_color or hex_color == 'transparent':
        return (0, 0, 0)
    
    hex_color = hex_color.lstrip('#')
    
    # Handle rgba format
    if hex_color.startswith('rgba'):
        # Extract values
        import re
        match = re.search(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', hex_color)
        if match:
            return (int(match.group(1))/255, int(match.group(2))/255, int(match.group(3))/255)
        return (0, 0, 0)
    
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    
    try:
        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255
        return (r, g, b)
    except:
        return (0, 0, 0)


if __name__ == "__main__":
    # Test
    test_layers = [
        {
            "pageNum": 1,
            "type": "text",
            "text": "Hello from Python!",
            "left": 100,
            "top": 100,
            "fontSize": 24,
            "fill": "#FF0000"
        }
    ]
    # flatten_pdf_with_layers("input.pdf", test_layers, "output.pdf")
