#!/bin/sh
cd worker
master_ip=$(cat "master_ip_address.txt")
token=$(cat "token")
echo $master_ip
echo $token
export K3S_KUBECONFIG_MODE="644"
export K3S_URL="https://$master_ip:6443"
export K3S_TOKEN="$token"
curl -sfL https://get.k3s.io | sh -s
