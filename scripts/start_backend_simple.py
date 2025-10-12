#!/usr/bin/env python3
"""
Simple backend startup script
"""

import subprocess
import sys
import os

def start_backend():
    """Start the backend server"""
    print("🚀 Starting LearnSphere Backend...")
    
    # Change to backend directory
    os.chdir("backend")
    
    # Start the server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

if __name__ == "__main__":
    start_backend()
