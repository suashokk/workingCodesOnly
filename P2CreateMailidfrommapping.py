import csv
import codecs

def extract_emails_by_countries(csv_file, countries_str):
    target_countries = [c.strip().lower() for c in countries_str.split(",")]
    emails = []
    with codecs.open(csv_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            country = row['COUNTRY'].strip().lower()
            email = row['EMAIL_ADDRESS'].strip()
            if country in target_countries:
                emails.append(email)
    return emails

def save_emails_to_txt(email_list, output_file):
    with codecs.open(output_file, mode='w', encoding='utf-8') as f:
        for email in email_list:
            f.write(email + '\n')

if __name__ == "__main__":
    csv_file = "/nas04/hrtest/output/output_mapping1.csv"
    countries = "IND,CHN,SAU,TUR,ZMB,POL,FRA,SWE,DEU"  # Change as needed
    output_file = "/nas04/hrtest/output/filtered_emails.txt"

    filtered_emails = extract_emails_by_countries(csv_file, countries)
    save_emails_to_txt(filtered_emails, output_file)

    print "Saved {} email(s) to: {}".format(len(filtered_emails), output_file)
