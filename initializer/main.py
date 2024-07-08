import os
import logging
from flask import Flask, request, jsonify
import kfp_client
import shutil
import json
import tempfile
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)


@app.route('/submit', methods=['POST'])
def sumbit():
    # Upload and run the pipeline
    data = request.form.get("json_data")
    data = json.loads(data)
    tar_file = request.files['file']
    if data and tar_file:
        user_namespace = data.get("user_namespace")  #test
        experiment = data.get("experiment")  #experiment_test
        pipeline_name = data.get("pipeline_name")  #test
        job_name = data.get("job_name")  #training_job
        pipeline_version = data.get("pipeline_version")  #v62

        # Use a temporary directory to save the tar file
        with tempfile.TemporaryDirectory() as tmpdirname:
            tar_path = os.path.join(tmpdirname, tar_file.filename)
            tar_file.save(tar_path)
            kfp_client.run_instance(user_namespace, experiment, pipeline_name, job_name, pipeline_version, tar_path)

    return "training phase initialized"


if __name__ == '__main__':
    app.run(debug=True, port=5005, host="0.0.0.0")
