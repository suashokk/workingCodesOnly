import os import re import csv import email import datetime from collections import defaultdict from email import policy from email.parser import BytesParser from concurrent.futures import ProcessPoolExecutor, as_completed

----- CONFIGURATION -----

ONPREM_COUNTRY_FILE = "onprem_countries.txt"   # Comma-separated country codes HR_FEED_FILE = "hr_feed.csv"                   # With EMAIL_ADDRESS and COUNTRY columns EML_FOLDER = "eml_files"                        # Folder containing .eml files

----- Load OnPrem Countries from file -----

onprem_countries = set() try: with open(ONPREM_COUNTRY_FILE, "r", encoding="utf-8", errors="ignore") as f: content = f.read() onprem_countries = {c.strip().upper() for c in content.split(',') if c.strip()} except Exception as e: print(f"[ERROR] Failed to read OnPrem country file: {e}", flush=True)

----- Load HR feed and classify email IDs -----

onPremCountryMailSet = set() SAASCountryMailSet = set() try: with open(HR_FEED_FILE, "r", encoding="utf-16", errors="ignore") as f: reader = csv.reader(f) header = next(reader) email_idx = header.index("EMAIL_ADDRESS") country_idx = header.index("COUNTRY")

for row in reader:
        try:
            email = row[email_idx].strip().lower()
            country = row[country_idx].strip().upper()
            if country in onprem_countries:
                onPremCountryMailSet.add(email)
            else:
                SAASCountryMailSet.add(email)
        except Exception as err:
            print(f"[WARN] Skipped line: {row} ({err})", flush=True)

except Exception as e: print(f"[ERROR] Failed to parse HR feed file: {e}", flush=True)

----- Regex to extract email addresses -----

email_regex = re.compile(r"[\w.-]+@[\w.-]+.\w+")

----- Stats holders -----

file_stats = defaultdict(int)

----- File Classification Function -----

def classify_eml_file(file_path): result = {"type": None, "size": 0} try: size = os.path.getsize(file_path) with open(file_path, "rb") as f: msg = BytesParser(policy=policy.default).parse(f) headers = " ".join(str(msg.get(h, "")) for h in ["from", "to", "cc", "bcc"]) emails = set(email_regex.findall(headers.lower()))

is_onprem = any(e in onPremCountryMailSet for e in emails)
    is_saas = any(e in SAASCountryMailSet for e in emails)

    result["size"] = size
    if is_onprem and is_saas:
        result["type"] = "combo"
    elif is_onprem:
        result["type"] = "onprem"
    elif is_saas:
        result["type"] = "saas"
except Exception as e:
    print(f"[{datetime.datetime.now()}] Error reading {file_path}: {e}", flush=True)
return result

----- Process All EML Files -----

if not os.path.isdir(EML_FOLDER): print(f"[ERROR] Folder not found: {EML_FOLDER}", flush=True) else: eml_files = [os.path.join(EML_FOLDER, f) for f in os.listdir(EML_FOLDER) if f.lower().endswith(".eml")] with ProcessPoolExecutor() as executor: future_map = {executor.submit(classify_eml_file, f): f for f in eml_files} for future in as_completed(future_map): res = future.result() if res["type"]: file_stats[f"{res['type']}FileCounter"] += 1 file_stats[f"{res['type']}FileSizeCounter"] += res["size"]

# ----- Final Report -----
print("\n--- Final Report ---", flush=True)
for category in ["onprem", "saas", "combo"]:
    print(f"{category.title()} Files: {file_stats[category+'FileCounter']} | Total Size: {file_stats[category+'FileSizeCounter']} bytes", flush=True)

