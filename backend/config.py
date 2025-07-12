import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv is optional
    pass

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')

# Gemini Pro API Key (replace with environment variable in production)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyBOoGu3bZcOmlSVRCvETvRdf7kOGj3hd40')

LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Optional Telegram integration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Cleanup behavior
CLEANUP_TMP = bool(int(os.getenv('CLEANUP_TMP', '1')))