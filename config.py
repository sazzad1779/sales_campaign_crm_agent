# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TOKEN_FILE = os.getenv('TOKEN_FILE')
CLIENT_SECRET_FILE = os.getenv('CLIENT_SECRET_FILE')
SHEET_ID = os.getenv('SHEET_ID')
GMAIL_USER_EMAIL = os.getenv('GMAIL_USER_EMAIL')
HUNTER_API_KEY = os.getenv('HUNTER_API_KEY')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 60))  # Default to 60 seconds if not set
