import requests
import time
import sys

def test_latency(name, url):
    start = time.time()
    try:
        resp = requests.get(url, timeout=15)
        end = time.time()
        print(f"[{name}] Status: {resp.status_code}, Time: {end - start:.4f}s")
    except Exception as e:
        end = time.time()
        print(f"[{name}] ERROR: {str(e)}, Time: {end - start:.4f}s")

if __name__ == "__main__":
    tests = [
        ("Admin Stats", "http://localhost:8000/api/admin/dashboard/stats"),
        ("Admin Activity", "http://localhost:8000/api/admin/dashboard/activity?limit=10"),
        ("Admin User Growth", "http://localhost:8000/api/admin/dashboard/user-growth")
    ]
    for name, url in tests:
        test_latency(name, url)
