import nltk
import os

# Create the directory for NLTK data
os.makedirs(os.path.join(os.path.dirname(__file__), 'nltk_data'), exist_ok=True)

# Set the NLTK data path
nltk.data.path.append(os.path.join(os.path.dirname(__file__), 'nltk_data'))

# Download the necessary NLTK data
nltk.download('punkt', download_dir=os.path.join(os.path.dirname(__file__), 'nltk_data')) 