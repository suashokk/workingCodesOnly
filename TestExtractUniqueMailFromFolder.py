import os
import logging
from collections import defaultdict
from your_module import extract_unique_email_ids_from_eml  # Adjust based on actual import

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def extract_unique_emails_from_folder(folder_path, onPremEmails, SAASEmails):
    """
    Segregate emails from .eml files into OnPrem, SaaS or Combo categories.
    """
    # File and size counters
    onPremFileCounter = comboFileCounter = saasFileCounter = 0
    onPremFileSizeCounter = comboFileSizeCounter = saasFileSizeCounter = 0

    # Email tracking
    all_email_ids = set()
    email_to_files = defaultdict(set)

    # Check for folder existence
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        logging.error(f"Invalid folder path: {folder_path}")
        return (0, 0, 0, 0, 0, 0)

    # Iterate over files
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".eml"):
            try:
                file_path = os.path.join(folder_path, filename)
                file_size = os.path.getsize(file_path)
                email_ids = extract_unique_email_ids_from_eml(file_path)

                print(f"[INFO] Processing {filename} | Emails: {email_ids}", flush=True)

                # Set flags for type
                isOnPremFile = any(email in onPremEmails for email in email_ids)
                isSaaSFile = any(email in SAASEmails for email in email_ids)

                # Categorize based on flags
                if isOnPremFile and isSaaSFile:
                    comboFileCounter += 1
                    comboFileSizeCounter += file_size
                    logging.info(f"Combo file detected: {filename}")
                elif isOnPremFile:
                    onPremFileCounter += 1
                    onPremFileSizeCounter += file_size
                    logging.info(f"OnPrem file detected: {filename}")
                elif isSaaSFile:
                    saasFileCounter += 1
                    saasFileSizeCounter += file_size
                    logging.info(f"SaaS file detected: {filename}")

                # Track all emails
                all_email_ids.update(email_ids)

            except Exception as e:
                logging.error(f"Failed to process {filename}: {e}", exc_info=True)
                print(f"[ERROR] Failed to process {filename}: {e}", flush=True)

    return (
        comboFileCounter, onPremFileCounter, saasFileCounter,
        comboFileSizeCounter, onPremFileSizeCounter, saasFileSizeCounter
    )
