import json

import requests
from kfp import dsl, compiler
from kfp.dsl import component, pipeline, pipeline_task
from kfp import kubernetes
import tarfile
import os
import kfp


# Define the prepare_data component
@component(
    base_image="gkorod/topo:1.0",
)
def train():
    import subprocess
    import shutil
    import os
    command = "source /root/.bashrc && conda activate epos && exec bash"
    subprocess.run("conda list", shell=True)
    # Run the command in a new shell
    subprocess.run(command, shell=True, executable='/bin/bash')
    subprocess.run([
        'python', 'epos/scripts/create_example_list.py',
        '--dataset=carObj12',
        '--split=train',
        '--split_type=primesense'
    ])

    # Step 3: Run the Python script to create the TFRecord
    subprocess.run([
        'python', 'epos/scripts/create_tfrecord.py',
        '--dataset=carObj12',
        '--split=train',
        '--split_type=primesense',
        '--examples_filename=carObj12_train-primesense_examples.txt',
        '--add_gt=True',
        '--shuffle=True',
        '--rgb_format=png'
    ], shell=True)

    # Step 4: Create the output directory
    os.makedirs('/app/store/tf_models/obj12', exist_ok=True)

    # Step 5: Run the Python script to train the model
    subprocess.run(['python', 'epos/scripts/train.py', '--model=obj12'],shell=True)
    contents = os.listdir("/app/store/tf_models/obj12")

    # Source file path
    src = '/app/store/tf_models'

    # Destination file path
    dst = '/trained_models'

    # Copy the file
    shutil.copytree(src, dst,dirs_exist_ok=True)
# Define the pipeline
@pipeline
def my_pipeline():
    """My ML pipeline."""
    training_task = train()
    training_task.set_accelerator_type('nvidia.com/gpu')
    kubernetes.add_pod_annotation(training_task, 'runtimeClassName', 'nvidia')
    kubernetes.mount_pvc(training_task, pvc_name="trained-models", mount_path="/trained_models")


# Compile the pipeline
compiler.Compiler().compile(my_pipeline, package_path="pipeline.yaml")

# Package the pipeline YAML
with tarfile.open("pipeline.tar.gz", "w:gz") as tar:
    tar.add("pipeline.yaml", arcname=os.path.basename("pipeline.yaml"))

# Upload and run the pipeline
json_info = {
    "user_namespace": "test",
    "experiment": "experiment_test",
    "pipeline_name": "test",
    "job_name": "training_job",
    "pipeline_version": "93"
}
# Create a multipart-encoded file
files = {
    'file': ('file.tar', open('pipeline.tar.gz', 'rb'), 'application/x-tar')
}

# Send the POST request to submit pipeline and initialize training phase
response = requests.post('http://192.168.1.240:5005/submit', files=files, data={'json_data': json.dumps(json_info)})
