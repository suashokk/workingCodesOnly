import csv

# Input file paths
email_txt_file = "emails.txt"
email_csv_file = "email_country.csv"
output_csv_file = "matched_email_country_mapping.csv"

# Step 1: Read email IDs from the .txt file
with open(email_txt_file, "r", encoding="ISO-8859-1") as f:
    email_ids = {line.strip() for line in f if "@" in line}

# Step 2: Read the CSV and find matches
matched_rows = []

with open(email_csv_file, "r", encoding="ISO-8859-1") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        email = row.get("EMAIL_ADDRESS", "").strip()
        country = row.get("COUNTRY", "").strip()
        if email in email_ids:
            matched_rows.append({"EMAIL_ADDRESS": email, "COUNTRY": country})

# Step 3: Write matched rows to a new CSV file
with open(output_csv_file, "w", newline='', encoding="utf-8") as out_file:
    writer = csv.DictWriter(out_file, fieldnames=["EMAIL_ADDRESS", "COUNTRY"])
    writer.writeheader()
    writer.writerows(matched_rows)

print(f"Matched email-country mapping saved to '{output_csv_file}'")
