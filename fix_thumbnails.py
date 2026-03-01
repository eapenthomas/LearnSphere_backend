import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def fix_thumbnails():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(url, key)

    # Fetch all courses with missing or empty thumbnails
    res = supabase.table("courses").select("id, title, thumbnail_url").execute()
    courses = res.data or []

    # Thumbnail map by keyword in title
    thumbnail_map = [
        ("active directory",       "https://images.unsplash.com/photo-1558494949-ef010cbdcc51?auto=format&fit=crop&w=800&q=80"),
        ("entra",                  "https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80"),
        ("azure",                  "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80"),
        ("aws",                    "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80"),
        ("cisco",                  "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?auto=format&fit=crop&w=800&q=80"),
        ("networking",             "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?auto=format&fit=crop&w=800&q=80"),
        ("google cloud",           "https://images.unsplash.com/photo-1677442135768-1f9c91277acc?auto=format&fit=crop&w=800&q=80"),
        ("kubernetes",             "https://images.unsplash.com/photo-1605745341112-85968b193ef5?auto=format&fit=crop&w=800&q=80"),
        ("docker",                 "https://images.unsplash.com/photo-1605745341112-85968b193ef5?auto=format&fit=crop&w=800&q=80"),
        ("cybersecurity",          "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=800&q=80"),
        ("security",               "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=800&q=80"),
        ("linux",                  "https://images.unsplash.com/photo-1629654297299-c8506221ca97?auto=format&fit=crop&w=800&q=80"),
        ("python",                 "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80"),
        ("devops",                 "https://images.unsplash.com/photo-1627163439134-7a8c47e08208?auto=format&fit=crop&w=800&q=80"),
        ("machine learning",       "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=800&q=80"),
        ("data",                   "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80"),
        ("web",                    "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=800&q=80"),
    ]

    # Default fallback thumbnail
    DEFAULT_THUMB = "https://images.unsplash.com/photo-1488190211105-8b0e65b80b4e?auto=format&fit=crop&w=800&q=80"

    updated = 0
    for course in courses:
        thumb = course.get("thumbnail_url") or ""
        if thumb.strip():
            continue  # already has a thumbnail

        title_lower = course["title"].lower()
        new_thumb = DEFAULT_THUMB
        for keyword, img_url in thumbnail_map:
            if keyword in title_lower:
                new_thumb = img_url
                break

        supabase.table("courses").update({"thumbnail_url": new_thumb}).eq("id", course["id"]).execute()
        print(f"✅ Updated: {course['title']} → {new_thumb[:60]}...")
        updated += 1

    print(f"\n✅ Done. {updated} courses updated.")

if __name__ == "__main__":
    fix_thumbnails()
