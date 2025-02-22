import os
import secrets

# Generate a secret key if not set
SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Use Railway-provided DATABASE_URL
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

if not SQLALCHEMY_DATABASE_URI:
    print("⚠️ DATABASE_URL is not set! Make sure it's configured in Railway.")

SQLALCHEMY_TRACK_MODIFICATIONS = False
