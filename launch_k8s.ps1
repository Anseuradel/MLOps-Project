# launch_k8s.ps1 - Minimal Deployment Script
# Assumes: 
# 1. Minikube cluster is already running
# 2. Docker images are already built/loaded

# function Start-InNewWindow {
#     param (
#         [string]$Command,
#         [string]$Title
#     )
#     Start-Process wt -ArgumentList @(
#         "-w", "0", "nt", 
#         "-d", (Get-Location).Path,
#         "--title", $Title,
#         "powershell", "-NoExit", "-Command", $Command
#     )
# }

function Start-InNewWindow {
    param (
        [string]$Command,
        [string]$Title
    )
    $psPath = "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
    if (-not (Test-Path $psPath)) {
        Write-Host "PowerShell not found at $psPath" -ForegroundColor Red
        $psPath = "powershell.exe"
    }

    Write-Host "Launching new window with command:" $Command

    Start-Process wt -ArgumentList @(
        "-w", "0", "nt",
        "-d", (Get-Location).Path,
        "--title", $Title,
        $psPath,
        "-NoExit",
        "-Command", $Command
    ) -ErrorAction Stop
}


# 1. Apply Kubernetes manifests
Write-Host "Deploying Kubernetes resources..."
kubectl apply -f k8s/persistence.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/prometheus.yaml
kubectl apply -f k8s/grafana.yaml

# 2. Wait for deployment
Write-Host "Waiting for services to become ready..."
kubectl wait --for=condition=available --timeout=300s deployment/ml-service -n default
Start-InNewWindow -Command "minikube service ml-service --url" -Title "ml_service" 
Start-InNewWindow -Command "uvicorn src.api.main:app --reload --port 8001" -Title "fastapi" 

# 3. Set up port forwarding
# Start-InNewWindow -Command "kubectl port-forward svc/prometheus 9090 -n monitoring" -Title "Prometheus"

$kubectlPath = "C:\Users\adela\adela\bin\kubectl.exe"

# Prometheus section - only run if service exists
$prometheusSvc = & $kubectlPath get svc prometheus -n monitoring --ignore-not-found
if ($prometheusSvc) {
    Start-InNewWindow -Command "& `"$kubectlPath`" port-forward svc/prometheus -n monitoring 9090:9090" -Title "Prometheus"
    Start-Sleep -Seconds 2
} else {
    Write-Host "Prometheus service not found - skipping port-forward" -ForegroundColor Yellow
}
Start-InNewWindow -Command "& `"$kubectlPath`" port-forward svc/grafana 3000 -n monitoring" -Title "Grafana" 
Start-InNewWindow -Command "& 'C:\Users\adela\adela\bin\kubectl.exe' port-forward svc/ml-service 8000:8000 -n default" -Title "ML Service"

# 4. Get service URLs
Write-Host "`nApplication Endpoints:"
Write-Host "- ML Service:    http://localhost:8000"
Write-Host "- Prometheus:    http://localhost:9090"
Write-Host "- Grafana:       http://localhost:3000 (admin/admin)`n"

# 5. Open browser tabs
Start-Process "http://localhost:3000"
Start-Process "http://localhost:9090"
