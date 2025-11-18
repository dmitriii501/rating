"""
WSGI entry point for production deployment (reg.ru, Apache, etc.)
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import create_app

app = create_app()
application = app

if __name__ == "__main__":
    app.run()

