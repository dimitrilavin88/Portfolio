# Environment Variables Reference

This document lists all environment variables needed for the Premier League MVP Predictor project.

---

## Required Environment Variables

### 1. Kaggle API Credentials

```env
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
```

**Purpose**: Authenticate with Kaggle API to download the Fantasy Premier League dataset.

**How to get**:
1. Go to https://www.kaggle.com/
2. Sign in to your account
3. Go to Account → API → Create New Token
4. Download the `kaggle.json` file
5. Extract username and key from the JSON file

**Required for**: ETL pipeline (data extraction)

---

### 2. Neon PostgreSQL Database

```env
DATABASE_URL=postgresql://user:password@host.neon.tech/neondb?sslmode=require
```

**Purpose**: Connection string to your Neon PostgreSQL database.

**Format**: 
- `postgresql://[username]:[password]@[host]/[database]?sslmode=require`
- Use the **pooled connection string** from Neon dashboard (recommended for production)

**How to get**:
1. Go to your Neon project dashboard
2. Find "Connection string" or "Connection details"
3. Copy the pooled connection string
4. Replace placeholders with actual values

**Required for**: ETL pipeline (database storage)

---

### 3. Google Sheets Configuration

#### Option A: Using Service Account JSON File (Local Development)

**File**: `service_account_key.json`

Place the service account JSON file in the project root directory.

The ETL script will automatically use this file if `GOOGLE_SERVICE_ACCOUNT_JSON` is not set.

#### Option B: Using Environment Variable (Recommended for Render)

```env
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"...","private_key_id":"...","private_key":"...","client_email":"...","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}
```

**Purpose**: Google Cloud service account credentials for Google Sheets API access.

**How to get**:
1. Create service account in Google Cloud Console
2. Download JSON key file
3. Minify the JSON (remove whitespace)
4. Paste as a single-line string

**Required for**: ETL pipeline (Google Sheets update)

```env
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here
```

**Purpose**: ID of the Google Sheets spreadsheet to update.

**How to get**:
1. Open your Google Sheets spreadsheet
2. Look at the URL: `https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit`
3. Copy the `SPREADSHEET_ID` part

**Required for**: ETL pipeline (Google Sheets update)

---

## Optional Environment Variables

### Port (for FastAPI)

```env
PORT=8000
```

**Purpose**: Port for FastAPI server (used by Render).

**Default**: 8000 (or Render will set it automatically)

**Required for**: FastAPI app deployment

---

## Environment Variable Setup

### Local Development

Create a `.env` file in `src/PremierLeague-PredictiveModel/`:

```env
# Kaggle API
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_key

# Neon Database
DATABASE_URL=postgresql://user:password@host.neon.tech/neondb?sslmode=require

# Google Sheets
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id

# Optional: Use service_account_key.json file instead
# GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
```

**Note**: For local development, you can use the `service_account_key.json` file instead of the environment variable.

### Render Deployment

Set environment variables in Render dashboard:

1. Go to your Render service
2. Navigate to "Environment" tab
3. Add each environment variable
4. For `GOOGLE_SERVICE_ACCOUNT_JSON`:
   - Paste the entire minified JSON as a single-line string
   - Make sure there are no line breaks
   - Escape quotes if needed (Render handles this automatically in UI)

---

## Security Notes

1. **Never commit** `.env` files or `service_account_key.json` to Git
2. Add to `.gitignore`:
   ```
   .env
   service_account_key.json
   *.json
   ```
3. Use environment variables in production (Render)
4. Rotate credentials periodically
5. Use service accounts with minimal required permissions

---

## Testing Environment Variables

### Test Database Connection

```python
import os
import psycopg2

database_url = os.getenv("DATABASE_URL")
conn = psycopg2.connect(database_url)
print("✅ Database connected")
```

### Test Google Sheets Connection

```python
import os
import gspread
from google.oauth2.service_account import Credentials
import json

# From environment variable
service_account_info = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))
creds = Credentials.from_service_account_info(
    service_account_info,
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
gc = gspread.authorize(creds)
print("✅ Google Sheets connected")
```

---

## Checklist

- [ ] KAGGLE_USERNAME set
- [ ] KAGGLE_KEY set
- [ ] DATABASE_URL set (Neon connection string)
- [ ] GOOGLE_SHEETS_SPREADSHEET_ID set
- [ ] GOOGLE_SERVICE_ACCOUNT_JSON set (Render) OR service_account_key.json file exists (local)
- [ ] All credentials tested and working
- [ ] Environment variables set in Render dashboard (for deployment)

