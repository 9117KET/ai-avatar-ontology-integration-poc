"""
Vercel serverless function handler for the AI Tutoring System.
This file provides the necessary wrapper for deploying the Quart ASGI app to Vercel.
"""

import os
import sys
import json
import base64
from urllib.parse import parse_qs

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Quart app
from app import app

# ASGI handler for Vercel
async def handler(request, response):
    """
    Vercel serverless function handler for ASGI applications.
    
    This function converts Vercel's request/response objects to the ASGI format
    and processes them through our Quart application.
    
    Args:
        request: The Vercel request object
        response: The Vercel response object
    
    Returns:
        The processed response from the Quart application
    """
    try:
        # Extract request info
        method = request.get('method', 'GET')
        url = request.get('url', '/')
        headers = request.get('headers', {})
        
        # Process body if present
        body = b''
        if 'body' in request and request['body']:
            if request.get('encoding') == 'base64':
                body = base64.b64decode(request['body'])
            else:
                body = request['body'].encode('utf-8')
        
        # Prepare the ASGI scope
        scope = {
            'type': 'http',
            'asgi': {
                'version': '3.0',
                'spec_version': '2.1'
            },
            'http_version': '1.1',
            'method': method,
            'scheme': 'https',
            'path': url.split('?')[0],
            'query_string': url.split('?')[1].encode('utf-8') if '?' in url else b'',
            'headers': [(k.lower().encode('utf-8'), v.encode('utf-8')) 
                        for k, v in headers.items()],
            'client': ('0.0.0.0', 0),
            'server': ('vercel', 0)
        }
        
        # Create a response dictionary to store the response data
        result = {
            'statusCode': 200,
            'headers': {},
            'body': '',
            'encoding': 'utf-8'
        }
        
        # Define ASGI receive function
        async def receive():
            return {
                'type': 'http.request',
                'body': body,
                'more_body': False
            }
        
        # Define ASGI send function
        async def send(message):
            if message['type'] == 'http.response.start':
                result['statusCode'] = message['status']
                result['headers'] = {
                    k.decode('utf-8'): v.decode('utf-8')
                    for k, v in message['headers']
                }
            elif message['type'] == 'http.response.body':
                if message.get('body', b''):
                    if isinstance(message['body'], str):
                        result['body'] += message['body']
                    else:
                        result['body'] += message['body'].decode('utf-8')
        
        # Call the ASGI application
        await app(scope, receive, send)
        
        # Set the response
        for key, value in result['headers'].items():
            response.setHeader(key, value)
        response.statusCode = result['statusCode']
        
        # Return the body
        return result['body']
    
    except Exception as e:
        # Error handling
        print(f"Error in Vercel handler: {str(e)}")
        response.statusCode = 500
        return json.dumps({"error": "Internal Server Error", "details": str(e)})
