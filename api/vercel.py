"""
Vercel serverless function handler for the AI Tutoring System.
This file provides the necessary wrapper for deploying the Flask app to Vercel.
"""

from http.server import BaseHTTPRequestHandler
import os
import sys

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app
from app import app

class VercelHandler(BaseHTTPRequestHandler):
    """Handler class for Vercel serverless functions."""
    
    def do_GET(self):
        """Handle GET requests."""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('Flask app is running'.encode('utf-8'))

    def do_POST(self):
        """Handle POST requests."""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('POST to Flask app'.encode('utf-8'))

def handler(req, res):
    """
    Vercel serverless function handler.
    
    Args:
        req: The request object
        res: The response object
    
    Returns:
        The Flask application response
    """
    def start_response(status, headers):
        res.statusCode = int(status.split(' ')[0])
        for header, value in headers:
            res.setHeader(header, value)
        return res.write

    return app(req, start_response) 