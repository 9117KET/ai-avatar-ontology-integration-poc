from http.server import BaseHTTPRequestHandler
import os
import sys
import json
import base64
from urllib.parse import parse_qs, urlparse

# Add project root to path
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_path)

# Ensure /tmp is available for NLTK data
os.makedirs('/tmp/nltk_data', exist_ok=True)

# Import the Flask app
from api.index import app

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests by passing to Flask app"""
        # Parse the URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        # Set up the WSGI environment
        environ = {
            'wsgi.input': None,
            'wsgi.errors': sys.stderr,
            'wsgi.version': (1, 0),
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'wsgi.url_scheme': 'https',
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': path,
            'QUERY_STRING': parsed_url.query,
            'SERVER_NAME': self.server.server_name,
            'SERVER_PORT': str(self.server.server_port),
            'SERVER_PROTOCOL': self.request_version,
        }
        
        # Add headers
        for name, value in self.headers.items():
            key = f'HTTP_{name.replace("-", "_").upper()}'
            environ[key] = value
        
        # Capture the Flask response
        response_body = []
        def start_response(status, response_headers, exc_info=None):
            # Get the status code
            status_code = int(status.split(' ')[0])
            self.send_response(status_code)
            
            # Add response headers
            for name, value in response_headers:
                self.send_header(name, value)
            self.end_headers()
            
            # Return a function to append to the response body
            return lambda data: response_body.append(data)
        
        # Call the Flask app
        result = app(environ, start_response)
        
        # Send the response
        for data in result:
            if data:  # Don't write empty strings
                self.wfile.write(data)
        
        # Close the iterator if needed
        if hasattr(result, 'close'):
            result.close()

    def do_POST(self):
        """Handle POST requests by passing to Flask app"""
        # Get the request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length else None
        
        # Parse the URL
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Set up the WSGI environment
        environ = {
            'wsgi.input': body,
            'wsgi.errors': sys.stderr,
            'wsgi.version': (1, 0),
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'wsgi.url_scheme': 'https',
            'REQUEST_METHOD': 'POST',
            'PATH_INFO': path,
            'QUERY_STRING': parsed_url.query,
            'CONTENT_TYPE': self.headers.get('Content-Type', ''),
            'CONTENT_LENGTH': str(content_length),
            'SERVER_NAME': self.server.server_name,
            'SERVER_PORT': str(self.server.server_port),
            'SERVER_PROTOCOL': self.request_version,
        }
        
        # Add headers
        for name, value in self.headers.items():
            key = f'HTTP_{name.replace("-", "_").upper()}'
            environ[key] = value
        
        # Capture the Flask response
        response_body = []
        def start_response(status, response_headers, exc_info=None):
            # Get the status code
            status_code = int(status.split(' ')[0])
            self.send_response(status_code)
            
            # Add response headers
            for name, value in response_headers:
                self.send_header(name, value)
            self.end_headers()
            
            # Return a function to append to the response body
            return lambda data: response_body.append(data)
        
        # Call the Flask app
        result = app(environ, start_response)
        
        # Send the response
        for data in result:
            if data:  # Don't write empty strings
                self.wfile.write(data)
        
        # Close the iterator if needed
        if hasattr(result, 'close'):
            result.close() 