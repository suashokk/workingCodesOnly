import os
import email
from email import policy
from email.parser import BytesParser

def load_filtered_emails(file_path):
    import codecs
    with codecs.open(file_path, 'r', encoding='utf-8') as f:
        return set([line.strip().lower() for line in f if line.strip()])

def file_contains_any_email(filepath, email_set):
    try:
        with open(filepath, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)
            text = str(msg)
            for email in email_set:
                if email in text:
                    return True
    except Exception as e:
        print("Error reading {}: {}".format(filepath, str(e)))
    return False

def scan_eml_files(folder_path, email_set):
    total_files = 0
    matched_files = 0

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".eml"):
                total_files += 1
                full_path = os.path.join(root, file)
                if file_contains_any_email(full_path, email_set):
                    matched_files += 1

    return matched_files, total_files

if __name__ == "__main__":
    filtered_email_file = "/nas04/hrtest/filtered_emails.txt"
    eml_folder = "/nas01/datacollection/dailyfeeds/emails/download/20250401_12-00"  # Folder with .eml files

    filtered_emails = load_filtered_emails(filtered_email_file)
    matched, total = scan_eml_files(eml_folder, filtered_emails)

    print("\nMatched .eml file(s): {} / {}".format(matched, total))
