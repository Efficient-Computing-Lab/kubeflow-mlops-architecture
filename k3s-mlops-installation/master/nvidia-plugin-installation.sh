export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 \
    && chmod 700 get_helm.sh \
    && ./get_helm.sh
kubectl create ns gpu-operator
kubectl label --overwrite ns gpu-operator pod-security.kubernetes.io/enforce=privileged
helm repo add nvidia https://helm.ngc.nvidia.com/nvidia \
    && helm repo update
helm install gpu-operator -n gpu-operator --create-namespace   nvidia/gpu-operator $HELM_OPTIONS     --set toolkit.env[0].name=CONTAINERD_CONFIG     --set toolkit.env[0].value=/etc/containerd/config.toml     --set toolkit.env[1].name=CONTAINERD_SOCKET     --set toolkit.env[1].value=/run/containerd/containerd.sock     --set toolkit.env[2].name=CONTAINERD_RUNTIME_CLASS     --set toolkit.env[2].value=nvidia     --set toolkit.env[3].name=CONTAINERD_SET_AS_DEFAULT     --set-string toolkit.env[3].value=true --set driver.enabled=false --set toolkit.enabled=false
kubectl apply -f nvidia-runtime-class.yaml