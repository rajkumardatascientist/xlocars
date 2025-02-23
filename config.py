import os
import secrets

# Generate a secret key if one doesn't exist
SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

DEBUG = True  # Disable in production

# Use DATABASE_URL from Render, if available
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    SQLALCHEMY_DATABASE_URI = DATABASE_URL  # Use Render's environment variable
else:
    # Manually construct the database URL if not provided
    DB_USER = os.environ.get('DB_USER', 'root')  # Default to 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '1234')  # Default to '1234'
    DB_HOST = os.environ.get('DB_HOST', 'localhost')  # Default to localhost
    DB_PORT = os.environ.get('DB_PORT', '5432')  # Default to 5432
    DB_NAME = os.environ.get('DB_NAME', 'zingcars')  # Default to 'zingcars'

    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

SQLALCHEMY_TRACK_MODIFICATIONS = False
