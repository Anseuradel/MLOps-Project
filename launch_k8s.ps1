# launch_k8s.ps1

# Function to start a process in a new terminal window
function Start-InNewTerminal {
    param (
        [string]$Command,
        [string]$Title
    )
    Start-Process wt -ArgumentList "-w", "0", "nt", "-d", (Get-Location).Path, "--title", $Title, "powershell", "-NoExit", "-Command", $Command
}

Write-Host "Starting Minikube..."
minikube start

Write-Host "Starting ML Service URL..."
$mlServiceUrl = minikube service ml-service --url
Write-Host "ML Service URL: $mlServiceUrl"

# Launch Prometheus in a new terminal
Start-InNewTerminal -Command "kubectl port-forward svc/prometheus 9090 -n default" -Title "Prometheus"

# Launch Grafana in a new terminal
Start-InNewTerminal -Command "kubectl port-forward -n monitoring deployment/grafana 3000" -Title "Grafana"
Start-Process "http://localhost:3000/login"

# Launch ML Service port forward in a new terminal
Start-InNewTerminal -Command "kubectl port-forward svc/ml-service 8000:8000 -n default" -Title "ML Service"

# Launch FastAPI server in a new terminal
Start-InNewTerminal -Command "uvicorn src.api.main:app --reload --port 8001" -Title "FastAPI Server"

Write-Host "All services launched in separate terminal windows."
