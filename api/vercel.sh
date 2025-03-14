#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Run NLTK downloader
python nltk.py

# Create necessary directories in /tmp (the only writable location in Vercel)
mkdir -p /tmp/nltk_data
mkdir -p /tmp/data/students

echo "Vercel build script completed successfully." 