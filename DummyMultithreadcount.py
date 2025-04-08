import os
from email import policy
from email.parser import BytesParser
from concurrent.futures import ProcessPoolExecutor, as_completed

def load_filtered_emails(file_path):
    print(f"[INFO] Loading filtered emails from: {file_path}")
    if not file_path or not os.path.isfile(file_path):
        print(f"[ERROR] Invalid or missing file path: {file_path}")
        return set()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            emails = set(
                line.strip().lower()
                for line in f
                if line and line.strip()
            )
            print(f"[INFO] Loaded {len(emails)} filtered emails.")
            return emails
    except Exception as e:
        print(f"[ERROR] Error reading filtered emails: {e}")
        return set()

def file_contains_any_email(args):
    file_path, email_set = args
    if not file_path or not os.path.isfile(file_path) or not email_set:
        return False

    try:
        with open(file_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)
            text = str(msg).lower()
            for email in email_set:
                if email in text:
                    print(f"[MATCH] Found match in file: {file_path}")
                    return True
            return False
    except Exception as e:
        print(f"[WARNING] Failed to read/parse file: {file_path} - {e}")
        return False

def scan_eml_files_parallel(folder_path, email_set, max_workers=8):
    print(f"[INFO] Scanning folder: {folder_path}")
    if not folder_path or not os.path.isdir(folder_path):
        print("[ERROR] Invalid folder path.")
        return 0, 0
    if not email_set:
        print("[ERROR] Email set is empty or None.")
        return 0, 0

    eml_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file and file.lower().endswith('.eml'):
                full_path = os.path.join(root, file)
                eml_files.append(full_path)

    total_files = len(eml_files)
    print(f"[INFO] Found {total_files} .eml files.")

    if total_files == 0:
        print("[INFO] No .eml files to process.")
        return 0, 0

    matched_files = 0

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        print(f"[INFO] Starting parallel processing with {max_workers} workers.")
        futures = [executor.submit(file_contains_any_email, (file, email_set)) for file in eml_files]

        for idx, future in enumerate(as_completed(futures), 1):
            try:
                if future.result():
                    matched_files += 1
                if idx % 1000 == 0:
                    print(f"[TRACE] Processed {idx} files...")
            except Exception as e:
                print(f"[WARNING] Error processing file {idx}: {e}")

    print(f"[INFO] Finished scanning.")
    return matched_files, total_files

if __name__ == "__main__":
    filtered_email_file = "/na2/hrtest/filtered_emails.txt"
    eml_folder = "/n2/Dopy/14-NV-2024/Em1113_10241114003004"

    filtered_emails = load_filtered_emails(filtered_email_file)
    if filtered_emails:
        matched, total = scan_eml_files_parallel(eml_folder, filtered_emails, max_workers=8)
        print(f"\n[RESULT] Matched .eml files: {matched} / {total}")
    else:
        print("[ERROR] No valid emails loaded. Aborting.")
