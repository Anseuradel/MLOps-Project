# MLOps-Project

how to start project :
1) launch docker desktop
2) launch terminal -> minikube start -> minikube service ml-service --url
3) launch promotheus -> kubectl port-forward svc/prometheus 9090 -n default
4) launch grafana -> kubectl port-forward -n monitoring deployment/grafana 3000 -> go http://localhost:3000/login (admin)
