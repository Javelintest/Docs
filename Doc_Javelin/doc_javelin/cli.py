"""
Command-line interface for Doc Javelin.
"""

import argparse
import sys
import os
from pathlib import Path

from doc_javelin.tools import (
    merge_pdfs,
    img_to_pdf,
    pdf_to_word,
    pdf_to_excel
)


def create_parser():
    """Create command-line argument parser."""
    parser = argparse.ArgumentParser(
        description='Doc Javelin - Document conversion and manipulation tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Merge PDFs
  python -m doc_javelin.cli merge file1.pdf file2.pdf -o merged.pdf
  
  # Convert images to PDF
  python -m doc_javelin.cli img2pdf image1.jpg image2.png -o output.pdf
  
  # Convert PDF to Word
  python -m doc_javelin.cli pdf2word document.pdf -o output.docx
  
  # Convert PDF to Excel
  python -m doc_javelin.cli pdf2excel data.pdf -o output.xlsx
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Merge PDFs command
    merge_parser = subparsers.add_parser('merge', help='Merge multiple PDF files')
    merge_parser.add_argument('files', nargs='+', help='PDF files to merge')
    merge_parser.add_argument('-o', '--output', required=True, help='Output PDF file path')
    
    # Image to PDF command
    img2pdf_parser = subparsers.add_parser('img2pdf', help='Convert images to PDF')
    img2pdf_parser.add_argument('images', nargs='+', help='Image files to convert')
    img2pdf_parser.add_argument('-o', '--output', required=True, help='Output PDF file path')
    img2pdf_parser.add_argument('-s', '--separate', action='store_true', 
                                help='Create separate PDF for each image')
    
    # PDF to Word command
    pdf2word_parser = subparsers.add_parser('pdf2word', help='Convert PDF to Word')
    pdf2word_parser.add_argument('pdf', help='Input PDF file')
    pdf2word_parser.add_argument('-o', '--output', required=True, help='Output Word file path (.docx)')
    
    # PDF to Excel command
    pdf2excel_parser = subparsers.add_parser('pdf2excel', help='Convert PDF to Excel')
    pdf2excel_parser.add_argument('pdf', help='Input PDF file')
    pdf2excel_parser.add_argument('-o', '--output', required=True, help='Output Excel file path (.xlsx)')
    pdf2excel_parser.add_argument('-s', '--sheet', default='Sheet1', help='Excel sheet name')
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'merge':
            success = merge_pdfs(args.files, args.output)
            if success:
                print(f"✓ Successfully merged {len(args.files)} PDF(s) into {args.output}")
            else:
                print("✗ Failed to merge PDFs")
                sys.exit(1)
        
        elif args.command == 'img2pdf':
            success = img_to_pdf(args.images, args.output, args.separate)
            if success:
                if args.separate:
                    print(f"✓ Successfully converted {len(args.images)} image(s) to PDF(s)")
                else:
                    print(f"✓ Successfully converted {len(args.images)} image(s) to {args.output}")
            else:
                print("✗ Failed to convert images to PDF")
                sys.exit(1)
        
        elif args.command == 'pdf2word':
            success = pdf_to_word(args.pdf, args.output)
            if success:
                print(f"✓ Successfully converted {args.pdf} to {args.output}")
            else:
                print("✗ Failed to convert PDF to Word")
                sys.exit(1)
        
        elif args.command == 'pdf2excel':
            success = pdf_to_excel(args.pdf, args.output, args.sheet)
            if success:
                print(f"✓ Successfully converted {args.pdf} to {args.output}")
            else:
                print("✗ Failed to convert PDF to Excel")
                sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n✗ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()

