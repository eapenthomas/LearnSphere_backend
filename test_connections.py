import requests

url = "http://localhost:8000/api/study-buddy/connections/101b5f33-4fcc-46b1-aacc-ec8886df87f1"
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYTFiMmMzZDQtZTVmNi03ODkwLWFiY2QtZWYxMjM0NTY3ODkwIiwiZW1haWwiOiJhbGV4LnR1cm5lckB0ZXN0bWFpbC5jb20iLCJyb2xlIjoic3R1ZGVudCIsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE3NzI1Mjg2MDJ9.wtj3N6KZVQ4kgKNjD6bMCxWmVc4FMYlxQPWntUnBRs4"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    import traceback
    traceback.print_exc()
