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


## Cite Us

If you use the above code for your research, please cite our paper:

- [Streamlining ML Training in Kubernetes: An MLOps Architecture with Kubeflow](https://dl.acm.org/doi/10.1145/3770501.3771304)
```
@inproceedings{10.1145/3770501.3771304,
author = {Korontanis, Ioannis and Zacharia, Athina and Makris, Antonios and Pateraki, Maria and Tserpes, Konstantinos},
title = {Streamlining ML Training in Kubernetes: An MLOps Architecture with Kubeflow},
year = {2025},
isbn = {9798400715952},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3770501.3771304},
doi = {10.1145/3770501.3771304},
abstract = {Machine Learning Operations (MLOps) is essential for automating the deployment, monitoring, and management of ML models. By integrating MLOps with DevOps practices, developers can create automated training pipelines. This paper explores using Kubeflow as an MLOps platform and GitHub Actions as a CI/CD pipeline for training and deploying ML models. Kubeflow provides a scalable framework for orchestrating ML workflows in containers, with Kubernetes enabling efficient resource management. Containerization ensures consistency, portability, and reproducibility across environments, while GitHub Actions automates testing, version control, and deployment. A real-world case study demonstrates this architecture and discusses challenges and best practices for modern MLOps workflows.},
booktitle = {Proceedings of the 15th International Conference on the Internet of Things},
pages = {267–270},
numpages = {4},
keywords = {Edge Computing, MLOps, DevOps},
location = {
},
series = {IOT '25}
}
```