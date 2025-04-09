import os
from email import policy
from email.parser import BytesParser
from concurrent.futures import ProcessPoolExecutor, as_completed

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

def file_contains_any_email(file_path, email_set):
    if not file_path or not os.path.isfile(file_path) or not email_set:
        return None

    try:
        with open(file_path, 'rb') as f:
            msg = BytesParser(policy=policy.default).parse(f)
            text = str(msg).lower()
            if any(email in text for email in email_set):
                return file_path  # Return file if match found
    except Exception:
        return None
    return None

def chunk_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def scan_eml_files_batched(folder_path, email_set, max_workers=8, chunk_size=5000):
    if not folder_path or not os.path.isdir(folder_path):
        print("[ERROR] Invalid folder path.")
        return [], 0

    print(f"[INFO] Walking through directory: {folder_path}")
    eml_files = [
        os.path.join(root, file)
        for root, _, files in os.walk(folder_path)
        for file in files if file.lower().endswith('.eml')
    ]

    total_files = len(eml_files)
    print(f"[INFO] Total .eml files found: {total_files}")

    if total_files == 0:
        return [], 0

    matched_files = []

    for i, batch in enumerate(chunk_list(eml_files, chunk_size)):
        print(f"[INFO] Processing batch {i + 1}: {len(batch)} files...")
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(file_contains_any_email, file, email_set) for file in batch]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    matched_files.append(result)

    return matched_files, total_files

if __name__ == "__main__":
    filtered_email_file = "/"
    eml_folder = ""

    filtered_emails = load_filtered_emails(filtered_email_file)

    if filtered_emails:
        matched_files, total = scan_eml_files_batched(
            eml_folder, filtered_emails,
            max_workers=8,
            chunk_size=5000  # reduce if memory usage is high
        )

        print(f"\n[RESULT] Matched files: {len(matched_files)} / {total}")
    else:
        print("[ERROR] No valid emails to scan.")
