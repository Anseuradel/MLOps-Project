# MLOps-Project

how to start project :
1) launch docker desktop
2) launch terminal -> minikube start -> minikube service ml-service --url
3) - launch promotheus (only scrapes ml-service) -> kubectl port-forward svc/prometheus 9090 -n default
   - launch prometheus (only for api metrics (cpu usage etc) -> kubectl port-forward svc/kube-prometheus-stack-prometheus -n monitoring 9090:9090
5) launch grafana -> kubectl port-forward -n monitoring deployment/grafana 3000 -> go http://localhost:3000/login (admin)
6) launch service -> kubectl port-forward svc/ml-service 8000:8000 -n default
7) launch fast api server -> uvicorn src.api.main:app --reload --port 8001
8) Make predictions -> Invoke-RestMethod -Uri "http://localhost:8000/predict" `
>>   -Method Post `
>>   -Headers @{"Content-Type"="application/json"} `
>>   -Body '{"text":"This is a test prediction"}'

8) if i have to make a change in api or model : docker build -t adelanseur95/ml-service:latest .
9) don't forget if model is changed, you need to run locally the file to create the model.joblib
10) Build & push the new image with the model


    docker build -t adelanseur95/ml-service:latest .
    docker push adelanseur95/ml-service:latest
    
    
    kubectl set image deployment/ml-service ml-service=adelanseur95/ml-service:latest -n default
    
    kubectl get pods -w
    
    kubectl port-forward svc/ml-service 8000:8000 -n default
    
    Invoke-RestMethod -Uri "http://localhost:8000/predict" `
      -Method Post `
      -Headers @{"Content-Type"="application/json"} `
      -Body '{"text":"This is a test prediction"}'
