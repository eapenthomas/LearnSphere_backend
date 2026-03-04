import os
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

res = supabase.table("study_buddy_requests").select("*").execute()
print("Total Requests:", len(res.data))
for req in res.data:
    print(f"Request ID: {req['id']} | Sender: {req['sender_id']} | Receiver: {req['receiver_id']} | Status: {req['status']}")
