<#
.SYNOPSIS
Launch Kubernetes environment with proper port forwarding
#>

# 1. Stop any existing port forwards
Write-Host "Stopping existing port forwards..."
Get-Process -Name "kubectl" | Where-Object { $_.CommandLine -like "*port-forward*" } | Stop-Process -Force -ErrorAction SilentlyContinue

# 2. Start Minikube cluster
Write-Host "Starting Minikube cluster..."
minikube delete
minikube start --driver=docker --cpus=4 --memory=6000m --addons=metrics-server

# 3. Configure Docker environment
Write-Host "Configuring Docker..."
minikube docker-env | Invoke-Expression

# 4. Build Docker image
Write-Host "Building Docker image..."
docker build -t ml-service:latest .

# 5. Apply configurations
Write-Host "Applying Kubernetes manifests..."
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/persistence.yaml
kubectl apply -f k8s/deployment.yaml

# 6. Wait for pods to be ready
Write-Host "Waiting for pods to be ready..."
function Wait-ForPod {
    param($name, $namespace="default")
    
    $attempt = 0
    $maxAttempts = 30
    
    do {
        $podStatus = kubectl get pods -n $namespace -l app=$name -o jsonpath='{.items[0].status.phase}'
        $isReady = kubectl get pods -n $namespace -l app=$name -o jsonpath='{.items[0].status.containerStatuses[0].ready}'
        
        if ($podStatus -eq "Running" -and $isReady -eq "true") {
            Write-Host "$name is ready"
            return $true
        }
        
        Write-Host "Waiting for $name to be ready... (Status: $podStatus, Ready: $isReady)"
        $attempt++
        Start-Sleep -Seconds 5
    } while ($attempt -lt $maxAttempts)
    
    Write-Host "Timed out waiting for $name to be ready" -ForegroundColor Red
    return $false
}

Wait-ForPod -name "ml-service"
Wait-ForPod -name "prometheus" -namespace "monitoring"
Wait-ForPod -name "grafana" -namespace "monitoring"

# 7. Apply services after pods are ready
Write-Host "Applying services..."
kubectl apply -f k8s/service.yaml

# 8. Get pod names for port forwarding
$ml_pod = kubectl get pods -l app=ml-service -o name
$prom_pod = kubectl get pods -n monitoring -l app=prometheus -o name
$grafana_pod = kubectl get pods -n monitoring -l app=grafana -o name

# 9. Start port forwarding
Write-Host "Starting port forwarding..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward $ml_pod 8000:8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward $prom_pod 9090:9090 -n monitoring"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward $grafana_pod 3000:3000 -n monitoring"

# 10. Apply HPA last
Write-Host "Applying HPA..."
kubectl apply -f k8s/hpa.yaml

# 11. Display access information
Start-Sleep -Seconds 3  # Wait for port forwards to establish
Write-Host @"

╔══════════════════════════════════════════╗
║          Kubernetes Environment          ║
╠══════════════════════════════════════════╣
║ ML Service:  http://localhost:8000      ║
║ Prometheus:  http://localhost:9090      ║
║ Grafana:     http://localhost:3000      ║
║                                          ║
║ NodePort Access:                         ║
║ ML Service:  $(minikube service ml-service --url) ║
║ Grafana:     $(minikube service grafana -n monitoring --url) ║
╚══════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# 12. Open Grafana in browser
Start-Process "http://localhost:3000"
