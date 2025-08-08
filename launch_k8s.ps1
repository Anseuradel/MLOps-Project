# launch_k8s.ps1

# Function to start a command in a new PowerShell terminal window
function Start-InNewWindow {
    param (
        [string]$Command,
        [string]$Title
    )
    $psCommand = "powershell -NoExit -Command `"$Command`""
    Start-Process wt -ArgumentList @("-w", "0", "nt", "-d", (Get-Location).Path, "--title", $Title, $psCommand)
}

Write-Host "Starting Minikube cluster..."
minikube start

Write-Host "Getting ML Service URL..."
$mlServiceUrl = minikube service ml-service --url
Write-Host "ML Service available at: $mlServiceUrl"

# Launch Prometheus in a new window
Start-InNewWindow -Command "kubectl port-forward svc/prometheus 9090 -n default" -Title "Prometheus (9090)"
Start-Sleep -Seconds 2  # Small delay between launches

# Launch Grafana in a new window
Start-InNewWindow -Command "kubectl port-forward -n monitoring deployment/grafana 3000" -Title "Grafana (3000)"
Start-Sleep -Seconds 2
Start-Process "http://localhost:3000/login"

# Launch ML Service port forwarding in a new window
Start-InNewWindow -Command "kubectl port-forward svc/ml-service 8000:8000 -n default" -Title "ML Service (8000)"
Start-Sleep -Seconds 2

# Launch FastAPI server in a new window
Start-InNewWindow -Command "uvicorn src.api.main:app --reload --port 8001" -Title "FastAPI Server (8001)"

Write-Host "All services launched in separate terminal windows:"
Write-Host "- Prometheus: http://localhost:9090"
Write-Host "- Grafana: http://localhost:3000 (admin/admin)"
Write-Host "- ML Service: http://localhost:8000"
Write-Host "- FastAPI Server: http://localhost:8001"
