import os
import re
import datetime
from email import policy
from email.parser import BytesParser

# ----- Configuration (update these paths) -----
ONPREM_COUNTRY_FILE = "onprem_countries.txt"   # Comma-separated country codes
HR_FEED_FILE = "hr_feed.csv"                   # Format: email_address,country
EML_FOLDER = "eml_files"                       # Folder containing .eml files

# ----- Initialize sets and counters -----
onPremCountryMailSet = set()
SAASCountryMailSet = set()

onPremFileCounter = 0
comboFileCounter = 0
saasFileCounter = 0

onPremFileSizeCounter = 0
comboFileSizeCounter = 0
saasFileSizeCounter = 0

# ----- Read OnPrem Countries from file -----
try:
    with open(ONPREM_COUNTRY_FILE, "r", encoding="utf-8") as f:
        onprem_countries = {code.strip().upper() for code in f.read().split(",") if code.strip()}
except Exception as e:
    print(f"[{datetime.datetime.now()}] Error reading ONPREM_COUNTRY_FILE: {e}", flush=True)
    onprem_countries = set()

# ----- Read HR feed and classify emails -----
try:
    with open(HR_FEED_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                email, country = line.strip().split(",")
                email = email.strip().lower()
                country = country.strip().upper()
                if country in onprem_countries:
                    onPremCountryMailSet.add(email)
                else:
                    SAASCountryMailSet.add(email)
            except Exception as line_error:
                print(f"[{datetime.datetime.now()}] Skipping invalid HR line: {line.strip()} ({line_error})", flush=True)
except Exception as e:
    print(f"[{datetime.datetime.now()}] Error reading HR_FEED_FILE: {e}", flush=True)

# ----- Regex for extracting emails -----
email_regex = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")

# ----- Process each .eml file -----
for filename in os.listdir(EML_FOLDER):
    if filename.lower().endswith(".eml"):
        file_path = os.path.join(EML_FOLDER, filename)
        try:
            file_size = os.path.getsize(file_path)

            with open(file_path, "rb") as f:
                msg = BytesParser(policy=policy.default).parse(f)

            # Combine all headers
            header_fields = ["from", "to", "cc", "bcc"]
            headers_combined = " ".join(str(msg.get(header, "")) for header in header_fields)

            # Extract all unique emails from headers
            found_emails = set(email_regex.findall(headers_combined.lower()))

            # Check for matching
            isOnPremFile = any(email in onPremCountryMailSet for email in found_emails)
            isSAASFile = any(email in SAASCountryMailSet for email in found_emails)

            if isOnPremFile and isSAASFile:
                comboFileCounter += 1
                comboFileSizeCounter += file_size
            elif isOnPremFile:
                onPremFileCounter += 1
                onPremFileSizeCounter += file_size
            elif isSAASFile:
                saasFileCounter += 1
                saasFileSizeCounter += file_size

        except Exception as e:
            print(f"[{datetime.datetime.now()}] Error processing file {filename}: {e}", flush=True)

# ----- Final Summary Report -----
print("\n--- Final Report ---", flush=True)
print(f"Matched OnPrem Only   : {onPremFileCounter} files, {onPremFileSizeCounter} bytes", flush=True)
print(f"Matched SAAS Only     : {saasFileCounter} files, {saasFileSizeCounter} bytes", flush=True)
print(f"Matched Combo (Both)  : {comboFileCounter} files, {comboFileSizeCounter} bytes", flush=True)
