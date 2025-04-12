import csv
import logging

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def extract_emails_by_countries(csv_file, countries_str):
    """
    Extract emails and classify them into OnPrem and SaaS based on country match.
    """
    # Parse input countries list and clean whitespace
    try:
        target_countries = [c.strip().upper() for c in countries_str.split(",") if c.strip()]
        logging.info(f"Target countries parsed: {target_countries}")
    except Exception as e:
        logging.error(f"Error parsing target countries: {e}", exc_info=True)
        return set(), set()

    onPremEmails = set()
    SAASEmails = set()

    # Read the CSV and classify emails
    try:
        with open(csv_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Validate row keys
                if 'COUNTRY' not in row or 'EMAIL_ADDRESS' not in row:
                    logging.warning(f"Missing columns in row: {row}")
                    continue

                # Extract and clean country and email fields
                country = row['COUNTRY']
                email = row['EMAIL_ADDRESS']

                if not country or not email:
                    logging.debug(f"Skipping row with nulls: {row}")
                    continue

                country = country.strip().upper()
                email = email.strip().lower()

                # Classify email into OnPrem or SaaS
                if country in target_countries:
                    onPremEmails.add(email)
                else:
                    SAASEmails.add(email)

    except FileNotFoundError:
        logging.error(f"CSV file not found: {csv_file}")
    except Exception as e:
        logging.error(f"Error reading CSV file {csv_file}: {e}", exc_info=True)
        print(f"[ERROR] Issue reading CSV: {e}", flush=True)

    return set(onPremEmails), set(SAASEmails)
