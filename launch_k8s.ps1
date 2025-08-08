# 1. Start Minikube
minikube delete
minikube start --driver=docker --cpus=4 --memory=6000m

# 2. Build Docker image
minikube docker-env | Invoke-Expression
docker build -t ml-service:latest .

# 3. Create monitoring namespace first
kubectl create namespace monitoring

# 4. Apply configurations
kubectl apply -f k8s/persistence.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/prometheus.yaml
kubectl apply -f k8s/grafana.yaml
kubectl apply -f k8s/hpa.yaml

# 5. Wait for services to be ready
Write-Host "Waiting for services to start..."
Start-Sleep -Seconds 20

# 6. Persistent port forwarding (keeps windows open)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward svc/ml-service 8000:8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward svc/prometheus 9090:9090 -n monitoring"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward svc/grafana 3000:3000 -n monitoring"

# 7. Open Grafana after delay
Start-Sleep -Seconds 5
Start-Process "http://localhost:3000"

Write-Host "Access URLs:"
Write-Host "ML Service: http://localhost:8000"
Write-Host "Prometheus: http://localhost:9090"
Write-Host "Grafana: http://localhost:3000 (admin/admin)"
