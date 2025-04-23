import nltk
import os

# Check if running on Vercel (read-only filesystem)
is_vercel = os.environ.get('VERCEL') == '1'
if is_vercel:
    nltk_data_dir = '/tmp/nltk_data'
else:
    nltk_data_dir = os.path.join(os.path.dirname(__file__), 'nltk_data')

# Create the directory for NLTK data
os.makedirs(nltk_data_dir, exist_ok=True)

# Set the NLTK data path
nltk.data.path.append(nltk_data_dir)

# Download the necessary NLTK data
nltk.download('punkt', download_dir=nltk_data_dir) 