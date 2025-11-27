#!/usr/bin/env python3
"""
Run Full Stack (Backend + Frontend Together)

This script starts both the backend API (port 8000) and frontend UI (port 8001)
in separate processes.

Usage:
    python run_full_stack.py
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def run_backend():
    """Start backend server"""
    print("\n" + "=" * 60)
    print("🚀 STARTING BACKEND...")
    print("=" * 60)
    return subprocess.Popen(
        [sys.executable, "run_backend.py"],
        cwd=Path(__file__).parent
    )

def run_frontend():
    """Start frontend server"""
    print("\n" + "=" * 60)
    print("🎨 STARTING FRONTEND...")
    print("=" * 60)
    time.sleep(3)  # Give backend time to start
    return subprocess.Popen(
        [sys.executable, "run_frontend.py"],
        cwd=Path(__file__).parent
    )

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔌 NEXUS HYBRID SEARCH - FULL STACK")
    print("=" * 60)
    
    try:
        backend = run_backend()
        frontend = run_frontend()
        
        print("\n" + "=" * 60)
        print("✅ FULL STACK RUNNING")
        print("=" * 60)
        print("📡 Backend API: http://localhost:8000")
        print("🎨 Frontend UI:  http://localhost:8001")
        print("📚 API Docs:     http://localhost:8000/docs")
        print("=" * 60)
        print("\nPress Ctrl+C to stop both servers...")
        print()
        
        backend.wait()
        frontend.wait()
        
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("🛑 STOPPING SERVERS...")
        print("=" * 60)
        backend.terminate()
        frontend.terminate()
        time.sleep(1)
        backend.kill()
        frontend.kill()
        print("✓ Servers stopped")
