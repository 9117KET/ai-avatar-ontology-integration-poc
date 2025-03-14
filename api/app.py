from http.server import BaseHTTPRequestHandler
import os
import sys

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app
from api.index import app

# Create a handler class for Vercel
class VercelHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # This is just a wrapper - not actually used but needed for Vercel
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('Flask app is running'.encode('utf-8'))

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('POST to Flask app'.encode('utf-8'))

# Create a handler function for the serverless function
def handler(req, res):
    # Get the WSGI application
    def start_response(status, headers):
        res.statusCode = int(status.split(' ')[0])
        for header, value in headers:
            res.setHeader(header, value)
        return res.write

    # Run the Flask app
    return app(req, start_response) 