# 1. Clean previous cluster
minikube delete

# 2. Start with adjusted resources
minikube start --driver=docker --cpus=4 --memory=6000m --disk-size=20g

# 3. Configure Docker environment
minikube docker-env | Invoke-Expression

# 4. Build image
docker build -t ml-service:latest .

# 5. Wait for Kubernetes API
$maxRetries = 30
$retryCount = 0
$connected = $false

while ($retryCount -lt $maxRetries -and -not $connected) {
    try {
        kubectl cluster-info
        if ($LASTEXITCODE -eq 0) {
            $connected = $true
            Write-Host "✓ Kubernetes API is ready"
        }
    } catch {
        Write-Host "Waiting for Kubernetes API to be ready... (attempt $($retryCount + 1))"
        Start-Sleep -Seconds 5
        $retryCount++
    }
}

if (-not $connected) {
    Write-Host "❌ Failed to connect to Kubernetes API after $maxRetries attempts"
    exit 1
}

# 6. Create monitoring namespace
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# 7. Apply configurations with validation disabled
kubectl apply --validate=false -f k8s/persistence.yaml
kubectl apply --validate=false -f k8s/configmap.yaml
kubectl apply --validate=false -f k8s/deployment.yaml
kubectl apply --validate=false -f k8s/service.yaml
kubectl apply --validate=false -f k8s/prometheus.yaml
kubectl apply --validate=false -f k8s/grafana.yaml
kubectl apply --validate=false -f k8s/hpa.yaml

# 8. Wait for services
Write-Host "Waiting for services to become ready..."
kubectl wait --for=condition=available deployment/ml-service --timeout=300s
kubectl wait --for=condition=available deployment/prometheus -n monitoring --timeout=300s
kubectl wait --for=condition=available deployment/grafana -n monitoring --timeout=300s

# 9. Port forwarding
Start-Process powershell -ArgumentList "kubectl port-forward svc/ml-service 8000:8000"
Start-Process powershell -ArgumentList "kubectl port-forward svc/prometheus 9090:9090 -n monitoring"
Start-Process powershell -ArgumentList "kubectl port-forward svc/grafana 3000:3000 -n monitoring"

# 10. Open Grafana
Start-Process "http://localhost:3000"

Write-Host "`nAccess URLs:"
Write-Host "ML Service: http://localhost:8000"
Write-Host "Prometheus: http://localhost:9090"
Write-Host "Grafana: http://localhost:3000 (admin/admin)"
