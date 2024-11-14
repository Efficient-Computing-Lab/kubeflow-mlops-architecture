# k3s-mlops-installation

The current repository utilizes Ansible to automate the setup of a K3s cluster and the MLOps tool MLFlow on Raspberrypies.

## Requirements

Before executing any playbook from this repository, ensure the following:
* Your local machine should have installed Ansible 4.10
* Each Raspberry Pi should have nvidia-smi pre-installed
* Each Raspberry Pi possesses a unique hostname. (Both hostnamectl and /etc/hosts/)
* Each Raspberry Pi contains the specified entries, cgroup_enable=memory cgroup_memory=1 cgroup_enable=cpuset, in /boot/cmdline.txt.
* Each Raspberry Pi should have ssh enabled and contain the public key of your local machine

If not, please utilize hostnamectl to configure the hostname and edit `/etc/hosts`, as well as modify `/boot/cmdline.txt` to include the specified entries mentioned above.

## Installation order

1. [Install K3s master](./ansible_scripts/README.md#Install-K3s-master)
2. [Install K3s workers](./ansible_scripts/README.md#Install-K3s-workers)
3. [Install K3s Nvidia Plugin](./ansible_scripts/README.md#Install-K3s-Nvidia-Plugin)
4. [Install Kubeflow](./ansible_scripts/README.md#Install-Kubeflow)
