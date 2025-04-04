import re

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def read_emails(file_path, seen_emails, duplicates, malformed):
    valid_emails = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            email = line.split()[0]  # Remove any trailing comments
            if is_valid_email(email):
                if email in seen_emails:
                    duplicates.add(email)
                else:
                    seen_emails.add(email)
                    valid_emails.append(email)
            else:
                malformed.add(line)
    return valid_emails

def extract_unique_emails(file1_path, file2_path, output_path, duplicates_log, malformed_log):
    seen = set()
    duplicates = set()
    malformed = set()

    read_emails(file1_path, seen, duplicates, malformed)
    read_emails(file2_path, seen, duplicates, malformed)

    # Write unique emails
    with open(output_path, 'w') as out_file:
        out_file.write('\n'.join(sorted(seen)))

    # Write duplicates
    with open(duplicates_log, 'w') as dup_file:
        dup_file.write('\n'.join(sorted(duplicates)))

    # Write malformed lines
    with open(malformed_log, 'w') as mal_file:
        mal_file.write('\n'.join(sorted(malformed)))

def main():
    file1 = 'emails1.eml'
    file2 = 'emails2.eml'
    output = 'output.eml'
    duplicates = 'duplicates.log'
    malformed = 'malformed.log'

    extract_unique_emails(file1, file2, output, duplicates, malformed)
    print(f"Processing complete.\n- Unique emails: {output}\n- Duplicates: {duplicates}\n- Malformed: {malformed}")

if __name__ == "__main__":
    main()
