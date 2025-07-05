import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')

# Gemini Pro API Key (replace with environment variable in production)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyBOoGu3bZcOmlSVRCvETvRdf7kOGj3hd40')