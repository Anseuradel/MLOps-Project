# launch_k8s.ps1
Write-Host "Starting Minikube cluster..." -ForegroundColor Cyan
minikube start --driver=docker --cpus=4 --memory=6g --disk-size=20g

# Set Docker environment
Write-Host "Configuring Docker environment..." -ForegroundColor Cyan
minikube docker-env | Invoke-Expression

# Build Docker image
Write-Host "Building ML service image..." -ForegroundColor Cyan
docker build -t ml-service:latest .

# Deploy Kubernetes manifests
Write-Host "Applying Kubernetes configurations..." -ForegroundColor Cyan
kubectl apply -f k8s/

# Wait for deployments
Write-Host "Waiting for services to become ready..." -ForegroundColor Cyan
kubectl wait --for=condition=available --timeout=300s deployment/ml-service -n default
kubectl wait --for=condition=available --timeout=300s deployment/prometheus -n monitoring
kubectl wait --for=condition=available --timeout=300s deployment/grafana -n monitoring

# Start port forwarding
Write-Host "Starting port forwarding..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward svc/ml-service 8000:8000 -n default"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward svc/prometheus 9090:9090 -n monitoring"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward svc/grafana 3000:3000 -n monitoring"

# Get service URLs
Write-Host "`nService Endpoints:" -ForegroundColor Green
Write-Host "ML Service: http://localhost:8000" -ForegroundColor Yellow
Write-Host "Prometheus: http://localhost:9090" -ForegroundColor Yellow
Write-Host "Grafana:    http://localhost:3000 (admin/admin)" -ForegroundColor Yellow
Write-Host "Minikube Dashboard: $(minikube service ml-service --url -n default)" -ForegroundColor Yellow

# Open Grafana in browser
Start-Process "http://localhost:3000"

Write-Host "`nSetup complete. Keep these terminal windows open." -ForegroundColor Green
