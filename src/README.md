# Use Case training

## Overview
This folder contains a Dockerfile and a create-image.sh script used to build 
the Docker image for EPOS, which is required during the training phase in Kubeflow.
Additionally, it includes several configuration files essential for setting up the
EPOS training process. The README.md provides an overview of different approaches to
training EPOS using containerization — starting from manual methods, progressing to
Kubeflow integration, and ultimately demonstrating how to combine GitHub Actions with
Kubeflow for a fully automated training pipeline

## Build and Push Docker Image
```sh
./create-image.sh
```
## Training performed on Docker container
To perform the training via docker container use the Docker image named gkorod/topo:v1.0. When the
container reaches the running state it will automatically start the training of EPOS, since this image version runs the start_training.sh script.
```sh
docker run -dt --gpus all --device /dev/nvidia0:/dev/nvidia0   --device /dev/nvidiactl:/dev/nvidiactl   --device /dev/nvidia-uvm:/dev/nvidia-uvm   --device /dev/nvidia-uvm-tools:/dev/nvidia-uvm-tools   gkorod/topo:v1.0
```

### Training performed on Kubernetes
To perform the training on Kubernetes use the Docker image named gkorod/topo:v1.0. When the
container reaches the running state it will automatically start the training of EPOS, since this image version runs the start_training.sh script.
```sh
kubectl apply -f pod-deployment.yaml
```
The pod-deployment.yaml has the following structure:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: topo-pod
  namespace: kubeflow
  labels:
    app: topo
spec:
  restartPolicy: OnFailure  # Options: Always, OnFailure, Never
  containers:
  - name: topo
    image: gkorod/topo:v1.1
    imagePullPolicy: Always
    resources:
      limits:
        nvidia.com/gpu: 1  # Limiting to 1 GPU
    volumeMounts:
    - mountPath: "/trained_models"
      name: data-volume
    - mountPath: "/datasets"
      name: data-volume2
  volumes:
  - name: data-volume2
    persistentVolumeClaim:
      claimName: datasets
  - name: data-volume
    persistentVolumeClaim:
      claimName: trained-models
  runtimeClassName: nvidia  # Specify the runtime class for NVIDIA GPUs
```
If there is no kubeflow namespace in your Kubernetes cluster create one or just delete the
key value pair from the above yaml file before applying it.


### Training performed on Kubeflow
To execute the training process on Kubeflow without utilizing GitHub Actions,
the pipeline_dsl/topo_example.py script must be run locally using the following command.
```sh
python3 topo_example.py
```
Make sure that topo_example.py uses the gkorod/topov1.1 Docker image. This Docker image it does not
start the training automatically it expects commands from Kubeflow pipelines. The above command will deploy a pod in the kubeflow namespace. 
Kyverno is configured to apply a policy on the kubeflow namespace ensuring that every pod will use the runtimeClassName: nvidia.

Each time you run the above script you have to change the pipeline version in the following part:
``` python
json_info = {
    "user_namespace": "test",
    "experiment": "experiment_test",
    "pipeline_name": "test",
    "job_name": "training_job",
    "pipeline_version": "127"
}
```
### Training performed on Kubeflow with Github Actions
The current repository uses Github Actions to trigger the training workflow of Kubeflow. Each time developers pushes
code to the main branch the workflow that is located at .github/workflows folder is being activated.

``` yaml
name: Run EPOS Kubeflow Pipeline

on:
  push:
    branches:
      - main

jobs:
  run-pipeline:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          pip install kfp requests pyyaml kfp-kubernetes

      - name: Run pipeline script
        run: python pipeline_dsl_example/topo_example.py \
              --initializer-ip ${{ secrets.INITIALIZER_IP }} \
              --initializer-port ${{ secrets.INITIALIZER_PORT }}
```

Before pushing code to the main branch, developers must update the pipeline version within 
the pipeline_dsl/topo_example.py script, as described in the previous section.
The GitHub Actions workflow ensures that all necessary dependencies required by the pipeline_dsl/topo_example.py script
are properly installed prior to its execution.
