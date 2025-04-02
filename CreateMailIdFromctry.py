import csv

def extract_emails_by_country(csv_file, target_country):
    emails = []
    with open(csv_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            country = row['country'].strip().lower()
            email = row['email'].strip()
            if country == target_country.lower():
                emails.append(email)
    return emails

if __name__ == "__main__":
    csv_file = "output_mapping.csv"
    country = "India"  # <-- change this to your desired country

    result_emails = extract_emails_by_country(csv_file, country)

    print(f"\nEmail IDs for country: {country}")
    for email in result_emails:
        print("-", email)

    print(f"\nTotal: {len(result_emails)} email(s)")
