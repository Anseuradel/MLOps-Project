# 1. Start fresh cluster
minikube delete
minikube start --driver=docker --cpus=4 --memory=6000m --addons=metrics-server

# 2. Build and configure
minikube docker-env | Invoke-Expression
docker build -t ml-service:latest .

# 3. Create namespace first
kubectl create namespace monitoring

# 4. Apply configurations in order
kubectl apply -f k8s/configmaps.yaml
kubectl apply -f k8s/persistence.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/prometheus.yaml
kubectl apply -f k8s/grafana.yaml

# 5. Wait for pods to be READY (not just Running)
function Wait-ForPod {
    param($name, $namespace)
    do {
        $status = kubectl get pod -n $namespace -l app=$name -o jsonpath='{.items[0].status.containerStatuses[0].ready}'
        if ($status -eq "true") {
            Write-Host "$name is ready"
            break
        }
        Write-Host "Waiting for $name to be ready..."
        Start-Sleep -Seconds 5
    } while ($true)
}

Wait-ForPod -name "ml-service" -namespace "default"
Wait-ForPod -name "prometheus" -namespace "monitoring"
Wait-ForPod -name "grafana" -namespace "monitoring"

# 6. Apply HPA after metrics server is ready
kubectl apply -f k8s/hpa.yaml

# 7. Start port forwarding
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward svc/ml-service 8000:8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward svc/prometheus 9090:9090 -n monitoring"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "kubectl port-forward svc/grafana 3000:3000 -n monitoring"

# 8. Open dashboard
Start-Sleep -Seconds 3
Start-Process "http://localhost:3000"
