# MLOps-Project

how to start project :
1) launch docker desktop
2) launch terminal -> minikube start -> minikube service ml-service --url
3) launch promotheus -> kubectl port-forward svc/prometheus 9090 -n default
4) launch grafana -> kubectl port-forward -n monitoring deployment/grafana 3000 -> go http://localhost:3000/login (admin)
5) launch service -> kubectl port-forward svc/ml-service 8000:8000 -n default
6) launch fast api server -> uvicorn src.api.main:app --reload --port 8001
7) Make predictions -> Invoke-RestMethod -Uri "http://localhost:8000/predict" `
>>   -Method Post `
>>   -Headers @{"Content-Type"="application/json"} `
>>   -Body '{"text":"This is a test prediction"}'

8) if i have to make a change in api or model : docker build -t adelanseur95/ml-service:latest .
9) don't forget if model is changed, you need to run locally the file to create the model.joblib
