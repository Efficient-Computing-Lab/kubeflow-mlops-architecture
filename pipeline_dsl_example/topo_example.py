import json

import requests
from kfp import dsl, compiler
from kfp.dsl import component, pipeline, pipeline_task
from kfp import kubernetes
import tarfile
import os
import kfp

@component(
    base_image="gkorod/topo:1.0",
)
def configure_parameters():
    import subprocess
    import shutil
    import os
    import yaml
    command="rm -r /datasets/params.yml"
    subprocess.run(command, shell=True)
    new_params_yaml ={
      "dataset": "carObj12",
      "model_variant": "xception_65",
      "atrous_rates": [12, 24, 36],
      "encoder_output_stride": 8,
      "decoder_output_stride": [4],
      "upsample_logits": False,
      "frag_seg_agnostic": False,
      "frag_loc_agnostic": False,
      "num_frags": 64,
      "corr_min_obj_conf": 0.1,
      "corr_min_frag_rel_conf": 0.5,
      "corr_project_to_model": False,
      "train_tfrecord_names": ["carObj12_train-primesense"],
      "train_max_height_before_crop": 480,
      "train_crop_size": "640, 480",
      "freeze_regex_list": ["xception_65/entry_flow"],
      "initialize_last_layer": True,
      "fine_tune_batch_norm": False,
      "train_steps": 15480,
      "train_batch_size": 1,
      "base_learning_rate": 0.0000001,
      "learning_power": 0.9,
      "obj_cls_loss_weight": 1.0,
      "frag_cls_loss_weight": 1.0,
      "frag_loc_loss_weight": 100.0,
      "train_knn_frags": 1,
      "data_augmentations": {
        "random_adjust_brightness": {
          "min_delta": -0.2,
          "max_delta": 0.4
        },
        "random_adjust_contrast": {
          "min_delta": 0.6,
          "max_delta": 1.4
        },
        "random_adjust_saturation": {
          "min_delta": 0.6,
          "max_delta": 1.4
        },
        "random_adjust_hue": {
          "max_delta": 1.0
        },
        "random_blur": {
          "max_sigma": 1.5
        },
        "random_gaussian_noise": {
          "max_sigma": 0.1
        }
      },
      "eval_tfrecord_names": ["tless_test_targets-bop19"],
      "eval_max_height_before_crop": 480,
      "eval_crop_size": "640, 480",
      "infer_tfrecord_names": ["carObj12_test"],
      "infer_max_height_before_crop": 480,
      "infer_crop_size": "640, 480"
    }
    # Save the dictionary to a YAML file
    with open('/app/store/tf_models/obj12/params.yml', 'w') as file:
        yaml.dump(new_params_yaml, file, default_flow_style=False)
    # Define source and destination paths
    training_set_source = "/datasets/epos/training_set"
    training_set_destination = "/app/datasets/carObj12/train_primesense"

    # Create the destination directory if it doesn't exist
    os.makedirs(os.path.dirname(training_set_destination), exist_ok=True)

    # Move the directory
    shutil.copytree(training_set_source, training_set_destination)


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
def epos_pipeline():
    """My ML pipeline."""
    setup_epos = configure_parameters()
    kubernetes.mount_pvc(setup_epos, pvc_name="datasets", mount_path="/datasets")
    training_task = train()
    training_task.set_accelerator_type('nvidia.com/gpu')
    kubernetes.add_pod_annotation(training_task, 'runtimeClassName', 'nvidia')
    kubernetes.mount_pvc(training_task, pvc_name="trained-models", mount_path="/trained_models")
    kubernetes.mount_pvc(training_task, pvc_name="datasets", mount_path="/datasets")


# Compile the pipeline
compiler.Compiler().compile(epos_pipeline, package_path="pipeline.yaml")

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
# The following IP is belonging to Erebor
response = requests.post('http://147.102.109.92:5005/submit', files=files, data={'json_data': json.dumps(json_info)})
