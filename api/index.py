from os.path import dirname, join
import sys
import os

# Add the root directory to path so we can import from the app
sys.path.insert(0, dirname(dirname(__file__)))

# Import and configure the main app
from app import app

# This is necessary for Vercel's serverless environment
if __name__ == "__main__":
    app.run()
