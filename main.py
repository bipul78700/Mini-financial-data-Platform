"""
Stock Data Intelligence Dashboard
Main FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from api.routes import router
from models.database import init_db
import os

# Initialize FastAPI app
app = FastAPI(
    title="Stock Data Intelligence Dashboard",
    description="A comprehensive API for stock market data analysis and insights",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://bipul78700.github.io",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["Stock Data"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("🚀 Stock Data Intelligence Dashboard API is ready!")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Stock Data Intelligence Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "companies": "/api/companies",
            "stock_data": "/api/data/{symbol}",
            "summary": "/api/summary/{symbol}",
            "compare": "/api/compare?symbol1=TCS&symbol2=INFY"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Stock Data Intelligence Dashboard"}


@app.get("/dashboard")
async def dashboard():
    """Serve the HTML dashboard"""
    dashboard_path = os.path.join(os.path.dirname(__file__), "templates", "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    else:
        return {"error": "Dashboard file not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
