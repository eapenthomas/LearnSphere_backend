#!/usr/bin/env python3
"""
LearnSphere Professional Startup Script
Automatically starts both backend and frontend servers
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_banner():
    """Print professional startup banner"""
    print("=" * 80)
    print("🎓 LearnSphere - Professional Learning Management System")
    print("=" * 80)
    print("🚀 Starting servers...")
    print()

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    # Check Python
    try:
        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 8:
            print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        else:
            print("❌ Python 3.8+ required")
            return False
    except:
        print("❌ Python not found")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()}")
        else:
            print("❌ Node.js not found")
            return False
    except:
        print("❌ Node.js not found")
        return False
    
    # Check npm (try multiple paths)
    npm_paths = ["npm", "npm.cmd", "C:\\Program Files\\nodejs\\npm.cmd"]
    npm_found = False
    
    for npm_path in npm_paths:
        try:
            result = subprocess.run([npm_path, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ npm {result.stdout.strip()}")
                npm_found = True
                break
        except:
            continue
    
    if not npm_found:
        print("❌ npm not found")
        print("   Please ensure Node.js and npm are installed and in PATH")
        return False
    
    print()
    return True

def start_backend():
    """Start the backend server"""
    print("🔧 Starting Backend Server...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Check if .env exists
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("⚠️  .env file not found in backend directory")
        print("   Please create .env file with your Supabase credentials")
    
    try:
        # Start backend server
        backend_process = subprocess.Popen(
            [sys.executable, "main.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✅ Backend server starting...")
        print("   📍 Backend URL: http://localhost:8000")
        print("   📚 API Docs: http://localhost:8000/docs")
        
        return backend_process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the frontend server"""
    print("\n🌐 Starting Frontend Server...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("📦 Installing frontend dependencies...")
        try:
            # Try different npm paths
            npm_paths = ["npm", "npm.cmd", "C:\\Program Files\\nodejs\\npm.cmd"]
            for npm_path in npm_paths:
                try:
                    subprocess.run([npm_path, "install"], cwd=frontend_dir, check=True)
                    print("✅ Dependencies installed")
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
            else:
                print("❌ Failed to install dependencies - npm not found")
                return None
        except Exception as e:
            print(f"❌ Failed to install dependencies: {e}")
            return None
    
    try:
        # Find working npm path
        npm_paths = ["npm", "npm.cmd", "C:\\Program Files\\nodejs\\npm.cmd"]
        npm_path = None
        
        for path in npm_paths:
            try:
                result = subprocess.run([path, "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    npm_path = path
                    break
            except:
                continue
        
        if not npm_path:
            print("❌ npm not found")
            return None
        
        # Start frontend server with npm run dev
        frontend_process = subprocess.Popen(
            [npm_path, "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("✅ Frontend server starting...")
        print("   📍 Frontend URL: http://localhost:3000")
        
        return frontend_process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def wait_for_servers():
    """Wait for servers to start and open browser"""
    print("\n⏳ Waiting for servers to start...")
    time.sleep(5)
    
    print("\n🌐 Opening LearnSphere in your browser...")
    try:
        webbrowser.open("http://localhost:3000")
        print("✅ Browser opened successfully")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("   Please manually open: http://localhost:3000")

def display_info():
    """Display important information"""
    print("\n" + "=" * 80)
    print("🎉 LearnSphere is now running!")
    print("=" * 80)
    print()
    print("📊 Available URLs:")
    print("   🌐 Frontend Application: http://localhost:3000")
    print("   🔧 Backend API: http://localhost:8000")
    print("   📚 API Documentation: http://localhost:8000/docs")
    print("   🏥 Health Check: http://localhost:8000/health")
    print()
    print("📋 Useful Commands:")
    print("   📊 Generate API Performance Report: python api_performance_report.py")
    print("   📊 Analyze Supabase Performance: python supabase_performance_analyzer.py")
    print()
    print("⚠️  To stop the servers, press Ctrl+C")
    print("=" * 80)

def main():
    """Main startup function"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        print("❌ Requirements not met. Please install the required tools.")
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend server")
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend server")
        backend_process.terminate()
        sys.exit(1)
    
    # Wait and open browser
    wait_for_servers()
    
    # Display info
    display_info()
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        
        # Terminate processes
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        
        print("✅ Servers stopped successfully")
        print("👋 Thank you for using LearnSphere!")

if __name__ == "__main__":
    main()
