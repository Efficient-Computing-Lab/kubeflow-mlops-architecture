import json

import requests

from kfp.dsl import component, pipeline, container_component, ContainerSpec, PipelineTask

from kfp import compiler
from kfp import kubernetes
import tarfile
import os

import argparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Provide Initializer IP and Port.")
parser.add_argument("--initializer-ip", required=True, help="IP address of the Initializer")
parser.add_argument("--initializer-port", required=True, help="Port of the Initializer")
args = parser.parse_args()

INITIALIZER_IP = args.initializer_ip
INITIALIZER_PORT = args.initializer_port

# Optional: sanity check
if not INITIALIZER_IP or not INITIALIZER_PORT:
    raise ValueError("Initializer IP and Port must be provided as arguments.")

# Construct the URL using environment variables
initializer_url = f'http://{INITIALIZER_IP}:{INITIALIZER_PORT}/submit'

@component(
    base_image="gkorod/topo:v1.1", packages_to_install=["pyyaml"]
)
def setup_train():
    import subprocess
    import yaml
    import requests
    import os

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
    #subprocess.run("ls /datasets/epos", shell=True)
    os.makedirs("/app/datasets/carObj12/train_primesense",exist_ok=True)
    subprocess.run("ls /app/datasets/carObj12",shell=True)
    subprocess.run("cp -r /datasets/epos/100_IndustryShapes/* /app/datasets/carObj12/train_primesense",shell=True)
    subprocess.run("ls /app/datasets/carObj12/train_primesense/",shell=True)
    #subprocess.run("ls /app/datasets/carObj12/train_primesense",shell=True)
    #subprocess.run("mv /app/datasets/carObj12/ /app/datasets/carObj12/train_primesense",shell=True)
    os.makedirs("/app/store/tf_data", exist_ok=True)
    # Run the command in a new shell
    subprocess.run("conda run -n epos python epos/scripts/create_example_list.py --dataset=carObj12 --split=train --split_type=primesense", shell=True)
    subprocess.run(
        "conda run -n epos python epos/scripts/create_tfrecord.py --dataset=carObj12 --split=train --split_type=primesense --examples_filename=carObj12_train-primesense_examples.txt --add_gt=True --shuffle=True --rgb_format=png",
        shell=True)
    subprocess.run(
        "conda run -n epos python epos/scripts/train.py --model=obj12",
        shell=True)
    model_version = "v1.0"
    target_path = f"/trained_models/epos/{model_version}"
    os.makedirs(target_path, exist_ok=True)
    subprocess.run("cp -r /app/store/tf_models /trained_models/epos/"+model_version,shell=True)
# Define the pipeline
@pipeline(name="epos-training")
def epos_pipeline():
    """My ML pipeline."""
    training_task = setup_train()
    training_task.set_accelerator_type('nvidia.com/gpu')
    training_task.set_accelerator_limit(1)
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
    "pipeline_version": "154"
}
# Create a multipart-encoded file
files = {
    'file': ('file.tar.gz', open('pipeline.tar.gz', 'rb'), 'application/x-tar')
}

# Send the POST request to submit pipeline and initialize training phase
response = requests.post(initializer_url, files=files, data={'json_data': json.dumps(json_info)})

print(f"Response from Initializer: {response.status_code}")
