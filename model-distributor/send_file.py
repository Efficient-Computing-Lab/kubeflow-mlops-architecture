import requests
import logging
logging.basicConfig(level=logging.INFO)

def readfile(file):
    url = "http://192.168.1.240:5002/upload"
    with open(file, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    if response.status_code == 200:
        logging.info("File "+file+ "sent to Model Splitter")