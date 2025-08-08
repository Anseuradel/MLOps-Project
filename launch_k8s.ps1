<#
.SYNOPSIS
Launch script for Kubernetes ML service deployment
#>

# 1. Clean previous cluster
Write-Host "Cleaning previous Minikube cluster..."
minikube delete

# 2. Start with adjusted resources
Write-Host "Starting Minikube cluster..."
minikube start --driver=docker --cpus=4 --memory=6000m --disk-size=20g

# 3. Configure Docker environment
Write-Host "Configuring Docker environment..."
minikube docker-env | Invoke-Expression

# 4. Build image
Write-Host "Building Docker image..."
docker build -t ml-service:latest .

# 5. Wait for Kubernetes API
Write-Host "Waiting for Kubernetes API to be ready..."
$maxRetries = 30
$retryCount = 0
$connected = $false

while ($retryCount -lt $maxRetries -and -not $connected) {
    try {
        $null = kubectl cluster-info
        if ($LASTEXITCODE -eq 0) {
            $connected = $true
            Write-Host "✓ Kubernetes API is ready"
        }
    }
    catch {
        Write-Host "Waiting for Kubernetes API... (attempt $($retryCount + 1))"
        Start-Sleep -Seconds 5
        $retryCount++
    }
}

if (-not $connected) {
    Write-Host "❌ Failed to connect to Kubernetes API after $maxRetries attempts" -ForegroundColor Red
    exit 1
}

# 6. Create monitoring namespace
Write-Host "Creating monitoring namespace..."
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# 7. Apply configurations
Write-Host "Applying Kubernetes configurations..."
$manifests = @(
    "persistence.yaml",
    "configmap.yaml",
    "deployment.yaml",
    "service.yaml",
    "prometheus.yaml",
    "grafana.yaml",
    "hpa.yaml"
)

foreach ($manifest in $manifests) {
    $path = Join-Path -Path "k8s" -ChildPath $manifest
    if (Test-Path $path) {
        Write-Host "Applying $manifest..."
        kubectl apply --validate=false -f $path
    }
    else {
        Write-Host "Warning: $path not found" -ForegroundColor Yellow
    }
}

# 8. Wait for services
Write-Host "`nWaiting for services to become ready..."
$services = @(
    @{Name="ml-service"; Namespace="default"},
    @{Name="prometheus"; Namespace="monitoring"},
    @{Name="grafana"; Namespace="monitoring"}
)

foreach ($service in $services) {
    Write-Host "Waiting for $($service.Name) in namespace $($service.Namespace)..."
    kubectl wait --for=condition=available deployment/$($service.Name) --namespace $($service.Namespace) --timeout=300s
}

# 9. Port forwarding
Write-Host "`nSetting up port forwarding..."
$portForwards = @(
    @{Service="ml-service"; Port=8000; Namespace="default"},
    @{Service="prometheus"; Port=9090; Namespace="monitoring"},
    @{Service="grafana"; Port=3000; Namespace="monitoring"}
)

foreach ($forward in $portForwards) {
    $command = "kubectl port-forward svc/$($forward.Service) $($forward.Port):$($forward.Port) --namespace $($forward.Namespace)"
    Write-Host "Starting: $command"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $command
}

# 10. Open Grafana
Start-Sleep -Seconds 5
Write-Host "`nOpening Grafana dashboard..."
Start-Process "http://localhost:3000"

# Display access information
Write-Host @"

╔══════════════════════════════════════════╗
║          Deployment Successful!          ║
╠══════════════════════════════════════════╣
║ ML Service:  http://localhost:8000      ║
║ Prometheus:  http://localhost:9090      ║
║ Grafana:     http://localhost:3000      ║
║ Credentials: admin/admin                ║
╚══════════════════════════════════════════╝
"@ -ForegroundColor Green
