#!/usr/bin/env python3
"""
LearnSphere Professional Startup Script
Starts both backend and frontend servers with professional output
"""

import subprocess
import sys
import os
import time
import threading
import webbrowser
from pathlib import Path

def print_banner():
    """Print professional startup banner"""
    print("=" * 80)
    print("🚀 LearnSphere - Professional Learning Management System")
    print("=" * 80)
    print("📅 Started:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print("🌐 Backend: FastAPI + Supabase")
    print("⚛️  Frontend: React + Vite + TailwindCSS")
    print("=" * 80)

def start_backend():
    """Start the FastAPI backend server"""
    print("\n🔧 Starting Backend Server...")
    print("-" * 50)
    
    try:
        # Change to backend directory
        os.chdir("backend")
        
        # Start the server
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Stream output
        for line in process.stdout:
            if "Uvicorn running on" in line:
                print("✅ Backend server started successfully!")
                print(f"🌐 Backend URL: http://localhost:8000")
                print(f"📚 API Docs: http://localhost:8000/docs")
                print("-" * 50)
            elif "ERROR" in line or "Exception" in line:
                print(f"❌ Backend Error: {line.strip()}")
            elif "INFO" in line:
                print(f"📝 {line.strip()}")
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the React frontend server"""
    print("\n⚛️  Starting Frontend Server...")
    print("-" * 50)
    
    try:
        # Change to frontend directory
        os.chdir("../frontend")
        
        # Start the development server
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Stream output
        for line in process.stdout:
            if "Local:" in line:
                print("✅ Frontend server started successfully!")
                print(f"🌐 Frontend URL: http://localhost:3000")
                print("-" * 50)
                # Auto-open browser
                time.sleep(2)
                webbrowser.open("http://localhost:3000")
                print("🚀 Browser opened automatically!")
            elif "ERROR" in line or "Error:" in line:
                print(f"❌ Frontend Error: {line.strip()}")
            elif "warn" in line.lower():
                print(f"⚠️  {line.strip()}")
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def check_dependencies():
    """Check if all dependencies are installed"""
    print("\n🔍 Checking Dependencies...")
    print("-" * 50)
    
    # Check backend dependencies
    backend_path = Path("backend/requirements.txt")
    if backend_path.exists():
        print("✅ Backend requirements.txt found")
    else:
        print("❌ Backend requirements.txt not found")
        return False
    
    # Check frontend dependencies
    frontend_path = Path("frontend/package.json")
    if frontend_path.exists():
        print("✅ Frontend package.json found")
    else:
        print("❌ Frontend package.json not found")
        return False
    
    # Check environment file
    env_path = Path("backend/.env")
    if env_path.exists():
        print("✅ Environment file found")
    else:
        print("⚠️  Environment file not found - using defaults")
    
    print("-" * 50)
    return True

def show_quick_links():
    """Show quick access links"""
    print("\n🔗 Quick Access Links:")
    print("-" * 50)
    print("🌐 Frontend:     http://localhost:3000")
    print("🔧 Backend API:  http://localhost:8000")
    print("📚 API Docs:     http://localhost:8000/docs")
    print("📊 Admin Panel:  http://localhost:3000/admin")
    print("👨‍🎓 Student:     http://localhost:3000/student")
    print("👨‍🏫 Teacher:     http://localhost:3000/teacher")
    print("-" * 50)

def main():
    """Main startup function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Missing dependencies. Please run setup first.")
        return
    
    # Start servers in separate threads
    backend_thread = threading.Thread(target=start_backend)
    frontend_thread = threading.Thread(target=start_frontend)
    
    try:
        # Start backend first
        backend_thread.start()
        time.sleep(3)  # Wait for backend to start
        
        # Start frontend
        frontend_thread.start()
        time.sleep(3)  # Wait for frontend to start
        
        # Show quick links
        show_quick_links()
        
        print("\n🎉 LearnSphere is now running!")
        print("📝 Press Ctrl+C to stop all servers")
        print("=" * 80)
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down LearnSphere...")
        print("✅ All servers stopped successfully!")
        print("👋 Thank you for using LearnSphere!")

if __name__ == "__main__":
    main()
