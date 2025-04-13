import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from email import policy
from email.parser import BytesParser

def extract_unique_email_ids_from_eml(file_path):
    email_set = set()
    try:
        with open(file_path, 'rb') as fp:
            msg = BytesParser(policy=policy.default).parse(fp)
            addresses = []
            if msg['From']:
                addresses.append(msg['From'])
            if msg['To']:
                addresses += msg.get_all('To', [])
            if msg['Cc']:
                addresses += msg.get_all('Cc', [])
            for address in addresses:
                if isinstance(address, str):
                    email_set.add(address.strip().lower())
    except Exception as e:
        print(f"[ERROR] Could not parse {file_path}: {e}", flush=True)
    return email_set


def process_file(file_path, onPremEmails, SAASEmails):
    try:
        file_size = os.path.getsize(file_path)
        email_ids = extract_unique_email_ids_from_eml(file_path)

        isOnPremFile = False
        isSaaSFile = False

        for email_id in email_ids:
            if not email_id:
                continue
            email_id = email_id.strip().lower()
            if email_id in onPremEmails:
                isOnPremFile = True
            if email_id in SAASEmails:
                isSaaSFile = True

        # Return classification
        if isOnPremFile and isSaaSFile:
            return ('combo', file_size)
        elif isOnPremFile:
            return ('onprem', file_size)
        elif isSaaSFile:
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
            except Exception as e:
                print(f"[ERROR] A worker crashed or returned invalid data: {e}", flush=True)

    return comboFileCounter, onPremFileCounter, saasFileCounter, comboFileSizeCounter, onPremFileSizeCounter, saasFileSizeCounter


# Run the main
if __name__ == "__main__":
    folder_path = "input_folder_path_here"
    onPremEmails = {"email1@onprem.com", "email2@onprem.com"}
    SAASEmails = {"email1@saas.com", "email2@saas.com"}

    result = extract_unique_emails_from_folder(folder_path, onPremEmails, SAASEmails)

    if result is not None:
        comboFileCounter, onPremFileCounter, saasFileCounter, comboFileSizeCounter, onPremFileSizeCounter, saasFileSizeCounter = result
        print(f"Combo: {comboFileCounter}, Size: {comboFileSizeCounter}")
        print(f"OnPrem: {onPremFileCounter}, Size: {onPremFileSizeCounter}")
        print(f"SaaS: {saasFileCounter}, Size: {saasFileSizeCounter}")
    else:
        print("[ERROR] No result returned.")
