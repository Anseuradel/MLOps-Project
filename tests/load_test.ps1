# load_test.ps1
$headers = @{"Content-Type"="application/json"}
$body = '{"text":"This is a test"}'
Invoke-WebRequest -Uri "http://localhost:8000/predict" -Method Post -Headers $headers -Body $body
