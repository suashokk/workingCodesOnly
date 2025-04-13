from concurrent.futures import ProcessPoolExecutor, as_completed
import os

def extract_unique_emails_from_folder(folder_path, onPremEmails, SAASEmails):
    onPremFileCounter = 0
    comboFileCounter = 0
    saasFileCounter = 0
    onPremFileSizeCounter = 0
    comboFileSizeCounter = 0
    saasFileSizeCounter = 0

    futures = []
    with ProcessPoolExecutor() as executor:
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                futures.append(executor.submit(process_file, file_path, onPremEmails, SAASEmails))

        for future in as_completed(futures):
            try:
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
                # You can log others like 'none' or 'error' if needed
            except Exception as e:
                print(f"[ERROR] A worker failed: {e}", flush=True)

    print("[INFO] Returning final counters", flush=True)
    return comboFileCounter, onPremFileCounter, saasFileCounter, comboFileSizeCounter, onPremFileSizeCounter, saasFileSizeCounter
