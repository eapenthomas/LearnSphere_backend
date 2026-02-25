import os
import uuid
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def create_courses():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase: Client = create_client(url, key)
    
    teacher_id = "2fdd3af3-2520-48f8-a367-642e6ed3a9e7" # Aura
    
    courses = [
        {
            "title": "Microsoft Active Directory Administration",
            "description": "Master AD DS, GPOs, and Domain Controller management in Windows Server environments.",
            "code": "AD-101",
            "thumbnail_url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc51?auto=format&fit=crop&w=800&q=80"
        },
        {
            "title": "Microsoft Entra ID (Formerly Azure AD)",
            "description": "Learn modern identity management, SSO, and Conditional Access in the cloud.",
            "code": "ENTRA-200",
            "thumbnail_url": "https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80"
        },
        {
            "title": "Azure Cloud Architecture (AZ-305)",
            "description": "Design high-availability solutions and migrate workloads to Microsoft Azure.",
            "code": "AZ-305",
            "thumbnail_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80"
        },
        {
            "title": "AWS Solutions Architect Associate",
            "description": "Comprehensive guide to EC2, S3, RDS, and scalable VPC design on AWS.",
            "code": "AWS-SAA",
            "thumbnail_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80"
        },
        {
            "title": "Cisco Networking Fundamentals (CCNA)",
            "description": "The foundation of networking: Switching, Routing, and IP connectivity.",
            "code": "CCNA-2024",
            "thumbnail_url": "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?auto=format&fit=crop&w=800&q=80"
        },
        {
            "title": "Google Cloud Platform Fundamentals",
            "description": "Introduction to GCP services: Compute Engine, BigQuery, and App Engine.",
            "code": "GCP-101",
            "thumbnail_url": "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?auto=format&fit=crop&w=800&q=80"
        },
        {
            "title": "Kubernetes & Docker Containerization",
            "description": "Learn to containerize applications and manage them with K8s orchestration.",
            "code": "K8S-DEVOPS",
            "thumbnail_url": "https://images.unsplash.com/photo-1605745341112-85968b193ef5?auto=format&fit=crop&w=800&q=80"
        },
        {
            "title": "Cybersecurity: Network Defense",
            "description": "Protect your infrastructure from modern threats and learn ethical hacking.",
            "code": "SEC-NET",
            "thumbnail_url": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=800&q=80"
        },
        {
            "title": "Linux System Administration (LPIC-1)",
            "description": "Master the Linux command line, shell scripting, and user management.",
            "code": "LNX-ADM",
            "thumbnail_url": "https://images.unsplash.com/photo-1629654297299-c8506221ca97?auto=format&fit=crop&w=800&q=80"
        },
        {
            "title": "Python for DevOps & Automation",
            "description": "Automate routine tasks and build infrastructure-as-code scripts with Python.",
            "code": "PY-DEV",
            "thumbnail_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80"
        }
    ]
    
    for c in courses:
        data = {
            "teacher_id": teacher_id,
            "title": c["title"],
            "description": c["description"],
            "code": c["code"],
            "thumbnail_url": c["thumbnail_url"],
            "status": "active"
        }
        try:
            res = supabase.table("courses").insert(data).execute()
            print(f"✅ Created course: {c['title']}")
        except Exception as e:
            print(f"❌ Failed to create {c['title']}: {e}")

if __name__ == "__main__":
    create_courses()
