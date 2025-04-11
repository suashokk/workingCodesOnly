import os
import re
import csv
import email
import datetime
from collections import defaultdict
from email import policy
from email.parser import BytesParser
from concurrent.futures import ProcessPoolExecutor, as_completed

# ---------- Logger ----------
def log(msg):
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

# ---------- Config Loader ----------
def read_config(filepath):
    countries = []
    eml_folder_path = ''
    hr_feed_path = ''
    
    try:
        with open(filepath, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if key.lower() == 'countries':
                    countries = [c.strip() for c in value.split(',') if c.strip()]
                elif key.lower() == 'emlfolderpath':
                    eml_folder_path = value
                elif key.lower() == 'hrfeedpath':
                    hr_feed_path = value
    except Exception as e:
        log(f"Config load error: {e}")
    return countries, eml_folder_path, hr_feed_path

# ---------- HR Feed Loader ----------
def load_hr_feed(path):
    email_country_map = {}
    try:
        with open(path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                email = row.get('email_address', '').strip()
                country = row.get('country', '').strip()
                if email and country:
                    email_country_map[email.lower()] = country
    except Exception as e:
        log(f"HR Feed load error: {e}")
    return email_country_map

# ---------- Email Extractor ----------
def extract_emails_from_eml(file_path):
    emails = set()
    try:
        with open(file_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)
            for header in ['From', 'To', 'Cc', 'Bcc']:
                values = msg.get_all(header, [])
                for item in values:
                    if isinstance(item, str):
                        for part in item.split(','):
                            match = re.search(r'[\w\.-]+@[\w\.-]+', part)
                            if match:
                                emails.add(match.group().lower())
    except Exception as e:
        log(f"Error parsing {file_path}: {e}")
    return emails

# ---------- File Processor ----------
def process_file(file_path, given_countries, email_country_map):
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    emails = extract_emails_from_eml(file_path)

    matched_emails = []
    unmatched_emails = []
    participant_countries = set()

    for email in emails:
        country = email_country_map.get(email)
        if country:
            participant_countries.add(country)
            if country in given_countries:
                matched_emails.append(email)
            else:
                unmatched_emails.append(email)

    isMatched = bool(matched_emails)
    isUnmatched = bool(unmatched_emails)
    isMatchedOnly = isMatched and not isUnmatched
    isUnmatchedOnly = isUnmatched and not isMatched
    category = 'Matched' if isMatchedOnly else 'Unmatched' if isUnmatchedOnly else 'Combo'

    isOnPrem = all(c in given_countries for c in participant_countries)
    isSaaS = all(c not in given_countries for c in participant_countries)
    classification = 'OnPrem Only' if isOnPrem else 'SaaS Only' if isSaaS else 'Combination'

    return {
        'file_name': file_name,
        'file_size': file_size,
        'matched_emails': matched_emails,
        'unmatched_emails': unmatched_emails,
        'isMatchedOnly': isMatchedOnly,
        'isUnmatchedOnly': isUnmatchedOnly,
        'category': category,
        'classification': classification
    }

# ---------- Main ----------
def main():
    config_path = './config.txt'  # Adjust as needed
    countries, eml_folder_path, hr_feed_path = read_config(config_path)
    email_country_map = load_hr_feed(hr_feed_path)

    matched_email_file_counter = 0
    unmatched_mail_file_counter = 0
    combo_file_counter = 0
    matched_email_file_size = 0
    unmatched_mail_file_size = 0
    combo_file_size = 0
    onprem_only_count = 0
    saas_only_count = 0
    combo_class_count = 0

    results = []

    log(f"Processing .eml files in: {eml_folder_path}")
    with ProcessPoolExecutor() as executor:
        futures = []
        for file in os.listdir(eml_folder_path):
            if file.lower().endswith('.eml'):
                full_path = os.path.join(eml_folder_path, file)
                futures.append(executor.submit(process_file, full_path, countries, email_country_map))

        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)

                if result['category'] == 'Matched':
                    matched_email_file_counter += 1
                    matched_email_file_size += result['file_size']
                elif result['category'] == 'Unmatched':
                    unmatched_mail_file_counter += 1
                    unmatched_mail_file_size += result['file_size']
                else:
                    combo_file_counter += 1
                    combo_file_size += result['file_size']

                if result['classification'] == 'OnPrem Only':
                    onprem_only_count += 1
                elif result['classification'] == 'SaaS Only':
                    saas_only_count += 1
                else:
                    combo_class_count += 1

            except Exception as e:
                log(f"Error in future result: {e}")

    report_file = os.path.join(eml_folder_path, 'eml_file_classification_report.csv')
    try:
        with open(report_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['File Name', 'File Size', 'Matched Emails', 'Unmatched Emails',
                             'isMatchedEmailFile', 'isNonmatchedEmailFile', 'Category', 'Participant Type Category'])
            for row in results:
                writer.writerow([
                    row['file_name'], row['file_size'],
                    ', '.join(row['matched_emails']),
                    ', '.join(row['unmatched_emails']),
                    row['isMatchedOnly'], row['isUnmatchedOnly'],
                    row['category'], row['classification']
                ])
        log(f"Report saved to: {report_file}")
    except Exception as e:
        log(f"Failed to write report: {e}")

    log("====== Final Summary ======")
    log(f"Matched Only Files   : {matched_email_file_counter} ({matched_email_file_size} bytes)")
    log(f"Unmatched Only Files : {unmatched_mail_file_counter} ({unmatched_mail_file_size} bytes)")
    log(f"Combo Files          : {combo_file_counter} ({combo_file_size} bytes)")
    log(f"OnPrem Only Messages : {onprem_only_count}")
    log(f"SaaS Only Messages   : {saas_only_count}")
    log(f"Combination Messages : {combo_class_count}")
    log("===========================")

if __name__ == "__main__":
    main()
