export PIPELINE_VERSION=2.2.0
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic?ref=$PIPELINE_VERSION"
kubectl wait pods -l "application-crd-id=kubeflow-pipelines" -n kubeflow --for "condition=Ready" --timeout "1800s"
kubectl expose deployment ml-pipeline-ui --type=LoadBalancer --name=ml-pipeline-ui-lb --port=3001 --target-port=3000 -n kubeflow
kubectl apply -f pvc.yaml
kubectl apply -f model-distributor-deployment.yaml
kubectl expose -n kubeflow  deployment model-distributor --port=4443 --target-port=4443 --name=model-distributor-lb --type=LoadBalancer
kubectl appply -f dataset-registry.yaml
kubectl expose -n kubeflow  deployment dataset-registry --port=4422 --target-port=4422 --name=model-distributor-lb --type=LoadBalancer