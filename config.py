import os
import secrets

# Generate a secret key if one doesn't exist
SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
# It's highly recommended to set the SECRET_KEY environment variable in production.

DEBUG = True  # Disable in production

# Get database credentials from environment variables
DB_USER = os.environ.get('DB_USER', 'root')  # Default to 'root'
DB_PASSWORD = os.environ.get('DB_PASSWORD', '1234')  # Default to '1234'
DB_HOST = os.environ.get('DB_HOST', 'localhost')  # Default to localhost
DB_PORT = os.environ.get('DB_PORT', '5432')  # Default to 5432
DB_NAME = os.environ.get('DB_NAME', 'zingcars')  # Default to 'zingcars'

# Construct the SQLAlchemy database URI
SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Print the database URI for verification (remove in production)
print(f"SQLALCHEMY_DATABASE_URI: {SQLALCHEMY_DATABASE_URI}")

SQLALCHEMY_TRACK_MODIFICATIONS = False