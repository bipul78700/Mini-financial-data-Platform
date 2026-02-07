# Stock Data Intelligence Dashboard

A comprehensive financial data platform built with Python and FastAPI that demonstrates data collection, processing, REST API development, and analytical metrics for stock market data.

## 🎯 Project Overview

This project is a mini financial data platform that:
- Collects real-time stock market data using yfinance
- Processes and cleans data with calculated metrics
- Provides RESTful APIs for data access and analysis
- Includes analytical insights and comparisons

## ⚙️ Tech Stack

- **Language**: Python 3.8+
- **Backend Framework**: FastAPI
- **Database**: SQLite (SQLAlchemy ORM)
- **Data Source**: yfinance (Yahoo Finance API)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly (optional)

## 📁 Project Structure

```
Stock-Data-Intelligence-Dashboard/
│
├── api/
│   ├── __init__.py
│   └── routes.py          # FastAPI route handlers
│
├── data/
│   ├── __init__.py
│   ├── collector.py       # Data collection from yfinance
│   └── processor.py       # Data cleaning and metrics calculation
│
├── models/
│   ├── __init__.py
│   └── database.py        # SQLite database models
│
├── utils/
│   ├── __init__.py
│   └── helpers.py         # Utility functions
│
├── templates/
│   └── dashboard.html     # HTML dashboard with visualizations
│
├── main.py                # FastAPI application entry point
├── run.py                 # Alternative script to run the app
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd Stock-Data-Intelligence-Dashboard
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python run.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   Or run main.py directly:
   ```bash
   python main.py
   ```

5. **Access the Application**
   - API Base URL: `http://localhost:8000`
   - Interactive API Docs (Swagger): `http://localhost:8000/docs`
   - Alternative API Docs (ReDoc): `http://localhost:8000/redoc`
   - **Web Dashboard**: `http://localhost:8000/dashboard`

## 🌐 Web Dashboard

The project includes a beautiful, interactive web dashboard for visualizing stock data:

- **Access**: Navigate to `http://localhost:8000/dashboard` after starting the server
- **Features**:
  - Real-time stock data visualization
  - Interactive charts (Closing Price, Daily Returns, Moving Averages, Volatility)
  - Stock comparison tool
  - Summary statistics display
  - Responsive design with modern UI

The dashboard uses Chart.js for visualizations and provides an intuitive interface for exploring stock data without writing code.

## 📊 API Endpoints

### 1. Get Available Companies
```
GET /api/companies
```
Returns list of available stock symbols.

**Response:**
```json
{
  "status": "success",
  "count": 7,
  "companies": ["TCS", "INFY", "RELIANCE", "HDFCBANK", "ICICIBANK", "WIPRO", "HCLTECH"]
}
```

### 2. Get Stock Data (Last N Days)
```
GET /api/data/{symbol}?days=30
```
Returns historical stock data for the specified symbol.

**Parameters:**
- `symbol`: Company symbol (e.g., TCS, INFY)
- `days`: Number of days (default: 30, max: 365)

**Example:**
```
GET /api/data/TCS?days=30
```

**Response:**
```json
{
  "status": "success",
  "symbol": "TCS",
  "days": 30,
  "data": [
    {
      "date": "2024-01-15",
      "open": 3500.0,
      "high": 3520.0,
      "low": 3480.0,
      "close": 3510.0,
      "volume": 1000000,
      "daily_return": 0.0029,
      "ma_7": 3505.0,
      "volatility_score": 0.15
    }
  ]
}
```

### 3. Get Stock Summary
```
GET /api/summary/{symbol}
```
Returns summary statistics including 52-week high, low, and average close price.

**Example:**
```
GET /api/summary/TCS
```

**Response:**
```json
{
  "status": "success",
  "symbol": "TCS",
  "summary": {
    "high_52w": 3850.0,
    "low_52w": 3200.0,
    "avg_close": 3520.0,
    "current_close": 3510.0,
    "total_records": 252,
    "date_range": {
      "start": "2023-01-01",
      "end": "2024-01-15"
    }
  }
}
```

### 4. Compare Two Stocks
```
GET /api/compare?symbol1=TCS&symbol2=INFY
```
Compares performance metrics between two stocks.

**Parameters:**
- `symbol1`: First stock symbol
- `symbol2`: Second stock symbol

**Response:**
```json
{
  "status": "success",
  "comparison": {
    "symbol1": "TCS",
    "symbol2": "INFY",
    "correlation": 0.75,
    "symbol1_metrics": {
      "total_return_pct": 12.5,
      "avg_daily_return": 0.0005,
      "volatility": 0.015,
      "high_52w": 3850.0,
      "low_52w": 3200.0,
      "avg_close": 3520.0
    },
    "symbol2_metrics": {
      "total_return_pct": 15.2,
      "avg_daily_return": 0.0006,
      "volatility": 0.018,
      "high_52w": 1850.0,
      "low_52w": 1500.0,
      "avg_close": 1650.0
    },
    "insights": {
      "better_performer": "INFY",
      "return_difference": 2.7,
      "correlation_interpretation": "Strong positive"
    }
  }
}
```

## 📈 Calculated Metrics

### 1. Daily Return
```
Daily Return = (Close - Open) / Open
```
Measures the percentage change from opening to closing price.

### 2. 7-Day Moving Average
```
MA_7 = Average of last 7 closing prices
```
Smooths out price fluctuations to identify trends.

### 3. 52-Week High and Low
Tracks the highest and lowest prices over the past year (252 trading days).

### 4. Volatility Score (Creative Metric)
```
Volatility Score = Standard Deviation of Daily Returns (Annualized)
```
Measures price volatility - higher values indicate more price fluctuation.

## 🔍 Data Processing Pipeline

1. **Data Collection**: Fetches stock data from yfinance API
2. **Data Cleaning**:
   - Removes rows with all NaN values
   - Forward fills missing price data
   - Removes invalid data (zero or negative prices)
   - Ensures proper date formatting
3. **Metrics Calculation**:
   - Daily returns
   - Moving averages
   - 52-week statistics
   - Volatility scores
4. **Data Storage**: Stores processed data in SQLite database

## 🧪 Testing the API

### Using cURL

```bash
# Get companies
curl http://localhost:8000/api/companies

# Get TCS data (last 30 days)
curl http://localhost:8000/api/data/TCS?days=30

# Get TCS summary
curl http://localhost:8000/api/summary/TCS

# Compare TCS and INFY
curl "http://localhost:8000/api/compare?symbol1=TCS&symbol2=INFY"
```

### Using Python requests

```python
import requests

base_url = "http://localhost:8000/api"

# Get companies
response = requests.get(f"{base_url}/companies")
print(response.json())

# Get stock data
response = requests.get(f"{base_url}/data/TCS?days=30")
print(response.json())

# Compare stocks
response = requests.get(f"{base_url}/compare?symbol1=TCS&symbol2=INFY")
print(response.json())
```

## 📝 Code Structure Explanation

### Data Collection (`data/collector.py`)
- `StockDataCollector`: Fetches stock data from yfinance
- Supports Indian stocks (NSE format: TCS.NS, INFY.NS)
- Handles errors gracefully

### Data Processing (`data/processor.py`)
- `StockDataProcessor`: Cleans and enriches data
- Calculates all required metrics
- Implements creative volatility score metric

### API Routes (`api/routes.py`)
- RESTful endpoints with proper error handling
- Input validation using FastAPI Query parameters
- JSON responses with consistent structure

### Database Models (`models/database.py`)
- SQLite database with SQLAlchemy ORM
- Indexed for performance
- Stores processed stock data

## 🚀 Deployment Tips

### Production Considerations

1. **Environment Variables**: Use environment variables for sensitive data
2. **Database**: Consider PostgreSQL for production instead of SQLite
3. **Caching**: Implement Redis for frequently accessed data
4. **Rate Limiting**: Add rate limiting to prevent API abuse
5. **Error Logging**: Implement proper logging (e.g., using Loguru)
6. **Testing**: Add unit tests and integration tests
7. **Docker**: Containerize the application for easy deployment

### Docker Deployment (Optional)

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📊 Insights and Analysis

The dashboard provides several analytical insights:

1. **Performance Comparison**: Compare total returns, volatility, and correlation between stocks
2. **Trend Analysis**: Moving averages help identify price trends
3. **Risk Assessment**: Volatility scores indicate price stability
4. **Correlation Analysis**: Understand how stocks move together

## 🐛 Troubleshooting

### Common Issues

1. **No data returned**: Check internet connection and yfinance API availability
2. **Import errors**: Ensure all dependencies are installed (`pip install -r requirements.txt`)
3. **Database errors**: Delete `stock_data.db` and restart the application
4. **Port already in use**: Change port in `main.py` or use `--port` flag with uvicorn

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [yfinance Documentation](https://pypi.org/project/yfinance/)
- [Pandas Documentation](https://pandas.pydata.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)


- Data collection and processing
- REST API development
- Database management
- Financial data analysis


---

**Happy Coding! 🚀**
