import asyncio
import time
import httpx

async def fetch_url(client, name, url):
    start = time.time()
    try:
        resp = await client.get(url, timeout=30.0)
        end = time.time()
        print(f"[{name}] Status: {resp.status_code}, Time: {end - start:.4f}s")
    except Exception as e:
        end = time.time()
        print(f"[{name}] ERROR: {str(e)}, Time: {end - start:.4f}s")

async def main():
    import json
    urls = [
        ("Admin Stats", "http://localhost:8000/api/admin/dashboard/stats"),
        ("Admin Activity", "http://localhost:8000/api/admin/dashboard/activity?limit=10"),
        ("Admin User Growth", "http://localhost:8000/api/admin/dashboard/user-growth"),
        ("Teacher Batch", "http://localhost:8000/api/teacher/dashboard/batch/ea6909bd-fec9-485a-ade9-d9c0879c9451"),
        ("Student Dashboard", "http://localhost:8000/api/dashboard-optimized/student/cfaba16c-e57d-419b-abf7-463d1a88bb3e")
    ]
    
    async with httpx.AsyncClient() as client:
        # Measure total time to load all dashboards concurrently
        start_all = time.time()
        tasks = [fetch_url(client, name, url) for name, url in urls]
        await asyncio.gather(*tasks)
        print(f"\nTOTAL CONCURRENT BATCH TIME: {time.time() - start_all:.4f}s")

if __name__ == "__main__":
    asyncio.run(main())
