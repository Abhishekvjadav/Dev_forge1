#!/usr/bin/env python3
"""
Run Backend Server Only (API on port 8000)

This script starts just the FastAPI backend without serving the frontend.
Use this if you want to run the frontend separately.

Usage:
    python run_backend.py
"""

import uvicorn
from app.main import create_app

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 STARTING HYBRID SEARCH BACKEND")
    print("=" * 60)
    print("✓ API will be available at: http://localhost:8000")
    print("✓ Swagger docs at: http://localhost:8000/docs")
    print("✓ ReDoc docs at: http://localhost:8000/redoc")
    print("✓ Open a separate terminal to run: python run_frontend.py")
    print("=" * 60)
    print()
    
    app = create_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
