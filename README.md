# Streamlining ML Training in Kubernetes: An MLOps Architecture with Kubeflow
This repository introduces an architecture that uses Kubeflow in order to perform
MLOps pipelines capable to automate training and storage of models.

![MLOps Architecture](Kubeflow%20Training.png)

## Documentation
1. [Installation guide](./k3s-mlops-installation/README.md)
    A step-by-step guide for deploying the presented Kubeflow MLOps architecture, including prerequisites, configuration, 
    and setup instructions. This guide is using Ansible for the installation process and the setups the 
    fully functional MLOps environment.
2. [Use Case Training](./src/README.md)
This documentation outlines the process of training [EPOS model](https://github.com/thodan/epos), 
beginning with basic manual approaches that leverage Docker and Kubernetes, 
and progressing to more advanced, automated methods using Kubeflow, 
including its integration with GitHub Actions for a fully streamlined workflow.
