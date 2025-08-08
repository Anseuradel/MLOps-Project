# Start Minikube with clean slate
minikube delete
minikube start --driver=docker --cpus=4 --memory=8g

# Configure Docker environment
minikube docker-env | Invoke-Expression

# Build image with clean cache
docker build --no-cache -t ml-service:latest .

# Create monitoring namespace if not exists
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Apply configurations in correct order
kubectl apply -f k8s/persistence.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/prometheus.yaml
kubectl apply -f k8s/grafana.yaml
kubectl apply -f k8s/hpa.yaml

# Wait for services
Write-Host "Waiting for services to become ready..."
kubectl wait --for=condition=available deployment/ml-service --timeout=120s
kubectl wait --for=condition=available deployment/prometheus -n monitoring --timeout=120s
kubectl wait --for=condition=available deployment/grafana -n monitoring --timeout=120s

# Port forwarding
Start-Process powershell -ArgumentList "kubectl port-forward svc/ml-service 8000:8000"
Start-Process powershell -ArgumentList "kubectl port-forward svc/prometheus 9090:9090 -n monitoring"
Start-Process powershell -ArgumentList "kubectl port-forward svc/grafana 3000:3000 -n monitoring"

# Open Grafana
Start-Process "http://localhost:3000"

Write-Host "`nAccess URLs:"
Write-Host "ML Service: http://localhost:8000"
Write-Host "Prometheus: http://localhost:9090"
Write-Host "Grafana: http://localhost:3000 (admin/admin)"
