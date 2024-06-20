from flask import Flask, send_file, abort, request
from werkzeug.utils import safe_join
import os
import threading
import main

app = Flask(__name__)

directory = os.environ.get('ENV_PATH', 'data')
thread1 = threading.Thread(target=main.find_new_files, args=(directory,))
thread1.start()


# Option 1: Using send_file
@app.route('/download/<filename>')
def download_file(filename):
    # Define the path to the directory where the files are stored

    # Create the full file path
    file_path = safe_join(directory, filename)

    try:
        # Send the file to the client
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError:
        # Return a 404 error if the file is not found
        abort(404)


@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the POST request contains a file
    if 'file' not in request.files:
        return 'No file part in the request', 400

    file = request.files['file']

    # Check if the file is empty
    if file.filename == '':
        return 'No selected file', 400

    # Save the file to a local directory with its original filename
    path = directory + "/submodels/"
    # Check if the directory exists
    if not os.path.exists(path):
        # Create the directory if it does not exist
        os.makedirs(path)
        print(f"Directory '{path}' created successfully.")
    else:
        print(f"Directory '{path}' already exists.")
    file.save(os.path.join(path, file.filename))

    return 'File uploaded successfully', 200


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=4443)
