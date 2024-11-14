sudo helm repo add community-charts https://community-charts.github.io/helm-charts
sudo KUBECONFIG=/home/rpi/.kube/config helm install my-mlflow community-charts/mlflow --namespace mlflow
export POD_NAME=$(kubectl get pods --namespace mlflow -l "app.kubernetes.io/name=mlflow,app.kubernetes.io/instance=my-mlflow" -o jsonpath="{.items[0].metadata.name}")
export CONTAINER_PORT=$(kubectl get pod --namespace mlflow $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
kubectl expose -n mlflow deployment my-mlflow --type=LoadBalancer --name=my-loadbalancer-service --port=$CONTAINER_PORT --target-port=$CONTAINER_PORT
sudo helm repo add istio https://istio-release.storage.googleapis.com/charts
kubectl create namespace istio-system
sudo KUBECONFIG=/home/rpi/.kube/config helm install istio-base istio/base -n istio-system
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.5/cert-manager.yaml
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.14.0/serving-crds.yaml
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.14.0/serving-core.yaml
kubectl apply -f https://github.com/knative/eventing/releases/download/knative-v1.14.1/eventing-crds.yaml
kubectl apply -f https://github.com/knative/eventing/releases/download/knative-v1.14.1/eventing-core.yaml
kubectl apply -f kserve.yaml

