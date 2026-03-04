import os
from supabase import create_client

url = "https://ffspaottcgyalpagbxvx.supabase.co"
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not key:
    print("WARNING: Key not found in env.")

try:
    supabase = create_client(url, key)

    print("--- ALL REQUESTS ---")
    res = supabase.table("study_buddy_requests").select("*").execute()
    count = 0
    for req in res.data:
        print(req)
        count += 1
    print(f"Total Requests: {count}")

    print("\n--- PROFILES ---")
    res2 = supabase.table("profiles").select("id, email, full_name").execute()
    for p in res2.data:
        if p['email'] in ['alex.turner@testmail.com', 'rena.danny@testmail.com']:
            print(p)
except Exception as e:
    print("Error:", e)
