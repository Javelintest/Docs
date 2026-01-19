# Doc Javelin 🎯

A comprehensive document conversion and manipulation tool built with Python. Doc Javelin helps you convert between different document formats and perform various file operations.

## Features

- 📄 **PDF Merge** - Combine multiple PDF files into one
- 🖼️ **Image to PDF** - Convert images (JPG, PNG, GIF, BMP, TIFF, WEBP) to PDF format
- 📝 **PDF to Word** - Extract text from PDFs and convert to Word documents (.docx)
- 📊 **PDF to Excel** - Extract tables from PDFs and convert to Excel spreadsheets (.xlsx)

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

#### Merge PDFs

Merge multiple PDF files into a single PDF:

```bash
python -m doc_javelin.cli merge file1.pdf file2.pdf file3.pdf -o merged.pdf
```

#### Convert Images to PDF

Convert one or more images to PDF:

```bash
# Single PDF with all images
python -m doc_javelin.cli img2pdf image1.jpg image2.png -o output.pdf

# Separate PDF for each image
python -m doc_javelin.cli img2pdf image1.jpg image2.png -o output_dir/ -s
```

#### Convert PDF to Word

Extract text from PDF and convert to Word document:

```bash
python -m doc_javelin.cli pdf2word document.pdf -o output.docx
```

#### Convert PDF to Excel

Extract tables from PDF and convert to Excel:

```bash
python -m doc_javelin.cli pdf2excel data.pdf -o output.xlsx
```

### Python API

You can also use Doc Javelin as a Python library:

```python
from doc_javelin.tools import merge_pdfs, img_to_pdf, pdf_to_word, pdf_to_excel

# Merge PDFs
merge_pdfs(['file1.pdf', 'file2.pdf'], 'merged.pdf')

# Convert images to PDF
img_to_pdf(['image1.jpg', 'image2.png'], 'output.pdf')

# Convert PDF to Word
pdf_to_word('document.pdf', 'output.docx')

# Convert PDF to Excel
pdf_to_excel('data.pdf', 'output.xlsx')
```

## Supported Formats

### Input Formats
- **PDF**: `.pdf`
- **Images**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`

### Output Formats
- **PDF**: `.pdf`
- **Word**: `.docx`
- **Excel**: `.xlsx`

## Project Structure

```
Doc_Javelin/
├── doc_javelin/
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   └── tools/
│       ├── __init__.py
│       ├── pdf_merger.py   # PDF merging functionality
│       ├── img_to_pdf.py   # Image to PDF conversion
│       ├── pdf_to_word.py  # PDF to Word conversion
│       └── pdf_to_excel.py # PDF to Excel conversion
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Requirements

- Python 3.8 or higher
- See `requirements.txt` for package dependencies

## Notes

- **PDF to Word/Excel**: The current implementation uses basic text extraction. For complex PDFs with advanced formatting, tables, or images, the output may not preserve all original formatting. For better results, consider using specialized libraries like `pdf2docx` or `tabula-py`.
- **Image to PDF**: Supports common image formats. RGBA images are automatically converted to RGB with white background.

## Contributing

Contributions are welcome! Feel free to add more conversion tools and improve existing functionality.

## License

This project is open source and available for personal and commercial use.

## Future Enhancements

- [ ] PDF splitting
- [ ] PDF rotation and manipulation
- [ ] Word to PDF conversion
- [ ] Excel to PDF conversion
- [ ] Batch processing
- [ ] GUI interface
- [ ] Advanced table extraction from PDFs
- [ ] OCR support for scanned documents

