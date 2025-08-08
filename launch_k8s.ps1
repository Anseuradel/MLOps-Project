# launch_k8s.ps1 - Updated version with deployment

function Start-InNewWindow {
    param (
        [string]$Command,
        [string]$Title
    )
    $psCommand = "powershell -NoExit -Command `"$Command`""
    Start-Process wt -ArgumentList @("-w", "0", "nt", "-d", (Get-Location).Path, "--title", $Title, $psCommand)
}

# 0. Clean up existing Minikube instance
Write-Host "Cleaning up existing Minikube cluster..."
minikube stop 2>&1 | Out-Null
minikube delete 2>&1 | Out-Null

# 1. Start Minikube cluster
Write-Host "Starting Minikube cluster..."
minikube start
if (-not $?) {
    Write-Host "Failed to start Minikube"
    exit 1
}

# 2. Build and load Docker image
Write-Host "Building and loading Docker image..."
docker build -t ml-service .
minikube image load ml-service:latest

# 3. Apply Kubernetes manifests
Write-Host "Deploying Kubernetes resources..."
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Wait for deployment to be ready
Write-Host "Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/ml-service -n default

# 4. Now proceed with service discovery and port forwarding
Write-Host "Getting ML Service URL..."
$mlServiceUrl = minikube service ml-service --url -n default
Write-Host "ML Service available at: $mlServiceUrl"

# Prometheus
Start-InNewWindow -Command "kubectl port-forward svc/prometheus 9090 -n default" -Title "Prometheus (9090)"
Start-Sleep -Seconds 2

# Grafana
Start-InNewWindow -Command "kubectl port-forward -n monitoring deployment/grafana 3000" -Title "Grafana (3000)"
Start-Sleep -Seconds 2
Start-Process "http://localhost:3000/login"

# ML Service port forwarding
Start-InNewWindow -Command "kubectl port-forward svc/ml-service 8000:8000 -n default" -Title "ML Service (8000)"
Start-Sleep -Seconds 2

# FastAPI server
Start-InNewWindow -Command "uvicorn src.api.main:app --reload --port 8001" -Title "FastAPI (8001)"

Write-Host "All services launched successfully"
Write-Host "Monitoring:"
Write-Host "- Prometheus: http://localhost:9090"
Write-Host "- Grafana: http://localhost:3000 (admin/admin)"
Write-Host "- ML Service: http://localhost:8000"
Write-Host "- FastAPI: http://localhost:8001"
