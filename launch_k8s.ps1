# launch_k8s.ps1 - Improved version with proper sequencing and error handling

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

# 2. Verify ml-service exists before proceeding
Write-Host "Checking for ml-service in default namespace..."
$serviceCheck = kubectl get svc ml-service -n default --output=name 2>&1
if ($serviceCheck -like "*NotFound*") {
    Write-Host "Error: ml-service not found in default namespace"
    Write-Host "Available services:"
    minikube service list
    exit 1
}

# 3. Get ML Service URL (must complete before other steps)
Write-Host "Getting ML Service URL..."
$mlServiceUrl = minikube service ml-service --url -n default
if (-not $?) {
    Write-Host "Failed to get ML Service URL"
    exit 1
}
Write-Host "ML Service available at: $mlServiceUrl"

# 4. Launch other services only after ML Service is confirmed available
Write-Host "Launching supporting services..."

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
