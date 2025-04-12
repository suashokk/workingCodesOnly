import re
import os
import logging
from email import policy
from email.parser import BytesParser

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def extract_unique_email_ids_from_eml(file_path):
    """
    Extract unique email IDs from an .eml file.
    """
    # Validate file path
    if not file_path or not os.path.isfile(file_path):
        logging.error(f"Invalid or missing file path: {file_path}")
        return set()

    # Compile email regex
    EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')

    # Initialize an empty set to store unique email addresses
    email_set = set()

    try:
        # Open the .eml file in binary mode
        with open(file_path, 'rb') as file:
            # Parse email message
            msg = BytesParser(policy=policy.default).parse(file)
            logging.info(f"Parsed file: {file_path}")

            # Headers to check for email addresses
            for header in ['from', 'to', 'cc', 'bcc']:
                # Check if header is present
                if header in msg and msg[header]:
                    # Extract email addresses using regex
                    matches = EMAIL_REGEX.findall(msg[header])
                    logging.debug(f"Found in {header}: {matches}")

                    # Add lowercase email IDs to the set
                    email_set.update(email.lower() for email in matches if email)
                else:
                    logging.debug(f"No data found in header: {header}")

    except Exception as e:
        # Handle any unexpected error during parsing
        logging.error(f"Could not parse {file_path}: {e}", exc_info=True)
        print(f"[ERROR] Could not parse {file_path}: {e}", flush=True)

    # Return the set of unique email addresses
    return email_set
