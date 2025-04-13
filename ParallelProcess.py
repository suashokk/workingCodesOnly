import os
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed

def process_file(file_path, onPremEmails, SAASEmails):
    try:
        file_size = os.path.getsize(file_path)
        email_ids = extract_unique_email_ids_from_eml(file_path)
        
        isOnPremFile = False
        isSAASFile = False

        for email_id in email_ids:
            if email_id:
                email_id = email_id.strip().lower()
                if email_id in onPremEmails:
                    isOnPremFile = True
                if email_id in SAASEmails:
                    isSAASFile = True

        # Classify and return counters
        if isOnPremFile and isSAASFile:
            return ('combo', file_size)
        elif isOnPremFile:
            return ('onprem', file_size)
        elif isSAASFile:
            return ('saas', file_size)
        else:
            return ('none', 0)
    
    except Exception as e:
        print(f"[ERROR] Processing {file_path}: {e}", flush=True)
        return ('error', 0)

def extract_unique_emails_from_folder(folder_path, onPremEmails, SAASEmails):
    onPremFileCounter = 0
    comboFileCounter = 0
    saasFileCounter = 0
    onPremFileSizeCounter = 0
    comboFileSizeCounter = 0
    saasFileSizeCounter = 0

    file_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".eml")]

    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(process_file, file_path, onPremEmails, SAASEmails)
            for file_path in file_list
        ]
        for future in as_completed(futures):
            result_type, file_size = future.result()
            if result_type == 'combo':
                comboFileCounter += 1
                comboFileSizeCounter += file_size
            elif result_type == 'onprem':
                onPremFileCounter += 1
                onPremFileSizeCounter += file_size
            elif result_type == 'saas':
                saasFileCounter += 1
                saasFileSizeCounter += file_size

    print(f"Combo Files: {comboFileCounter}, Size: {comboFileSizeCounter}")
    print(f"OnPrem Files: {onPremFileCounter}, Size: {onPremFileSizeCounter}")
    print(f"SaaS Files: {saasFileCounter}, Size: {saasFileSizeCounter}")
