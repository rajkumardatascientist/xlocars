# utils.py
import datetime
import re
from PIL import Image as PILImage
import pytesseract
import logging

def now():
    return datetime.datetime.utcnow()

def process_registration_card(image_file):
    """
    Processes the uploaded registration card image.

    Args:
        image_file: The uploaded image file object.

    Returns:
        A dictionary containing extracted data (registration_number, expiry_date, vin).
        Returns an empty dictionary if extraction fails.
    """
    try:
        img = PILImage.open(image_file)

        # 1. OCR the image
        text = pytesseract.image_to_string(img)
        logging.info(f"OCR Text: {text}")

        # 2. Extract Data (using regex or NLP)
        registration_number = extract_registration_number(text)
        expiry_date = extract_expiry_date(text)
        vin = extract_vin(text)

        # 3. Return the extracted data
        return {
            'registration_number': registration_number,
            'registration_expiry': expiry_date,
            'vin': vin
        }

    except Exception as e:
        logging.exception("Error in process_registration_card: %s", e)
        return {}  # Return empty dictionary in case of error


def extract_registration_number(text):
    """Extracts the registration number from the OCR text using regex."""
    # Example regex (adapt to your registration number format)
    match = re.search(r'[A-Z]{2}[ -]\d{1,2}[ -][A-Z]{1,2}[ -]\d{4}', text)
    return match.group(0) if match else None


def extract_expiry_date(text):
    """Extracts the expiry date from the OCR text using regex."""
    # Example regex (adapt to your date format)
    match = re.search(r'\d{2}[/-]\d{2}[/-]\d{4}', text)
    if match:
        try:
            date_object = datetime.datetime.strptime(match.group(0), '%d/%m/%Y').date()
            return date_object
        except ValueError:
            try:
                date_object = datetime.datetime.strptime(match.group(0), '%m/%d/%Y').date()
                return date_object
            except ValueError:
                return None
    return None


def extract_vin(text):
    """Extracts the VIN from the OCR text using regex."""
    # Example regex for a VIN
    match = re.search(r'[A-HJ-NPR-Z0-9]{17}', text)
    return match.group(0) if match else None