#!/usr/bin/env python3
"""
Simple script to run the Doc Javelin web server.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from doc_javelin.app import app

if __name__ == '__main__':
    print("=" * 60)
    print("Doc Javelin Web Server")
    print("=" * 60)
    print("\nStarting server on http://0.0.0.0:5000")
    print("Visit http://localhost:5000 in your browser")
    print("\nPress CTRL+C to stop the server\n")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)

