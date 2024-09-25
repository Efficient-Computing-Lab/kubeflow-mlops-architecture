# Example for Topographers

## Overview
This folders holds a Dockerfile and a create-image.sh script that creates that Docker image of EPOS that
should be used in the training phase of Kubeflow. It also contains a couple of files that configure EPOS training.

## Build and Push Docker Image
```sh
./create-image.sh
```
## Run Docker Container
```sh
docker run -dt --gpus all --device /dev/nvidia0:/dev/nvidia0   --device /dev/nvidiactl:/dev/nvidiactl   --device /dev/nvidia-uvm:/dev/nvidia-uvm   --device /dev/nvidia-uvm-tools:/dev/nvidia-uvm-tools   gkorod/topo:v1.0
```

### Train performed on Docker container
```sh
docker exec -it {container_id} bash
python epos/scripts/create_example_list.py --dataset=carObj12 --split=train --split_type=primesense
python epos/scripts/create_tfrecord.py --dataset=carObj12 --split=train --split_type=primesense --examples_filename=carObj12_train-primesense_examples.txt --add_gt=True --shuffle=True --rgb_format=png
python epos/scripts/train.py --model=obj12
```

