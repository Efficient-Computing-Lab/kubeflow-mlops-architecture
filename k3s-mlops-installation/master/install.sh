#!/bin/sh
export K3S_KUBECONFIG_MODE="644"
curl -sfL https://get.k3s.io | sh -s
sudo mkdir master/join-token
sudo touch master/join-token/token
sudo cp /var/lib/rancher/k3s/server/node-token master/join-token/token
sudo chmod a+rw master/join-token/token
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
export KUBECONFIG=~/.kube/config
mkdir ~/.kube 2> /dev/null
sudo k3s kubectl config view --raw > "$KUBECONFIG"
chmod 600 "$KUBECONFIG"