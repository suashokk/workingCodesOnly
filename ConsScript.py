import os 
import re 
import csv 
import email 
import datetime 
from collections import defaultdict
from email import policy 
from email.parser import BytesParser 
from concurrent.futures import ProcessPoolExecutor, as_completed

def extract_unique_email_ids_from_eml(file_path): unique_emails = set() try: with open(file_path, 'r', errors='ignore') as f: content = f.read() email_ids = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+.[a-zA-Z0-9-.]+', content) unique_emails.update(email_ids) except Exception as e: print(f"[ERROR] Failed to parse {file_path}: {e}", flush=True) return unique_emails

def extract_unique_emails_from_folder(folder_path): all_email_ids = set() email_to_files = defaultdict(set) matched_files = set() unmatched_files = set() matched_file_sizes = 0 unmatched_file_sizes = 0

for filename in os.listdir(folder_path):
    if filename.lower().endswith(".eml"):
        file_path = os.path.join(folder_path, filename)
        email_ids = extract_unique_email_ids_from_eml(file_path)
        all_email_ids.update(email_ids)
        found_match = False
        for email_id in set(email_ids):
            email_to_files[email_id.lower()].add(filename)
        # This placeholder check will be replaced in main after matched_emails is known
return all_email_ids, email_to_files

def extract_emails_by_countries(csv_file, countries_str): target_countries = [c.strip().lower() for c in countries_str.split(",")] emails = [] with open(csv_file, mode='r', encoding='utf-8') as f: reader = csv.DictReader(f) for row in reader: country = row['COUNTRY'].strip().lower() email = row['EMAIL ADDRESS'].strip() if country in target_countries: emails.append(email.lower()) return emails

def save_emails_to_txt(email_list, output_file): with open(output_file, mode='w', encoding='utf-8') as f: for email in email_list: f.write(email + '\n')

def save_email_file_counts(email_to_files, output_file): with open(output_file, mode='w', newline='', encoding='utf-8') as f: writer = csv.writer(f) writer.writerow(['EMAIL', 'FILE_COUNT']) for email, files in email_to_files.items(): writer.writerow([email, len(files)])

def save_file_stats(folder_path, matched_emails, email_to_files): matched_files = set() unmatched_files = set() matched_size = 0 unmatched_size = 0

for filename in os.listdir(folder_path):
    if filename.lower().endswith(".eml"):
        file_path = os.path.join(folder_path, filename)
        emails_in_file = extract_unique_email_ids_from_eml(file_path)
        is_matched = any(email.lower() in matched_emails for email in emails_in_file)
        file_size = os.path.getsize(file_path)

        if is_matched:
            matched_files.add(filename)
            matched_size += file_size
        else:
            unmatched_files.add(filename)
            unmatched_size += file_size

print(f"[STATS] Matched Files: {len(matched_files)}, Size: {matched_size / 1024:.2f} KB")
print(f"[STATS] Unmatched Files: {len(unmatched_files)}, Size: {unmatched_size / 1024:.2f} KB")

def main(): folder_path = "/your/eml/folder" csv_file = "/your/mapping.csv" target_countries = "IND,USA,POL,FRA,DEU"

print(f"[{datetime.datetime.now()}] Extracting emails from .eml files", flush=True)
all_email_ids, email_to_files = extract_unique_emails_from_folder(folder_path)

print(f"[{datetime.datetime.now()}] Extracting matched country emails", flush=True)
matched_emails = set(extract_emails_by_countries(csv_file, target_countries))

all_email_ids_lower = set(e.lower() for e in all_email_ids)
matched = all_email_ids_lower & matched_emails
unmatched = all_email_ids_lower - matched

print(f"[FINAL] Matched emails (by country): {len(matched)}")
print(f"[FINAL] Unmatched emails (not in country list): {len(unmatched)}")
print(f"[FINAL] Email->File relationships: {len(email_to_files)}")
print(f"[FINAL] Total .eml files scanned: {len(os.listdir(folder_path))}")

# Save outputs
save_emails_to_txt(matched, "matched_emails.txt")
save_emails_to_txt(unmatched, "unmatched_emails.txt")
save_email_file_counts(email_to_files, "email_file_counts.csv")

# Save file stats
save_file_stats(folder_path, matched_emails, email_to_files)

if name == 'main': main()

