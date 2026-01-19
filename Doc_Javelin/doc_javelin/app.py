"""
Flask web application for Doc Javelin.
"""

import os
import uuid
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import tempfile
import shutil

from doc_javelin.tools import (
    merge_pdfs,
    img_to_pdf,
    pdf_to_word,
    pdf_to_excel
)

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=TEMPLATE_DIR)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(tempfile.gettempdir(), 'doc_javelin_uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(tempfile.gettempdir(), 'doc_javelin_outputs')

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {
    'pdf': {'pdf'},
    'images': {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'},
    'word': {'docx'},
    'excel': {'xlsx'}
}


def allowed_file(filename, file_type='pdf'):
    """Check if file extension is allowed."""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    if file_type == 'pdf':
        return ext in ALLOWED_EXTENSIONS['pdf']
    elif file_type == 'images':
        return ext in ALLOWED_EXTENSIONS['images']
    return ext in ALLOWED_EXTENSIONS.get(file_type, set())


@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')


@app.route('/merge')
def merge_page():
    """Merge PDFs page."""
    return render_template('merge.html')


@app.route('/img2pdf')
def img2pdf_page():
    """Image to PDF page."""
    return render_template('img2pdf.html')


@app.route('/pdf2word')
def pdf2word_page():
    """PDF to Word page."""
    return render_template('pdf2word.html')


@app.route('/pdf2excel')
def pdf2excel_page():
    """PDF to Excel page."""
    return render_template('pdf2excel.html')


@app.route('/api/merge', methods=['POST'])
def merge():
    """Merge PDFs endpoint."""
    try:
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files[]')
        if not files or all(f.filename == '' for f in files):
            return jsonify({'error': 'No files selected'}), 400
        
        # Save uploaded files
        temp_files = []
        for file in files:
            if file and file.filename and allowed_file(file.filename, 'pdf'):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
                file.save(filepath)
                temp_files.append(filepath)
        
        if not temp_files:
            return jsonify({'error': 'No valid PDF files provided'}), 400
        
        # Merge PDFs
        output_filename = f"merged_{uuid.uuid4()}.pdf"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        success = merge_pdfs(temp_files, output_path)
        
        # Cleanup temp files
        for temp_file in temp_files:
            try:
                os.remove(temp_file)
            except:
                pass
        
        if success:
            return jsonify({
                'success': True,
                'filename': output_filename,
                'message': f'Successfully merged {len(temp_files)} PDF(s)'
            })
        else:
            return jsonify({'error': 'Failed to merge PDFs'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/img2pdf', methods=['POST'])
def img2pdf():
    """Convert images to PDF endpoint."""
    try:
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files[]')
        separate = request.form.get('separate', 'false').lower() == 'true'
        
        if not files or all(f.filename == '' for f in files):
            return jsonify({'error': 'No files selected'}), 400
        
        # Save uploaded files
        temp_files = []
        for file in files:
            if file and file.filename and allowed_file(file.filename, 'images'):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
                file.save(filepath)
                temp_files.append(filepath)
        
        if not temp_files:
            return jsonify({'error': 'No valid image files provided'}), 400
        
        if separate:
            # Create separate PDFs
            output_files = []
            for temp_file in temp_files:
                base_name = os.path.splitext(os.path.basename(temp_file))[0]
                output_filename = f"{base_name}_{uuid.uuid4()}.pdf"
                output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
                
                success = img_to_pdf([temp_file], output_path, single_pdf_per_image=True)
                if success:
                    output_files.append(output_filename)
            
            # Cleanup
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except:
                    pass
            
            return jsonify({
                'success': True,
                'files': output_files,
                'message': f'Successfully converted {len(output_files)} image(s) to PDF(s)'
            })
        else:
            # Single PDF
            output_filename = f"images_{uuid.uuid4()}.pdf"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            success = img_to_pdf(temp_files, output_path, single_pdf_per_image=False)
            
            # Cleanup
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except:
                    pass
            
            if success:
                return jsonify({
                    'success': True,
                    'filename': output_filename,
                    'message': f'Successfully converted {len(temp_files)} image(s) to PDF'
                })
            else:
                return jsonify({'error': 'Failed to convert images to PDF'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pdf2word', methods=['POST'])
def pdf2word():
    """Convert PDF to Word endpoint."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file or not allowed_file(file.filename, 'pdf'):
            return jsonify({'error': 'Invalid PDF file'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
        file.save(filepath)
        
        # Convert to Word
        output_filename = f"{os.path.splitext(filename)[0]}_{uuid.uuid4()}.docx"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        success = pdf_to_word(filepath, output_path)
        
        # Cleanup
        try:
            os.remove(filepath)
        except:
            pass
        
        if success:
            return jsonify({
                'success': True,
                'filename': output_filename,
                'message': 'Successfully converted PDF to Word'
            })
        else:
            return jsonify({'error': 'Failed to convert PDF to Word'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pdf2excel', methods=['POST'])
def pdf2excel():
    """Convert PDF to Excel endpoint."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file or not allowed_file(file.filename, 'pdf'):
            return jsonify({'error': 'Invalid PDF file'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{filename}")
        file.save(filepath)
        
        # Convert to Excel
        output_filename = f"{os.path.splitext(filename)[0]}_{uuid.uuid4()}.xlsx"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        success = pdf_to_excel(filepath, output_path)
        
        # Cleanup
        try:
            os.remove(filepath)
        except:
            pass
        
        if success:
            return jsonify({
                'success': True,
                'filename': output_filename,
                'message': 'Successfully converted PDF to Excel'
            })
        else:
            return jsonify({'error': 'Failed to convert PDF to Excel'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<filename>')
def download(filename):
    """Download converted file."""
    try:
        return send_from_directory(
            app.config['OUTPUT_FOLDER'],
            filename,
            as_attachment=True
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 100MB'}), 413


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

