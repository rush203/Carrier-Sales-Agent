# 🚀 Fly.io Deployment Instructions

This document provides step-by-step instructions to deploy the ACME Logistics API to Fly.io.

## 📋 Prerequisites

### 1. Required Accounts
- **Fly.io Account**: Sign up at [fly.io](https://fly.io)
- **Google Cloud Account**: For Google Sheets API credentials
- **GitHub Account**: (Optional, for version control)

### 2. Required Software
- **Fly CLI**: Install from [fly.io/docs/hands-on/install-flyctl](https://fly.io/docs/hands-on/install-flyctl)
- **Python 3.11+**: [python.org](https://python.org)
- **Git**: [git-scm.com](https://git-scm.com)

### 3. Required Files
Ensure you have all these files in your project directory:
```
acme-logistics/
├── main.py                    # Main FastAPI application
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── fly.toml                   # Fly.io configuration
├── .dockerignore             # Docker ignore file
├── google-credentials.json   # Google Sheets API credentials
└── FLY_DEPLOYMENT_INSTRUCTIONS.md
```

## 🔧 Setup Instructions

### Step 1: Install Fly CLI

**Windows (PowerShell):**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

**macOS/Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

### Step 2: Login to Fly.io
```bash
fly auth login
```

### Step 3: Google Sheets API Setup

1. **Go to Google Cloud Console**: [console.cloud.google.com](https://console.cloud.google.com)
2. **Create a new project** or select existing one
3. **Enable Google Sheets API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"
4. **Create Service Account**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in details and create
5. **Generate JSON Key**:
   - Click on the service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Choose JSON format
   - Download the file
6. **Rename and Place**:
   - Rename downloaded file to `google-credentials.json`
   - Place it in your project root directory

### Step 4: Share Google Sheet
1. **Create or use existing Google Sheet**
2. **Share with service account email** (found in credentials JSON)
3. **Give Editor permissions**
4. **Copy the Spreadsheet ID** from the URL

### Step 5: Update Configuration

**Update `main.py` with your Google Sheet details:**
```python
# Google Sheets Configuration
GOOGLE_SHEETS_URL = "https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID/edit?usp=sharing"
SPREADSHEET_ID = "YOUR_SPREADSHEET_ID"
GOOGLE_CREDENTIALS_FILE = "google-credentials.json"
```

## 🚀 Deployment Steps

### Step 1: Initialize Fly App (First Time Only)
```bash
fly launch
```
- Choose app name (e.g., `acme-logistics`)
- Choose region (e.g., `iad` for Virginia)
- Don't deploy yet when asked

### Step 2: Verify Configuration Files

**Check `fly.toml`:**
```toml
app = "acme-logistics"
primary_region = "iad"

[build]

[env]
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
  processes = ["app"]

[[http_service.checks]]
  grace_period = "10s"
  interval = "30s"
  method = "GET"
  timeout = "5s"
  path = "/health"
```

**Check `Dockerfile`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Check `requirements.txt`:**
```
fastapi
uvicorn
pandas
matplotlib
seaborn
gspread
google-auth
google-auth-oauthlib
google-auth-httplib2
python-dotenv
pydantic
```

### Step 3: Deploy to Fly.io
```bash
fly deploy
```

### Step 4: Verify Deployment
```bash
fly status
fly logs
```

## 🧪 Testing the Deployment

### 1. Health Check
```bash
curl https://acme-logistics.fly.dev/health
```

### 2. Test Search Endpoint
```bash
curl -X GET "https://acme-logistics.fly.dev/search?origin=chicago&destination=dallas" \
  -H "X-API-Key: supersecretapikey123"
```

### 3. Test Webhook Endpoint
```bash
curl -X POST "https://acme-logistics.fly.dev/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_intent": "yes",
    "counter_offer": "2000",
    "agreed_rate": "2100",
    "negotiation_attempts": "2",
    "sentiment": "positive",
    "call_outcome": "booked"
  }'
```

### 4. Test Dashboard
```bash
curl -X GET "https://acme-logistics.fly.dev/dashboard" \
  -H "X-API-Key: supersecretapikey123"
```

## 📊 Available Endpoints

| Endpoint | Method | Authentication | Description |
|----------|--------|----------------|-------------|
| `/health` | GET | None | Health check |
| `/search` | GET | API Key Required | Search loads by origin/destination |
| `/webhook` | POST | None | Receive HappyRobot data |
| `/dashboard` | GET | API Key Required | View webhook data |
| `/files` | GET | API Key Required | File information |
| `/generate-charts` | GET | API Key Required | Generate analytics charts |

## 🔑 API Authentication

**API Key**: `supersecretapikey123`

**Usage**: Include in headers as `X-API-Key: supersecretapikey123`

## 📁 File Structure After Deployment

```
acme-logistics/
├── main.py                    # FastAPI application
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── fly.toml                   # Fly.io configuration
├── .dockerignore             # Docker ignore file
├── google-credentials.json   # Google Sheets API credentials
├── webhook_data.csv          # Generated CSV file
├── charts/                   # Generated charts directory
└── FLY_DEPLOYMENT_INSTRUCTIONS.md
```

## 🔄 Update Deployment

To update the application:

1. **Make changes to your code**
2. **Deploy updates**:
   ```bash
   fly deploy
   ```
3. **Check status**:
   ```bash
   fly status
   ```

## 🐛 Troubleshooting

### Common Issues

**1. Port Configuration Error**
```
WARNING The app is not listening on the expected address
```
- Ensure `Dockerfile` exposes port 8080
- Ensure `main.py` runs on port 8080
- Check `fly.toml` internal_port setting

**2. Google Sheets Authentication Error**
```
Google credentials file not found
```
- Verify `google-credentials.json` exists in project root
- Check file permissions
- Ensure service account has proper access

**3. Build Failures**
```bash
fly logs
```
- Check for missing dependencies in `requirements.txt`
- Verify Python version compatibility

**4. Runtime Errors**
```bash
fly logs
```
- Check application logs for specific errors
- Verify environment variables and configurations

### Useful Commands

```bash
# View logs
fly logs

# Check app status
fly status

# Scale app
fly scale count 1

# Restart app
fly apps restart

# Destroy app (if needed)
fly apps destroy acme-logistics
```

## 📞 Support

- **Fly.io Documentation**: [fly.io/docs](https://fly.io/docs)
- **FastAPI Documentation**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **Google Sheets API**: [developers.google.com/sheets](https://developers.google.com/sheets)

## 🎯 Success Criteria

Your deployment is successful when:

✅ **Health check returns 200**  
✅ **Search endpoint returns load data**  
✅ **Webhook endpoint stores data**  
✅ **Google Sheets integration works**  
✅ **Charts are generated**  
✅ **All endpoints respond correctly**  

## 🔒 Security Notes

- **API Key**: Change the default API key in production
- **Google Credentials**: Keep `google-credentials.json` secure
- **Environment Variables**: Use Fly.io secrets for sensitive data
- **CORS**: Configure CORS properly for production

## 📈 Monitoring

Monitor your deployment with:

```bash
# View real-time logs
fly logs --follow

# Check app metrics
fly status

# Monitor resource usage
fly dashboard
```

---

**Deployment URL**: `https://acme-logistics.fly.dev/`  
**Last Updated**: August 3, 2025  
**Version**: 1.0.0 