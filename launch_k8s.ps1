# 1. Start Minikube
Write-Host "Starting Minikube cluster..."
minikube delete
minikube start --driver=docker --cpus=4 --memory=6000m

# 2. Build Docker image
Write-Host "Building Docker image..."
minikube docker-env | Invoke-Expression
docker build -t ml-service:latest .

# 3. Create namespaces
Write-Host "Creating namespaces..."
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# 4. Apply configurations
Write-Host "Applying Kubernetes configurations..."
kubectl apply -f k8s/persistence.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/prometheus.yaml
kubectl apply -f k8s/grafana.yaml
kubectl apply -f k8s/hpa.yaml

# 5. Wait for pods to be RUNNING
Write-Host "Waiting for pods to be ready..."
$pods = @(
    "ml-service",
    "prometheus",
    "grafana"
)

foreach ($pod in $pods) {
    $namespace = if ($pod -eq "ml-service") { "default" } else { "monitoring" }
    
    Write-Host "Waiting for $pod pod..."
    do {
        $status = kubectl get pods -n $namespace -l app=$pod -o jsonpath='{.items[0].status.phase}'
        if ($status -eq "Pending") {
            Write-Host "$pod is still Pending, waiting..."
            Start-Sleep -Seconds 5
        }
        elseif ($status -eq "Running") {
            Write-Host "$pod is now Running"
            break
        }
        else {
            Write-Host "$pod status: $status"
            Start-Sleep -Seconds 5
        }
    } while ($true)
}

# 6. Start port forwarding
Write-Host "Starting port forwarding..."
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
