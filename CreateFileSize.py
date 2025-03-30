import os
import re
from email import policy
from email.parser import BytesParser

def load_email_ids(mapping_file):
    email_ids = set()
    with open(mapping_file, mode='r', encoding='utf-8') as f:
        next(f)  # Skip header
        for line in f:
            email = line.strip().split(",")[0]
            if email:
                email_ids.add(email.lower().strip())
    return email_ids

def file_contains_email(filepath, email_ids):
    try:
        with open(filepath, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)
        text = str(msg).lower()
        for email in email_ids:
            if email in text:
                return True
        return False
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False

def calculate_total_matching_size(input_folder, email_ids):
    total_size = 0
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(".eml"):
                full_path = os.path.join(root, file)
                if file_contains_email(full_path, email_ids):
                    total_size += os.path.getsize(full_path)
    return total_size

if __name__ == "__main__":
    mapping_file = "output_mapping.csv"
    input_folder = "input"  # Folder containing .eml files

    email_ids = load_email_ids(mapping_file)
    total_size_bytes = calculate_total_matching_size(input_folder, email_ids)
    total_size_mb = total_size_bytes / (1024 * 1024)

    print(f"\nTotal size of matching .eml files: {total_size_bytes} bytes ({total_size_mb:.2f} MB)")
