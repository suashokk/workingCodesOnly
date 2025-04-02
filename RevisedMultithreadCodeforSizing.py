import os
import mmap
from concurrent.futures import ProcessPoolExecutor

def read_user_ids(file_path):
    """Reads user IDs from a file and returns a set of them."""
    with open(file_path, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def file_contains_user_id_wrapper(args):
    """Wrapper to allow multiprocessing (can't use lambdas or closures)."""
    file_path, user_ids = args
    try:
        with open(file_path, 'rb') as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                for user_id in user_ids:
                    if mm.find(user_id.encode()) != -1:
                        return os.path.getsize(file_path)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    return 0

def generate_file_paths(folder_path):
    """Yields full file paths in folder."""
    for root, _, files in os.walk(folder_path):
        for file in files:
            yield os.path.join(root, file)

def calculate_matching_files_size(folder_path, user_ids):
    """Main function to calculate matching file size using multiprocessing."""
    file_paths = list(generate_file_paths(folder_path))
    args_list = [(path, user_ids) for path in file_paths]

    with ProcessPoolExecutor() as executor:
        sizes = executor.map(file_contains_user_id_wrapper, args_list)

    return sum(sizes)

if __name__ == "__main__":
    user_ids_file = "/home/ngcmodel/aruveh/SAASandNONSASFileSizing/output/filtered_emails.txt"
    folder_path = "/nasbox/datacollection/adhirveds/email1/download/20250226"

    user_ids = read_user_ids(user_ids_file)
    total_size = calculate_matching_files_size(folder_path, user_ids)
    print(f"Total size of files containing user IDs: {total_size} bytes")
