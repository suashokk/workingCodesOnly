import os
import mmap
from concurrent.futures import ProcessPoolExecutor

def read_user_ids(file_path):
    """Reads user IDs from a given file and returns a set of unique IDs."""
    with open(file_path, 'r') as file:
        return set(line.strip() for line in file if line.strip())

def file_contains_user_id(file_path, user_ids):
    """Checks whether a file contains any of the user IDs using mmap for efficiency."""
    try:
        with open(file_path, 'rb') as file:
            with mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as mmap_file:
                for user_id in user_ids:
                    if mmap_file.find(user_id.encode()) != -1:
                        return os.path.getsize(file_path)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return 0

def generate_file_paths(folder_path):
    """Generator to yield all file paths under folder_path recursively."""
    for root, _, files in os.walk(folder_path):
        for file in files:
            yield os.path.join(root, file)

def calculate_matching_files_size(folder_path, user_ids):
    """Calculates total size of files that contain at least one user ID."""
    with ProcessPoolExecutor() as executor:
        file_paths = generate_file_paths(folder_path)
        sizes = executor.map(lambda path: file_contains_user_id(path, user_ids), file_paths)
    return sum(sizes)

if __name__ == "__main__":
    # Replace with actual file path and folder path
    user_ids_file = "/home/ngcmodel/aruveh/SAASandNONSASFileSizing/output/filtered_emails.txt"
    folder_path = "/nasbox/datacollection/adhirveds/email1/download/20250226"

    user_ids = read_user_ids(user_ids_file)
    total_size = calculate_matching_files_size(folder_path, user_ids)
    print(f"Total size of files containing any user ID: {total_size} bytes")
