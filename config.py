"""
Configuration management for the application
Uses environment variables with sensible defaults
"""

import os
from typing import List

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stock_data.db")

# CORS Configuration (comma-separated list; include your Render URL if frontend is on same or different Render service)
ALLOWED_ORIGINS_STR = os.getenv(
    "ALLOWED_ORIGINS",
    "https://bipul78700.github.io,http://localhost:8000,http://127.0.0.1:8000"
)
ALLOWED_ORIGINS = [o.strip() for o in ALLOWED_ORIGINS_STR.split(",") if o.strip()]

# Add wildcard for development if explicitly set
CORS_ALLOW_ALL = os.getenv("CORS_ALLOW_ALL", "false").lower() == "true"
if CORS_ALLOW_ALL:
    ALLOWED_ORIGINS.append("*")

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "10000"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Data Collection Configuration
DEFAULT_DATA_PERIOD = os.getenv("DEFAULT_DATA_PERIOD", "1y")
MAX_DAYS_PARAM = int(os.getenv("MAX_DAYS_PARAM", "365"))

# Application Metadata
APP_NAME = "Stock Data Intelligence Dashboard"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "A comprehensive API for stock market data analysis and insights"
