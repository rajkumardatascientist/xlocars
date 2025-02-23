import os
import secrets

# Generate a secret key if one doesn't exist
SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

DEBUG = True  # Disable in production

# Use Render's DATABASE_URL environment variable
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

if not SQLALCHEMY_DATABASE_URI:
    raise ValueError("❌ DATABASE_URL is not set. Please configure it in Render.")

SQLALCHEMY_TRACK_MODIFICATIONS = False
