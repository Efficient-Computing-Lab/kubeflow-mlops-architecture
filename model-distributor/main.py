import os
import time
import logging

logging.basicConfig(level=logging.INFO)

def get_file_info(directory):
    """Retrieve file information including creation and modification times."""
    file_info = {}
    for file in os.listdir(directory):
        path = os.path.join(directory, file)
        if os.path.isfile(path):
            stats = os.stat(path)
            file_info[file] = {
                'created': stats.st_ctime,
                'modified': stats.st_mtime
            }
    return file_info

def find_new_files(directory):
    """Find new and rewritten files in the given directory."""
    current_files_info = get_file_info(directory)
    
    while True:
        time.sleep(5)  # Check every 5 seconds
        latest_files_info = get_file_info(directory)
        
        # Find new and updated files
        new_files = set(latest_files_info.keys()) - set(current_files_info.keys())
        updated_files = {
            file for file in latest_files_info
            if file in current_files_info and latest_files_info[file]['modified'] != current_files_info[file]['modified']
        }
        
        if new_files:
            logging.info("New files found:")
            for file in new_files:
                logging.info(f"File: {os.path.join(directory, file)}, Created: {time.ctime(latest_files_info[file]['created'])}")
        
        if updated_files:
            logging.info("Updated files found:")
            for file in updated_files:
                logging.info(f"File: {os.path.join(directory, file)}, Modified: {time.ctime(latest_files_info[file]['modified'])}")
        
        # Update current files info
        current_files_info = latest_files_info

# Get environment variables
directory_path = os.environ.get('ENV_PATH', '/data')

# Start finding new files
find_new_files(directory_path)
