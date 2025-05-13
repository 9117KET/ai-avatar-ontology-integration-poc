from os.path import dirname, join
import sys
import os

# Add the root directory to path so we can import from the app
sys.path.insert(0, dirname(dirname(__file__)))

# Import and configure the main app
from app import app
from serverless_wsgi import handle_request

def handler(event, context):
    return handle_request(app, event, context)
