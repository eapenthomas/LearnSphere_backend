import os
from supabase import create_client, Client
from dotenv import load_dotenv
import json

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

res = supabase.table("enrollments").select("student_id").limit(1).execute()
student_id = res.data[0]["student_id"] if res.data else None

if student_id:
    import requests
    url = f"http://localhost:8000/api/dashboard-optimized/student/{student_id}"
    resp = requests.get(url)
    data = resp.json()
    with open("dump.json", "w", encoding="utf-8") as f:
        json.dump(data.get("recent_courses", [])[:1], f, indent=2)
else:
    print("No enrollments found.")
