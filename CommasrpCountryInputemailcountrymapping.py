import csv

def get_emails_by_countries(csv_file, country_list):
    selected_emails = []
    with open(csv_file, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)

        try:
            email_index = headers.index("EMAIL_ADDRESS")
            country_index = headers.index("COUNTRY")
        except ValueError:
            raise Exception("Required columns 'EMAIL_ADDRESS' or 'COUNTRY' not found in CSV")

        for row in reader:
            if len(row) > max(email_index, country_index):
                country = row[country_index].strip()
                if country in country_list:
                    email = row[email_index].strip()
                    selected_emails.append(email)

    return selected_emails

# Example usage
countries = ["India", "USA"]  # Replace with your comma-separated list
csv_path = "your_csv_file.csv"
emails = get_emails_by_countries(csv_path, countries)
print(emails)
