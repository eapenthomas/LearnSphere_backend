#!/usr/bin/env python3
"""
LearnSphere Development Server Startup Script
Professional startup with clean output and health checks
"""

import os
import sys
import time
import subprocess
import threading
import requests
from datetime import datetime

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class DevServerManager:
    """Professional development server manager"""
    
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3001"
        
    def log(self, message: str, color: str = Colors.OKBLUE):
        """Log message with timestamp and color"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] {message}{Colors.ENDC}")
        
    def check_port(self, port: int) -> bool:
        """Check if port is available"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
    
    def wait_for_server(self, url: str, timeout: int = 30) -> bool:
        """Wait for server to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code in [200, 404]:  # 404 is OK for some endpoints
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        return False
    
    def start_backend(self):
        """Start backend server with clean output"""
        self.log("🚀 Starting Backend Server...", Colors.HEADER)
        
        # Check if port 8000 is available
        if not self.check_port(8000):
            self.log("⚠️  Port 8000 is already in use", Colors.WARNING)
            return False
        
        try:
            # Change to backend directory
            backend_dir = os.path.join(os.getcwd(), "backend")
            
            # Start backend process with suppressed output
            self.backend_process = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for backend to be ready
            self.log("⏳ Waiting for backend to initialize...", Colors.OKCYAN)
            if self.wait_for_server(self.backend_url):
                self.log("✅ Backend server ready at http://localhost:8000", Colors.OKGREEN)
                return True
            else:
                self.log("❌ Backend server failed to start", Colors.FAIL)
                return False
                
        except Exception as e:
            self.log(f"❌ Backend startup error: {str(e)}", Colors.FAIL)
            return False
    
    def start_frontend(self):
        """Start frontend server with clean output"""
        self.log("🎨 Starting Frontend Server...", Colors.HEADER)
        
        try:
            # Change to frontend directory
            frontend_dir = os.path.join(os.getcwd(), "frontend")
            
            # Start frontend process with suppressed output
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for frontend to be ready
            self.log("⏳ Waiting for frontend to build...", Colors.OKCYAN)
            time.sleep(5)  # Give Vite time to start
            
            if self.wait_for_server(self.frontend_url):
                self.log("✅ Frontend server ready at http://localhost:3001", Colors.OKGREEN)
                return True
            else:
                self.log("❌ Frontend server failed to start", Colors.FAIL)
                return False
                
        except Exception as e:
            self.log(f"❌ Frontend startup error: {str(e)}", Colors.FAIL)
            return False
    
    def monitor_processes(self):
        """Monitor server processes for errors"""
        def monitor_backend():
            if self.backend_process:
                stdout, stderr = self.backend_process.communicate()
                if stderr and "error" in stderr.lower():
                    self.log(f"⚠️  Backend error: {stderr[:100]}...", Colors.WARNING)
        
        def monitor_frontend():
            if self.frontend_process:
                stdout, stderr = self.frontend_process.communicate()
                if stderr and "error" in stderr.lower() and "postcss" not in stderr.lower():
                    self.log(f"⚠️  Frontend error: {stderr[:100]}...", Colors.WARNING)
        
        # Start monitoring threads
        if self.backend_process:
            threading.Thread(target=monitor_backend, daemon=True).start()
        if self.frontend_process:
            threading.Thread(target=monitor_frontend, daemon=True).start()
    
    def health_check(self):
        """Perform health check on running servers"""
        self.log("🔍 Performing health check...", Colors.HEADER)
        
        # Check backend
        try:
            response = requests.get(self.backend_url, timeout=5)
            self.log("✅ Backend health check passed", Colors.OKGREEN)
        except:
            self.log("❌ Backend health check failed", Colors.FAIL)
        
        # Check frontend
        try:
            response = requests.get(self.frontend_url, timeout=5)
            self.log("✅ Frontend health check passed", Colors.OKGREEN)
        except:
            self.log("❌ Frontend health check failed", Colors.FAIL)
    
    def display_info(self):
        """Display server information"""
        self.log("=" * 60, Colors.HEADER)
        self.log("🎓 LearnSphere Development Environment Ready", Colors.HEADER)
        self.log("=" * 60, Colors.HEADER)
        self.log("📊 Backend API:     http://localhost:8000", Colors.OKBLUE)
        self.log("🎨 Frontend App:    http://localhost:3001", Colors.OKBLUE)
        self.log("📚 Documentation:   docs/README.md", Colors.OKBLUE)
        self.log("🧪 Run Tests:       python tests/test_suite.py", Colors.OKBLUE)
        self.log("=" * 60, Colors.HEADER)
        self.log("💡 Voice Navigation: Say 'Hey dashboard' to test", Colors.OKCYAN)
        self.log("📅 Deadline Cards:   Check student dashboard", Colors.OKCYAN)
        self.log("🔧 Admin Panel:      Login as admin user", Colors.OKCYAN)
        self.log("=" * 60, Colors.HEADER)
        self.log("Press Ctrl+C to stop all servers", Colors.WARNING)
    
    def cleanup(self):
        """Clean up processes on exit"""
        self.log("🛑 Shutting down servers...", Colors.WARNING)
        
        if self.backend_process:
            self.backend_process.terminate()
            self.log("✅ Backend server stopped", Colors.OKGREEN)
        
        if self.frontend_process:
            self.frontend_process.terminate()
            self.log("✅ Frontend server stopped", Colors.OKGREEN)
    
    def start_development_environment(self):
        """Start complete development environment"""
        try:
            self.log("🚀 LearnSphere Development Server Startup", Colors.HEADER)
            self.log("=" * 60, Colors.HEADER)
            
            # Start backend
            if not self.start_backend():
                return False
            
            # Start frontend
            if not self.start_frontend():
                return False
            
            # Monitor processes
            self.monitor_processes()
            
            # Health check
            time.sleep(2)
            self.health_check()
            
            # Display info
            self.display_info()
            
            # Keep running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.cleanup()
                return True
                
        except Exception as e:
            self.log(f"❌ Startup failed: {str(e)}", Colors.FAIL)
            self.cleanup()
            return False

def main():
    """Main startup function"""
    # Change to project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    # Start development environment
    manager = DevServerManager()
    success = manager.start_development_environment()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
