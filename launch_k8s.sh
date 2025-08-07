#!/bin/bash

# Start Minikube cluster
minikube start --driver=docker --cpus=4 --memory=6g --disk-size=20g

# Set up Docker environment
eval $(minikube docker-env)

# Build your ML service image
docker build -t ml-service:latest .

# Deploy all Kubernetes manifests
kubectl apply -f k8s/

# Wait for deployments to be ready
echo "Waiting for services to become ready..."
kubectl wait --for=condition=available --timeout=300s deployment/ml-service -n default
kubectl wait --for=condition=available --timeout=300s deployment/prometheus -n monitoring
kubectl wait --for=condition=available --timeout=300s deployment/grafana -n monitoring

# Set up port forwarding in background
echo "Setting up port forwarding..."
kubectl port-forward svc/ml-service 8000:8000 -n default &
kubectl port-forward svc/prometheus 9090:9090 -n monitoring &
kubectl port-forward svc/grafana 3000:3000 -n monitoring &

# Get service URLs
echo -e "\nService Endpoints:"
echo "ML Service: http://localhost:8000"
echo "Prometheus: http://localhost:9090"
echo "Grafana:    http://localhost:3000 (admin/admin)"
echo "Minikube Dashboard: $(minikube service ml-service --url -n default)"

# Open Grafana in default browser
start http://localhost:3000   # Windows

# Keep the script running to maintain port forwarding
wait
