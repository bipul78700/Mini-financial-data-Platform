"""
Simple script to run the FastAPI application
Alternative to: uvicorn main:app --reload
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Stock Data Intelligence Dashboard...")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🌐 Dashboard: http://localhost:8000/dashboard")
    print("💡 Press CTRL+C to stop the server\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
