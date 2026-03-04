import requests

url = "http://localhost:8000/api/admin/dashboard/activity?limit=10"
print(f"Fetching {url}")

try:
    resp = requests.get(url, timeout=25)
    print(resp.status_code)
    try:
        print(resp.json())
    except:
        print(resp.text)
except Exception as e:
    print(e)
