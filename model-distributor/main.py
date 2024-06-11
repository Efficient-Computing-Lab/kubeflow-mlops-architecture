import os
import time
import logging

logging.basicConfig(level=logging.INFO)

def find_new_files(directory):
    """Find new and rewritten files in the given directory."""
    current_files = set(os.listdir(directory))
    
    while True:
        time.sleep(5)  # Check every 5 seconds
        latest_files = set(os.listdir(directory))
        
        # Find the new files
        new_files = latest_files - current_files
        if new_files:
            logging.info("New files found:")
            for file in new_files:
                logging.info(os.path.join(directory, file))
        
        # Update current files and checksums
        current_files = latest_files

# Get environment variables
directory_path = os.environ.get('ENV_PATH', '/data')

# Start finding new files
find_new_files(directory_path)
