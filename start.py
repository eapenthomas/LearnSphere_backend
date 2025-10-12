#!/usr/bin/env python3
"""
LearnSphere Quick Start Script
Simple script to start the development environment
"""

import subprocess
import sys
import os

def main():
    print("🚀 LearnSphere Development Environment")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ Error: Please run this script from the LearnSphere root directory")
        sys.exit(1)
    
    print("📁 Current directory:", os.getcwd())
    print("🔧 Available startup options:")
    print("1. Start Backend Only")
    print("2. Start Frontend Only") 
    print("3. Start Both (Development)")
    print("4. Start Professional Environment")
    print("5. Exit")
    
    choice = input("\n👉 Select option (1-5): ").strip()
    
    if choice == "1":
        print("🔧 Starting Backend Server...")
        subprocess.run([sys.executable, "scripts/start_backend_simple.py"])
    elif choice == "2":
        print("🎨 Starting Frontend Development Server...")
        os.chdir("frontend")
        subprocess.run(["npm", "run", "dev"])
    elif choice == "3":
        print("🚀 Starting Full Development Environment...")
        subprocess.run([sys.executable, "scripts/start_dev.py"])
    elif choice == "4":
        print("💼 Starting Professional Environment...")
        subprocess.run([sys.executable, "scripts/start_learnsphere_professional.py"])
    elif choice == "5":
        print("👋 Goodbye!")
        sys.exit(0)
    else:
        print("❌ Invalid choice. Please select 1-5.")
        main()

if __name__ == "__main__":
    main()
