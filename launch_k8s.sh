#!/bin/bash

# Start Minikube with extra resources
minikube start --driver=docker --cpus=4 --memory=8g --disk-size=20g
eval $(minikube docker-env)

# Build and load Docker image
docker build -t ml-service:latest .

# Apply all Kubernetes manifests
kubectl apply -f k8s/

# Wait for services
echo "Waiting for services to become ready..."
kubectl wait --for=condition=available deployment/ml-service --timeout=120s
kubectl wait --for=condition=available deployment/prometheus --timeout=120s -n monitoring
kubectl wait --for=condition=available deployment/grafana --timeout=120s -n monitoring

# Set up port forwarding
kubectl port-forward svc/ml-service 8000:8000 &
kubectl port-forward svc/prometheus 9090:9090 -n monitoring &
kubectl port-forward svc/grafana 3000:3000 -n monitoring &

# Display info
echo -e "\n\033[1mAccess URLs:\033[0m"
echo "ML Service: http://localhost:8000"
echo "Prometheus: http://localhost:9090"
echo "Grafana:    http://localhost:3000 (admin/admin)"
echo "Minikube Dashboard: $(minikube service ml-service --url)"

# Open Grafana
xdg-open http://localhost:3000  # Linux
# open http://localhost:3000    # Mac
# start http://localhost:3000   # Windows

wait
