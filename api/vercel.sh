#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Run NLTK downloader
python nltk.py

# Create necessary directories
mkdir -p nltk_data
mkdir -p data/students

echo "Vercel build script completed successfully." 