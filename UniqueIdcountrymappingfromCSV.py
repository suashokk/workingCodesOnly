import pandas as pd

def get_email_country_mapping(csv_path):
    """
    Reads the CSV file and creates a dictionary with email addresses as keys and countries as values.
    """
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Create a dictionary mapping Email Address to Country
    email_country_mapping = dict(zip(df['Email Address'], df['Country']))

    return email_country_mapping

# Path to the generated CSV file
csv_path = "/mnt/data/unique_email_list.csv"

# Get the email-country mapping
email_country_mapping = get_email_country_mapping(csv_path)

# Print the mapping
for email, country in email_country_mapping.items():
    print(f"{email} -> {country}")
