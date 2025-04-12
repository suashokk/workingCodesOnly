import os import re import csv import logging import datetime from collections import defaultdict from email import policy from email.parser import BytesParser from concurrent.futures import ProcessPoolExecutor, as_completed

Setup logging

logging.basicConfig( level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s', handlers=[logging.StreamHandler()] )

def extract_unique_email_ids_from_eml(file_path): if not file_path or not os.path.isfile(file_path): logging.error(f"Invalid or missing file path: {file_path}") return file_path, set(), 0

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
email_set = set()
file_size = 0

try:
    with open(file_path, 'rb') as file:
        msg = BytesParser(policy=policy.default).parse(file)
        file_size = os.path.getsize(file_path)
        for header in ['from', 'to', 'cc', 'bcc']:
            if header in msg and msg[header]:
                matches = EMAIL_REGEX.findall(msg[header])
                email_set.update(email.lower() for email in matches if email)
except Exception as e:
    logging.error(f"Could not parse {file_path}: {e}", exc_info=True)
    print(f"[ERROR] Could not parse {file_path}: {e}", flush=True)

return file_path, email_set, file_size

def process_eml_file(args): file_path, onPremEmails, SAASEmails = args _, email_ids, file_size = extract_unique_email_ids_from_eml(file_path)

isOnPremFile = any(email in onPremEmails for email in email_ids)
isSaaSFile = any(email in SAASEmails for email in email_ids)

category = "none"
if isOnPremFile and isSaaSFile:
    category = "combo"
elif isOnPremFile:
    category = "onprem"
elif isSaaSFile:
    category = "saas"

return category, file_size

def extract_unique_emails_from_folder(folder_path, onPremEmails, SAASEmails): if not os.path.exists(folder_path) or not os.path.isdir(folder_path): logging.error(f"Invalid folder path: {folder_path}") return (0, 0, 0, 0, 0, 0)

eml_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(".eml")]

comboFileCounter = onPremFileCounter = saasFileCounter = 0
comboFileSizeCounter = onPremFileSizeCounter = saasFileSizeCounter = 0

with ProcessPoolExecutor() as executor:
    futures = [executor.submit(process_eml_file, (file_path, onPremEmails, SAASEmails)) for file_path in eml_files]
    for future in as_completed(futures):
        try:
            category, size = future.result()
            if category == "combo":
                comboFileCounter += 1
                comboFileSizeCounter += size
            elif category == "onprem":
                onPremFileCounter += 1
                onPremFileSizeCounter += size
            elif category == "saas":
                saasFileCounter += 1
                saasFileSizeCounter += size
        except Exception as e:
            logging.error(f"Worker failed: {e}", exc_info=True)

return (
    comboFileCounter, onPremFileCounter, saasFileCounter,
    comboFileSizeCounter, onPremFileSizeCounter, saasFileSizeCounter
)

def extract_emails_by_countries(csv_file, countries_str): try: target_countries = [c.strip().upper() for c in countries_str.split(",") if c.strip()] logging.info(f"Target countries parsed: {target_countries}") except Exception as e: logging.error(f"Error parsing target countries: {e}", exc_info=True) return set(), set()

onPremEmails = set()
SAASEmails = set()

try:
    with open(csv_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'COUNTRY' not in row or 'EMAIL_ADDRESS' not in row:
                logging.warning(f"Missing columns in row: {row}")
                continue

            country = row['COUNTRY']
            email = row['EMAIL_ADDRESS']

            if not country or not email:
                logging.debug(f"Skipping row with nulls: {row}")
                continue

            country = country.strip().upper()
            email = email.strip().lower()

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

def main(): start_time = datetime.datetime.now()

folder_path = "C:/Users/2006171/OneDrive - Standard Chartered Bank/Documents/20241119_12-00/Outlook"
csv_file = "C:/Users/2006171/OneDrive - Standard Chartered Bank/Documents/hrfeeds/ALL_COMMSUV_20241219_D_1.csv"
target_countries = "IND,CHN,SAU,TUR,ZMB,POL,FRA,SWE,DEU"

print(f"[{start_time}] Extracting matched country emails", flush=True)
onPremEmails, SAASEmails = extract_emails_by_countries(csv_file, target_countries)

comboFileCounter, onPremFileCounter, saasFileCounter, \
comboFileSizeCounter, onPremFileSizeCounter, saasFileSizeCounter = \
    extract_unique_emails_from_folder(folder_path, onPremEmails, SAASEmails)

print("comboFileCounter, onPremFileCounter, saasFileCounter :", comboFileCounter, onPremFileCounter, saasFileCounter)
print("comboFileSizeCounter, onPremFileSizeCounter, saasFileSizeCounter :", comboFileSizeCounter, onPremFileSizeCounter, saasFileSizeCounter)

print("Message contains participants only from OnPrem countries :", onPremFileCounter)
print("Message contains participants only from SaaS countries :", saasFileCounter)
print("Message contains participants with a combination of OnPrem and SaaS :", comboFileCounter)

end_time = datetime.datetime.now()
print(f"Start Time: {start_time}", flush=True)
print(f"End Time: {end_time}", flush=True)
print(f"Total Duration: {end_time - start_time}", flush=True)

if name == 'main': main()

