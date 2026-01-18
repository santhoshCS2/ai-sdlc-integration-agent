#!/usr/bin/env python3
"""
AI SDLC Integration Agent - Startup Script
Automated setup and launch for the complete platform
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("🚀 AI-Powered SDLC Automation Platform")
    print("   Complete Software Development Life Cycle Automation")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        sys.exit(1)
    print("✅ Python version:", sys.version.split()[0])

def check_node_version():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Node.js version:", result.stdout.strip())
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Node.js is not installed or not in PATH")
    print("   Please install Node.js 16+ from https://nodejs.org/")
    return False

def setup_backend():
    """Setup and start backend server"""
    print("\n📦 Setting up backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    os.chdir(backend_dir)
    
    # Create virtual environment if it doesn't exist
    venv_dir = Path("venv")
    if not venv_dir.exists():
        print("   Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        pip_cmd = ["venv\\Scripts\\pip"]
        python_cmd = ["venv\\Scripts\\python"]
    else:  # Unix/Linux/macOS
        pip_cmd = ["venv/bin/pip"]
        python_cmd = ["venv/bin/python"]
    
    print("   Installing dependencies...")
    subprocess.run(pip_cmd + ["install", "-r", "requirements.txt"], check=True)
    
    # Initialize database
    print("   Initializing database...")
    subprocess.run(python_cmd + ["reset_db.py"])
    
    print("✅ Backend setup complete")
    os.chdir("..")
    return True

def setup_frontend():
    """Setup frontend dependencies"""
    print("\n📦 Setting up frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    os.chdir(frontend_dir)
    
    # Install npm dependencies
    print("   Installing npm dependencies...")
    subprocess.run(["npm", "install"], check=True)
    
    print("✅ Frontend setup complete")
    os.chdir("..")
    return True

def start_backend():
    """Start backend server"""
    print("\n🚀 Starting backend server...")
    
    backend_dir = Path("backend")
    os.chdir(backend_dir)
    
    if os.name == 'nt':  # Windows
        python_cmd = ["venv\\Scripts\\python"]
    else:  # Unix/Linux/macOS
        python_cmd = ["venv/bin/python"]
    
    # Start backend server in background
    backend_process = subprocess.Popen(
        python_cmd + ["-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    os.chdir("..")
    print("✅ Backend server starting on http://localhost:8000")
    return backend_process

def start_frontend():
    """Start frontend development server"""
    print("\n🚀 Starting frontend server...")
    
    frontend_dir = Path("frontend")
    os.chdir(frontend_dir)
    
    # Start frontend server in background
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    os.chdir("..")
    print("✅ Frontend server starting on http://localhost:5173")
    return frontend_process

def wait_for_servers():
    """Wait for servers to be ready"""
    print("\n⏳ Waiting for servers to start...")
    time.sleep(5)
    
    # Check if servers are responding
    try:
        import requests
        
        # Check backend
        backend_response = requests.get("http://localhost:8000/docs", timeout=5)
        if backend_response.status_code == 200:
            print("✅ Backend server is ready")
        
        # Check frontend
        frontend_response = requests.get("http://localhost:5173", timeout=5)
        if frontend_response.status_code == 200:
            print("✅ Frontend server is ready")
            
    except Exception as e:
        print(f"⚠️  Server check failed: {e}")
        print("   Servers may still be starting up...")

def open_browser():
    """Open application in browser"""
    print("\n🌐 Opening application in browser...")
    webbrowser.open("http://localhost:5173")

def print_success_info():
    """Print success information"""
    print("\n" + "=" * 60)
    print("🎉 AI SDLC Integration Agent is now running!")
    print("=" * 60)
    print()
    print("📍 Application URLs:")
    print("   Frontend:     http://localhost:5173")
    print("   Backend API:  http://localhost:8000")
    print("   API Docs:     http://localhost:8000/docs")
    print()
    print("🤖 Available AI Agents:")
    print("   • UI/UX Agent - Design analysis and Figma integration")
    print("   • Architecture Agent - System design and documentation")
    print("   • Impact Analysis Agent - Business and technical assessment")
    print("   • Coding Agent - Production-ready code generation")
    print("   • Testing Agent - Comprehensive test suite generation")
    print("   • Security Agent - Vulnerability assessment")
    print("   • Code Review Agent - Expert-level code analysis")
    print()
    print("📚 Quick Start:")
    print("   1. Upload a PRD document or enter project description")
    print("   2. Select agents to run or use full SDLC automation")
    print("   3. Monitor real-time progress in the dashboard")
    print("   4. Download generated reports and code")
    print()
    print("🛑 To stop the servers, press Ctrl+C")
    print("=" * 60)

def main():
    """Main startup function"""
    print_banner()
    
    # Check system requirements
    print("🔍 Checking system requirements...")
    check_python_version()
    
    if not check_node_version():
        sys.exit(1)
    
    # Setup components
    if not setup_backend():
        sys.exit(1)
    
    if not setup_frontend():
        sys.exit(1)
    
    # Start servers
    backend_process = start_backend()
    frontend_process = start_frontend()
    
    # Wait and check servers
    wait_for_servers()
    
    # Open browser
    open_browser()
    
    # Print success info
    print_success_info()
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Servers stopped successfully")
        print("👋 Thank you for using AI SDLC Integration Agent!")

if __name__ == "__main__":
    main()