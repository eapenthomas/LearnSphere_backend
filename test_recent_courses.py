import requests
import json

url = "http://localhost:8000/api/dashboard-optimized/student/cfaba16c-e57d-419b-abf7-463d1a88bb3e"
resp = requests.get(url)
data = resp.json()
print("Recent Courses Sample:")
print(json.dumps(data.get("recent_courses", [])[:2], indent=2))
