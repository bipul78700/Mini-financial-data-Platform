"""
Stock Data Intelligence Dashboard
Main FastAPI application entry point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from api.routes import router
from models.database import init_db
import logging
import os
import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Initializing database...")
    init_db()
    logger.info("🚀 Stock Data Intelligence Dashboard API is ready!")
    yield
    # Shutdown (if needed in future)
    logger.info("Shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title=config.APP_NAME,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["Stock Data"])


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
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
