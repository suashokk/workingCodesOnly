import csv
from email.message import EmailMessage

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

def write_eml_file(email_list, output_file):
    msg = EmailMessage()
    msg['Subject'] = "Filtered Email List"
    msg['From'] = "noreply@example.com"
    msg['To'] = "admin@example.com"
    body = "Filtered Email IDs:\n\n" + "\n".join(email_list)
    msg.set_content(body)

    with open(output_file, 'wb') as f:
        f.write(bytes(msg))

if __name__ == "__main__":
    csv_file = "output_mapping.csv"
    country = "India"  # Change this as needed
    output_file = "filtered_emails.eml"

    filtered_emails = extract_emails_by_country(csv_file, country)
    write_eml_file(filtered_emails, output_file)

    print(f"Written {len(filtered_emails)} email ID(s) to {output_file}")
