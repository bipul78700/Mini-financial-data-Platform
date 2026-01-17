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

5. **Update dashboard.html**:
   - Open `templates/dashboard.html`
   - Find line 288: `return 'https://your-backend-url.here/api';`
   - Replace with: `return 'https://your-app.railway.app/api';`

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

5. **Update dashboard.html** (same as Railway step 5)

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

### Dashboard shows errors
- Check browser console (F12) for CORS errors
- Verify backend URL is correct in `dashboard.html`
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
