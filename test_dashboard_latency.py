import requests
import time
import json

student_id = "0c88dbbe-197e-4d43-9824-de157ce946e1"

start_time = time.time()
response = requests.get(f"http://localhost:8000/api/dashboard-optimized/student/{student_id}")

end_time = time.time()
print(f"Status Code: {response.status_code}")
print(f"Time Taken: {end_time - start_time:.4f} seconds")
try:
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Response Text: {response.text}")

