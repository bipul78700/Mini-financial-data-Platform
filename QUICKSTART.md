# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python run.py
```

### Step 3: Access the Dashboard
Open your browser and navigate to:
- **Dashboard**: http://localhost:8000/dashboard
- **API Docs**: http://localhost:8000/docs

## 📝 Quick Test

### Test API Endpoints

1. **Get Available Companies**
   ```bash
   curl http://localhost:8000/api/companies
   ```

2. **Get Stock Data (TCS, last 30 days)**
   ```bash
   curl http://localhost:8000/api/data/TCS?days=30
   ```

3. **Get Summary Statistics**
   ```bash
   curl http://localhost:8000/api/summary/TCS
   ```

4. **Compare Two Stocks**
   ```bash
   curl "http://localhost:8000/api/compare?symbol1=TCS&symbol2=INFY"
   ```

## 🎯 Using the Dashboard

1. Select a stock from the dropdown (e.g., TCS, INFY, RELIANCE)
2. Choose number of days (default: 30)
3. Click "Load Data" to see visualizations
4. Click "Load Summary" to see statistics
5. Use "Compare" to compare two stocks side-by-side

## 💡 Tips

- The first API call may take a few seconds as it fetches data from yfinance
- Data is cached in SQLite database for faster subsequent requests
- All Indian stocks use NSE format (e.g., TCS.NS, INFY.NS)

## 🐛 Troubleshooting

**Issue**: "No data available"
- **Solution**: Check your internet connection. yfinance requires internet access.

**Issue**: Port 8000 already in use
- **Solution**: Change the port in `run.py` or use: `uvicorn main:app --port 8001`

**Issue**: Import errors
- **Solution**: Make sure all dependencies are installed: `pip install -r requirements.txt`

---

For detailed documentation, see [README.md](README.md)
