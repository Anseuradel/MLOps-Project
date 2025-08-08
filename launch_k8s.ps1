# Simple Kubernetes launch script
Write-Host "Starting Minikube cluster..."
minikube delete
minikube start --driver=docker --cpus=4 --memory=6000m

Write-Host "Building Docker image..."
minikube docker-env | Invoke-Expression
docker build -t ml-service:latest .

Write-Host "Applying Kubernetes configurations..."
kubectl apply -f k8s/persistence.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/prometheus.yaml
kubectl apply -f k8s/grafana.yaml
kubectl apply -f k8s/hpa.yaml

Write-Host "Starting port forwarding..."
Start-Process powershell -ArgumentList "kubectl port-forward svc/ml-service 8000:8000"
Start-Process powershell -ArgumentList "kubectl port-forward svc/prometheus 9090:9090 -n monitoring"
Start-Process powershell -ArgumentList "kubectl port-forward svc/grafana 3000:3000 -n monitoring"

Write-Host "Access URLs:"
Write-Host "ML Service: http://localhost:8000"
Write-Host "Prometheus: http://localhost:9090"
Write-Host "Grafana: http://localhost:3000 (admin/admin)"
