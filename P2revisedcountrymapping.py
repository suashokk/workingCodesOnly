# -*- coding: utf-8 -*-
import csv
import codecs
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

# Input file paths
email_txt_file = '/nas04/hrtest/output/finaloutput.txt'
email_csv_file = '/nas04/hrtest/ALL_COMMSUV_20250403_D_1.csv'
output_csv_file = '/nas04/hrtest/output/output_mapping1.csv'

# Step 1: Read email IDs from the .txt file
email_ids = []
with codecs.open(email_txt_file, 'r', encoding='ISO-8859-1') as f:
    for line in f:
        line = line.strip()
        if "@" in line:
            email_ids.append(line.lower())  # optional: normalize casing

# Step 2: Read the CSV and find matches
matched_rows = []
with codecs.open(email_csv_file, 'r', encoding='ISO-8859-1') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        email = row.get("EMAIL_ADDRESS", "").strip()
        country = row.get("COUNTRY", "").strip()
        if email.lower() in email_ids:  # case-insensitive match
            matched_rows.append({
                "EMAIL_ADDRESS": email,
                "COUNTRY": country
            })

# Step 3: Write matched rows to a new CSV file
with codecs.open(output_csv_file, 'w', encoding='utf-8') as out_file:
    writer = csv.DictWriter(out_file, fieldnames=["EMAIL_ADDRESS", "COUNTRY"])
    writer.writeheader()
    for row in matched_rows:
        # Ensure all values are UTF-8 encoded strings
        writer.writerow({
            "EMAIL_ADDRESS": row["EMAIL_ADDRESS"],
            "COUNTRY": row["COUNTRY"]
        })

print("Matched email-country mapping saved to {}".format(output_csv_file))
