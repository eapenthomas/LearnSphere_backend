import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def find_teacher():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(url, key)
    
    res = supabase.table("profiles").select("id, full_name, role").ilike("full_name", "%Aura%").execute()
    print(res.data)

if __name__ == "__main__":
    find_teacher()
