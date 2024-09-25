\#!/bin/bash

# Ask for version number
read -p "Enter version number (e.g., 1.0.): " VERSION

# Docker Hub username and image name
DOCKER_USERNAME="gkorod"
IMAGE_NAME="topo"

# Build the Docker image
echo "Building Docker image $DOCKER_USERNAME/$IMAGE_NAME:$VERSION..."
docker build -t $DOCKER_USERNAME/$IMAGE_NAME:$VERSION .

#Check if the build was successful
if [ $? -eq 0 ]; then
    echo "Docker image built successfully!"
else
    echo "Error: Docker image build failed."
    exit 1
fi

# Push the Docker image to Docker Hub
echo "Pushing Docker image to Docker Hub..."
docker push $DOCKER_USERNAME/$IMAGE_NAME:$VERSION

#Check if the push was successful
if [ $? -eq 0 ]; then
    echo "Docker image pushed successfully to Docker Hub as $DOCKER_USERNAME/$IMAGE_NAME:$VERSION"
else
    echo "Error: Docker image push failed."
    exit 1
#fi
