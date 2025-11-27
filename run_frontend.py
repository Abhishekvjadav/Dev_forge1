#!/usr/bin/env python3
"""
Run Frontend Server Only (UI on port 8001)

This script serves just the frontend static files on port 8001.
Make sure the backend is running on port 8000.

Usage:
    python run_frontend.py
"""

import os
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import time

class CORSRequestHandler(SimpleHTTPRequestHandler):
    """HTTP handler with CORS support for development"""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def translate_path(self, path):
        """Serve index.html for all HTML file requests"""
        if path == '/' or not path.endswith(('.js', '.css', '.png', '.jpg', '.svg', '.json')):
            path = '/index.html'
        return super().translate_path(path)
    
    def log_message(self, format, *args):
        """Simplified logging"""
        print(f"[{self.log_date_time_string()}] {format % args}")


if __name__ == "__main__":
    # Change to static directory
    static_dir = Path(__file__).parent / "app" / "static"
    
    if not static_dir.exists():
        print("❌ Error: app/static directory not found!")
        print(f"Expected: {static_dir}")
        exit(1)
    
    os.chdir(static_dir)
    
    PORT = 8001
    
    print("=" * 60)
    print("🎨 STARTING HYBRID SEARCH FRONTEND")
    print("=" * 60)
    print(f"✓ Frontend available at: http://localhost:{PORT}")
    print(f"✓ Serving files from: {static_dir}")
    print("✓ Make sure backend is running on port 8000")
    print("=" * 60)
    print()
    
    server = HTTPServer(('0.0.0.0', PORT), CORSRequestHandler)
    
    try:
        # Try to open browser
        time.sleep(0.5)
        webbrowser.open(f'http://localhost:{PORT}')
        print(f"🌐 Opening http://localhost:{PORT} in your browser...")
        print()
    except:
        pass
    
    try:
        print(f"Server running. Press Ctrl+C to stop.")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Frontend server stopped")
