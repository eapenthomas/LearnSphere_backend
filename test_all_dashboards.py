import requests
import time
import sys

def test_latency(name, url):
    start = time.time()
    try:
        resp = requests.get(url, timeout=10)
        end = time.time()
        print(f"[{name}] Status: {resp.status_code}, Time: {end - start:.4f}s")
    except Exception as e:
        end = time.time()
        print(f"[{name}] ERROR: {str(e)}, Time: {end - start:.4f}s")

if __name__ == "__main__":
    tests = [
        ("Student Dashboard", "http://localhost:8000/api/dashboard-optimized/student/cfaba16c-e57d-419b-abf7-463d1a88bb3e"),
        ("Admin Stats", "http://localhost:8000/api/admin/dashboard/stats"),
        ("Teacher Batch", "http://localhost:8000/api/teacher/dashboard/batch/ea6909bd-fec9-485a-ade9-d9c0879c9451")
    ]
    for name, url in tests:
        test_latency(name, url)
