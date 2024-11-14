# Ansible instructions

Ansible should be installed in your local machine. All the ssh public keys should be also stored in your local machine. If this steps are already then installations can be performed successfully.

## Install K3s master

The first step to install a K3s cluster is to install its master. In order to do so you should run the following playbook:

```bash
ansible-playbook -i hosts install_k3s_master.yaml -vvv
```

This playbook executes the `master/install.sh` script on the Raspberry Pi defined as `raspberrypies-master` in the hosts file. The output of this script is the join token, which will be copied to your local machine within the `worker` folder.

## Install K3s workers

The second step is to setup K3s workers. To start the installation process use the following playbook:

```bash
ansible-playbook -i hosts install_k3s_workers.yaml -vvv
```
This playbook executes the  `worker/install.sh` script on Raspberry Pies defined as `raspberrypies-workers` in the hosts file. The installation script uses the join-token retrieved from `master/install.sh` and the master's IP that is retrieved from the hosts file by your local machine.
## Install K3s Nvidia Plugin
Afterwards, the Kubernetes Nvidia Plugin has to be installed. To start the installation process use the following playbook:
```bash
ansible-playbook -i hosts install_k3s_nvidia_plugin.yaml -vvv
```
This playbook executes the `master/nvidia-plugin-installation.sh` script on the Raspberry Pi defined as `raspberrypies-master` in the hosts file.
## Install Kubeflow

Then, Kubeflow should be installed in the K3s master. The purpose of Kubeflow is to perform MLOps. In order to do so you should run the following playbook:

```bash
ansible-playbook -i hosts install_kubeflow_master.yaml -vvv
```
This playbook executes the `master/kubeflow-install.sh` script on the Raspberry Pi defined as `raspberrypies-master` in the hosts file.

# Install Kyverno

The last step is to install Kyverno in the K3s master. Kyverno is an easy policy manager for Kubernetes, we used it to
make nvidia GPUs accessible to pods that are under kubeflow namespace. In order to do so you should run the following playbook:

```bash
ansible-playbook -i hosts install_kyverno.yaml -vvv
```
This playbook executes the `master/kyverno-install.sh` script on the Raspberry Pi defined as `raspberrypies-master` in the hosts file.


