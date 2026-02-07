# Deployment Guide for GitHub Pages

## Problem: Why GitHub Pages Shows README Instead of Dashboard

GitHub Pages **only serves static files** (HTML, CSS, JavaScript). It cannot run Python backend applications like FastAPI.

Your project has two parts:
1. **Frontend (Dashboard)**: `templates/dashboard.html` - Can be served by GitHub Pages ✅
2. **Backend (FastAPI API)**: `main.py`, `api/routes.py`, etc. - Cannot run on GitHub Pages ❌

## Solution: Deploy Backend Separately

You need to deploy the FastAPI backend on a platform that supports Python applications, then connect your GitHub Pages frontend to it.

## Step-by-Step Deployment

### Option 1: Deploy Backend on Railway (Recommended - Free Tier Available)

1. **Sign up at [Railway.app](https://railway.app)**

2. **Create a new project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your repository

3. **Configure the service**:
   - Railway will auto-detect Python
   - Add environment variables if needed
   - Set the start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Get your backend URL**:
   - Railway will provide a URL like: `https://your-app.railway.app`
   - Your API will be at: `https://your-app.railway.app/api`

5. **Update dashboard.html** (only if the dashboard is hosted on a different domain, e.g. GitHub Pages):
   - Open `templates/dashboard.html`
   - In `<head>`, add: `<meta name="api-base" content="https://your-app.railway.app/api">`
   - Replace with your actual Railway URL (no trailing slash after `/api`)

6. **Commit and push**:
   ```bash
   git add templates/dashboard.html
   git commit -m "Update API URL for deployed backend"
   git push
   ```

### Option 2: Deploy Backend on Render (Free Tier Available)

1. **Sign up at [Render.com](https://render.com)**

2. **Create a new Web Service**:
   - Connect your GitHub repository
   - Select your repository
   - Choose "Python 3" environment

3. **Configure**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3

4. **Get your backend URL**:
   - Render provides: `https://your-app.onrender.com`
   - Your API: `https://your-app.onrender.com/api`

5. **Update dashboard.html** (same as Railway step 5: add `<meta name="api-base" content="https://your-app.onrender.com/api">` in `<head>` when dashboard is on a different host)

### Option 3: Deploy Backend on Heroku

1. **Install Heroku CLI** and login

2. **Create `Procfile`** in project root:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

3. **Deploy**:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

4. **Get URL**: `https://your-app-name.herokuapp.com/api`

## Setting Up GitHub Pages

1. **Go to your repository settings** on GitHub

2. **Navigate to Pages** section

3. **Source**: Select your branch (usually `main` or `master`)

4. **Root**: Select `/ (root)` or `/docs` if you use docs folder

5. **Save** - GitHub will provide your Pages URL

## File Structure for GitHub Pages

Your repository should have:
```
Mini-financial-data-Platform/
├── index.html              # Redirects to dashboard
├── templates/
│   └── dashboard.html      # Main dashboard (updated with backend URL)
├── README.md
└── ... (other files)
```

## Testing

1. **Test backend**: Visit `https://your-backend-url.railway.app/health`
   - Should return: `{"status": "healthy", ...}`

2. **Test API**: Visit `https://your-backend-url.railway.app/api/companies`
   - Should return list of companies

3. **Test dashboard**: Visit `https://bipul78700.github.io/Mini-financial-data-Platform/`
   - Should load dashboard and connect to backend

## Important Notes

### CORS Configuration

Make sure your backend allows requests from GitHub Pages. In `main.py`, you already have:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows all origins
    ...
)
```

For production, you might want to restrict this:
```python
allow_origins=[
    "https://bipul78700.github.io",
    "http://localhost:8000"
]
```

### Environment Variables

If you need environment variables (API keys, etc.), set them in your deployment platform:
- **Railway**: Project → Variables tab
- **Render**: Environment → Environment Variables
- **Heroku**: `heroku config:set KEY=value`

## Troubleshooting

### "Backend not accessible. Status: 404" when opening /dashboard (API works in Swagger)

**Cause:** The dashboard page is often served by a **different server** than your API (e.g. a static site on the same domain). So `/docs` and `/api/companies` hit your FastAPI app, but when you open `/dashboard`, that request may be served by a static host that doesn’t have `/api` routes, so the dashboard’s `fetch('/api/...')` gets a 404.

**Fix:**

1. **If dashboard and API are the same Render Web Service (only FastAPI, no static site)**  
   The dashboard now uses `window.location.origin + '/api'`, so it should work. Redeploy and hard-refresh the page (Ctrl+F5). If it still 404s, use (2).

2. **If the dashboard is on a different host (e.g. static site or GitHub Pages)**  
   Point the dashboard at your API with a meta tag. In `templates/dashboard.html`, inside `<head>`, add:
   ```html
   <meta name="api-base" content="https://YOUR-APP.onrender.com/api">
   ```
   Replace `YOUR-APP` with your Render service URL (no trailing slash after `api`). Save, redeploy the frontend, and reload the dashboard.

3. **Ensure only one thing serves the site**  
   On Render, avoid having both a Static Site and a Web Service on the same URL if they overlap. Prefer serving the dashboard from the FastAPI app at `/dashboard` so all requests go to the same backend.

### "404" or "Error loading data" at /api/data/SYMBOL (e.g. /api/data/INFY)

**Cause:** The backend is reached, but the **data source** (yfinance) returns no data. On Render free tier this can happen (e.g. NSE blocked, timeout, or cold start). The app now returns **503** with a clear message instead of 404, and the dashboard shows that message.

**Fixes:**

1. **Check the new error message**  
   After redeploying, the dashboard will show the API’s `detail` (e.g. "Stock data temporarily unavailable..."). Use that to confirm it’s a data issue, not a missing route.

2. **CORS on Render**  
   If your dashboard is on the same Render Web Service, CORS is not required. If the frontend is on another origin (e.g. another Render URL or GitHub Pages), set the env var on the **backend** service:
   - `ALLOWED_ORIGINS` = `https://your-dashboard-url.com,https://your-app.onrender.com`  
   (comma-separated, no spaces after commas.)

3. **Retry**  
   Free-tier instances can sleep; the first request may fail. Click "Load Data" again after a few seconds.

4. **Logs**  
   In Render → your service → Logs, look for "No data found for symbol" or "NSE blocked" to confirm yfinance issues.

### Dashboard shows errors
- Check browser console (F12) for CORS errors
- Verify backend URL is correct in `dashboard.html` or via `<meta name="api-base" content="...">`
- Test backend API directly in browser

### Backend not responding
- Check deployment logs on your platform
- Verify `requirements.txt` has all dependencies
- Check if port is configured correctly

### GitHub Pages not updating
- Wait a few minutes for GitHub to rebuild
- Clear browser cache
- Check GitHub Actions/Pages build status

## Quick Checklist

- [ ] Backend deployed on Railway/Render/Heroku
- [ ] Backend URL obtained and tested
- [ ] `templates/dashboard.html` updated with backend URL
- [ ] Changes committed and pushed to GitHub
- [ ] GitHub Pages enabled and configured
- [ ] Dashboard loads and connects to backend successfully

## Alternative: Static Demo Version

If you don't want to deploy a backend, you could create a static demo version with mock data, but it won't have real-time data functionality.

---

**Need help?** Check the deployment platform's documentation or open an issue in your repository.
