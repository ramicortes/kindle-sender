from dotenv import load_dotenv
import os
import sys
import configparser

def load_config():
    """Load configuration from .env file."""
    load_dotenv()  # Load environment variables from .env file

    config = {
        'Email': {
            'from_email': os.getenv('FROM_EMAIL', ''),
            'password': os.getenv('EMAIL_PASSWORD', ''),
            'kindle_email': os.getenv('KINDLE_EMAIL', ''),
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': os.getenv('SMTP_PORT', '587'),
        }
    }

    # Validate required fields
    if not config['Email']['from_email'] or not config['Email']['password'] or not config['Email']['kindle_email']:
        raise ValueError("Missing required email configuration in .env file.")

    return config
