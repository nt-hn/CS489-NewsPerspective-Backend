import os
from dotenv import load_dotenv

if os.getenv('RAILWAY_ENVIRONMENT') is None:
    load_dotenv()

class Config:
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    PORT = int(os.getenv('PORT', 5000))
    HOST = '0.0.0.0'
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
