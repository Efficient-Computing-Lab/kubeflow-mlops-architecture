import os
import logging
from flask import Flask, request, jsonify
import kfp_client
import shutil
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
@app.route('/submit', methods=['POST'])
def sumbit ():
    # Upload and run the pipeline
    data = request.form.get("json_data")
    tar_file = request.files['file']
    if data and 'files' in request.files:
        user_namespace = data.get("user_namespace") #test
        experiment= data.get("experiment") #experiment_test
        pipeline_name = data.get("pipeline_name") #test
        job_name = data.get("job_name") #training_job
        pipeline_version = data.get("pipeline_version") #v62

        tar_file = request.files['file']
        tar_path = os.path.join('/tmp', tar_file.filename)
        tar_file.save(tar_path)
        kfp_client.run_instance(user_namespace, experiment, pipeline_name, job_name, pipeline_version)
        shutil.rmtree('/tmp')

if __name__ == '__main__':
    app.run(debug=True, port=5005, host="0.0.0.0")