"""
Convenience Launcher for Enterprise Decision Intelligence Platform
Launches FastAPI backend server on port 8000
"""
import sys
import uvicorn
from config.settings import settings

if __name__ == "__main__":
    print("=" * 75)
    print(" Enterprise AI Business Decision Intelligence Platform")
    print("=" * 75)
    print(" Starting FastAPI Backend Server on http://localhost:8000 ...")
    print(" Interactive Swagger API Docs: http://localhost:8000/docs")
    print(" Redoc Alternative Docs:       http://localhost:8000/redoc")
    print(" React Frontend (dev server):   http://localhost:5173")
    print("=" * 75)
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
