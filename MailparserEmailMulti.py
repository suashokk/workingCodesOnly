import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from mailparser import parse_from_file
from datetime import datetime

def load_filtered_emails(file_path):
    print(f"[INFO] Loading filtered emails from: {file_path}")
    if not file_path or not os.path.isfile(file_path):
        print(f"[ERROR] Invalid file path: {file_path}")
        return set()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            emails = {line.strip().lower() for line in f if line.strip()}
            print(f"[INFO] Loaded {len(emails)} emails.")
            return emails
    except Exception as e:
        print(f"[ERROR] Failed to read email list: {e}")
        return set()

def file_contains_email_fast(file_path, email_set):
    if not file_path or not os.path.isfile(file_path) or not email_set:
        return None

    try:
        mail = parse_from_file(file_path)
        subject = mail.subject or ""
        body = mail.body or ""
        text = (subject + " " + body).lower()

        if any(email in text for email in email_set):
            return file_path
    except Exception:
        return None
    return None

def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def scan_eml_files(folder_path, email_set, max_workers=8, chunk_size=5000):
    if not folder_path or not os.path.isdir(folder_path):
        print("[ERROR] Invalid folder path.")
        return [], 0

    print(f"[INFO] Walking through: {folder_path}")
    eml_files = [
        os.path.join(root, file)
        for root, _, files in os.walk(folder_path)
        for file in files if file.lower().endswith('.eml')
    ]

    total_files = len(eml_files)
    print(f"[INFO] Total .eml files: {total_files}")

    matched_files = []

    for i, batch in enumerate(chunk_list(eml_files, chunk_size)):
        print(f"[BATCH] Processing batch {i + 1} with {len(batch)} files...")
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(file_contains_email_fast, file, email_set) for file in batch]
            for idx, future in enumerate(as_completed(futures), 1):
                result = future.result()
                if result:
                    matched_files.append(result)
                if idx % 1000 == 0:
                    print(f"[TRACE] Checked {idx} files in batch {i + 1}...")

    return matched_files, total_files

def save_results(file_list, output_path):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for path in file_list:
                f.write(path + '\n')
        print(f"[INFO] Saved matched files to: {output_path}")
    except Exception as e:
        print(f"[ERROR] Could not save results: {e}")

if __name__ == "__main__":
    start_time = datetime.now()

    filtered_email_file = "/nas02/hrtest/filtered_emails.txt"
    eml_folder = "/nas02/Datacopy/14-NOV-2024/Email-20241113_12-00-20241114003004"
    output_file = "matched_eml_files.txt"

    email_set = load_filtered_emails(filtered_email_file)

    if email_set:
        matched, total = scan_eml_files(
            eml_folder, email_set,
            max_workers=8,
            chunk_size=5000
        )
        print(f"\n[RESULT] Matched: {len(matched)} / {total} files.")
        save_results(matched, output_file)
    else:
        print("[ERROR] No emails to search for.")

    print(f"[DONE] Time taken: {datetime.now() - start_time}")
