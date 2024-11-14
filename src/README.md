# Example for Topographers

## Overview
This folders holds a Dockerfile and a create-image.sh script that creates that Docker image of EPOS that
should be used in the training phase of Kubeflow. It also contains a couple of files that configure EPOS training.

## Build and Push Docker Image
```sh
./create-image.sh
```
## Training performed on Docker container
To perform the training via docker container use the Docker image named gkorod/topo:v1.0. When the
container reaches the running state it will automatically start the training of EPOS
```sh
docker run -dt --gpus all --device /dev/nvidia0:/dev/nvidia0   --device /dev/nvidiactl:/dev/nvidiactl   --device /dev/nvidia-uvm:/dev/nvidia-uvm   --device /dev/nvidia-uvm-tools:/dev/nvidia-uvm-tools   gkorod/topo:v1.0
```

### Training performed on Kubernetes
To perform the training on Kubernetes use the Docker image named gkorod/topo:v1.0. When the
container reaches the running state it will automatically start the training of EPOS
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
To perform training on Kubeflow, you have to use the pipeline_dsl/topo_example.py by using the following command
```sh
python3 topo_example.py
```
The above command will deploy a pod in the kubeflow namespace. Kyverno is configured to apply a policy
on the kubeflow namespace ensuring that every pod will use the runtimeClassName: nvidia.

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
