# Premier League MVP Predictor - Setup Guide
## Database & Looker Studio Integration

This guide will walk you through setting up:
1. Neon PostgreSQL Database
2. Google Sheets API (for Looker Studio)
3. ETL Pipeline
4. Render Deployment Configuration

---

## Step 1: Set Up Neon PostgreSQL Database

### 1.1 Create Neon Account and Project

1. Go to https://neon.tech/
2. Sign up for a free account (GitHub, Google, or Email)
3. Click "New Project"
4. Fill in project details:
   - **Project name**: `premier-league-mvp` (or your choice)
   - **Database name**: `neondb` (default is fine)
   - **PostgreSQL version**: 15 or 16 (default)
   - **Region**: Choose closest to you
5. Click "Create Project"
6. Wait for project creation (~10-30 seconds)

### 1.2 Get Connection String

1. Once the project is created, you'll see the dashboard
2. Look for "Connection string" or "Connection details"
3. **IMPORTANT**: Copy the **pooled connection string** (recommended for production)
   - It looks like: `postgresql://neondb_owner:npg_B2piM4qkWmQb@ep-delicate-dust-af3f1hic-pooler.c-2.us-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require`
4. **SAVE THE PASSWORD** - you won't be able to see it again!
   - If you lose it, you can reset it in project settings

### 1.3 Create Database Schema

1. In Neon dashboard, click "SQL Editor" (left sidebar)
2. Open the `database_schema.sql` file from this project
3. Copy and paste the SQL code into the SQL Editor
4. Click "Run" to execute the schema creation
5. Verify tables were created:
   - You should see: `players`, `player_history`, `predictions`, `data_updates`

**Alternative**: You can also use a SQL client like DBeaver or pgAdmin to connect and run the schema.

---

## Step 2: Set Up Google Sheets API

### 2.1 Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Sign in with your Google account
3. Click the project dropdown at the top
4. Click "New Project"
5. Enter project name: `premier-league-mvp` (or your choice)
6. Click "Create"
7. Wait for project creation

### 2.2 Enable Google Sheets API

1. In Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Google Sheets API"
3. Click on "Google Sheets API"
4. Click "Enable"

### 2.3 Create Service Account

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Fill in:
   - **Service account name**: `premier-league-etl` (or your choice)
   - **Service account ID**: Auto-generated (can customize)
   - **Description**: "ETL service account for Premier League data"
4. Click "Create and Continue"
5. Skip "Grant this service account access to project" (optional)
6. Click "Done"

### 2.4 Create Service Account Key

1. In the "Credentials" page, find your service account
2. Click on the service account email
3. Go to the "Keys" tab
4. Click "Add Key" → "Create new key"
5. Choose "JSON" format
6. Click "Create"
7. **DOWNLOAD THE JSON FILE** - you'll need this!
8. Save it as `service_account_key.json` (for local development)

### 2.5 Create Google Sheets Spreadsheet

1. Go to https://sheets.google.com/
2. Create a new spreadsheet
3. Name it: "Premier League Players Data" (or your choice)
4. **IMPORTANT**: Note the Spreadsheet ID from the URL
   - URL format: `https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit`
   - Copy the `SPREADSHEET_ID` part
5. Share the spreadsheet with your service account:
   - Click "Share" button
   - Enter the service account email (found in the JSON file: `client_email`)
   - Give it "Editor" access
   - Click "Send"

---

## Step 3: Configure Environment Variables

### 3.1 Local Development (.env file)

Create a `.env` file in the `src/PremierLeague-PredictiveModel/` directory:

```env
# Kaggle API Credentials
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key

# Neon PostgreSQL Database
DATABASE_URL=postgresql://user:password@host.neon.tech/neondb?sslmode=require

# Google Sheets Configuration
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here
```

**For Google Service Account (Local Development)**:
- Use the `service_account_key.json` file (place it in the project directory)
- The ETL script will automatically use it if `GOOGLE_SERVICE_ACCOUNT_JSON` is not set

**For Render Deployment**:
- You'll need to convert the JSON file to a string (see Step 4)

### 3.2 Environment Variables for Render

You'll need to set these in Render dashboard (see Step 4).

---

## Step 4: Deploy to Render

### 4.1 Prepare for Render Deployment

#### Option A: Using Service Account JSON File (Not Recommended for Render)
- Render doesn't easily handle file uploads
- Better to use environment variable method

#### Option B: Using Environment Variable (Recommended)

1. **Convert JSON to String**:
   - Open your `service_account_key.json` file
   - Copy the entire JSON content
   - Go to https://jsonformatter.org/json-minify (or similar)
   - Minify the JSON (remove all whitespace)
   - Copy the minified JSON string

2. **Set Environment Variables in Render**:
   - Go to your Render dashboard
   - Navigate to your service
   - Go to "Environment" tab
   - Add the following environment variables:

```
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
DATABASE_URL=postgresql://user:password@host.neon.tech/neondb?sslmode=require
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"...","private_key_id":"...","private_key":"...","client_email":"...","client_id":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","client_x509_cert_url":"..."}
```

**Note**: For `GOOGLE_SERVICE_ACCOUNT_JSON`, paste the entire minified JSON as a single-line string.

### 4.2 Set Up Scheduled ETL Job on Render

Render doesn't support cron jobs directly in the free tier, but you have options:

#### Option A: Render Cron Jobs (Paid Feature)
- Upgrade to paid plan
- Set up a cron job to run `python etl_pipeline.py` on schedule

#### Option B: External Cron Service (Free)
- Use a free service like:
  - **cron-job.org** (https://cron-job.org/)
  - **EasyCron** (https://www.easycron.com/)
  - **GitHub Actions** (if your code is on GitHub)

**Recommended: cron-job.org Setup**:

1. Go to https://cron-job.org/
2. Sign up (free)
3. Create a new cron job:
   - **Name**: "Premier League ETL"
   - **URL**: `https://your-render-app.onrender.com/api/run-etl` (if you create an endpoint)
   - **Schedule**: Choose frequency (e.g., daily at 2 AM)
   - **Save**

**Or: Create ETL Endpoint in FastAPI**:

Add this to your FastAPI app (optional):

```python
@app.post("/api/run-etl")
async def run_etl():
    """Run ETL pipeline via API endpoint"""
    from etl_pipeline import main as run_etl
    try:
        run_etl()
        return {"status": "success", "message": "ETL pipeline completed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

Then set up cron job to hit this endpoint.

#### Option C: Manual Run (For Testing)
- SSH into Render instance
- Run `python etl_pipeline.py` manually

---

## Step 5: Test the ETL Pipeline

### 5.1 Test Locally

1. Make sure you have:
   - `.env` file configured
   - `service_account_key.json` file in project directory
   - Database schema created in Neon

2. Run the ETL pipeline:
   ```bash
   cd src/PremierLeague-PredictiveModel
   python etl_pipeline.py
   ```

3. Check results:
   - Verify data in Neon database (use SQL Editor)
   - Verify data in Google Sheets
   - Check for any errors

### 5.2 Test on Render

1. Set up environment variables in Render
2. Deploy your code
3. Run ETL pipeline (via endpoint or manually)
4. Verify data updates

---

## Step 6: Connect Looker Studio

### 6.1 Create Looker Studio Dashboard

1. Go to https://lookerstudio.google.com/
2. Sign in with your Google account
3. Click "Create" → "Data Source"
4. Search for "Google Sheets"
5. Click "Google Sheets"
6. Click "Select" → Choose your spreadsheet
7. Click "Connect"

### 6.2 Configure Data Source

1. Review the fields (columns) from your spreadsheet
2. Adjust data types if needed:
   - Right-click field → Change type
   - Set numeric fields as "Number"
   - Set text fields as "Text"
3. Click "Create Report"

### 6.3 Build Dashboard

1. Add charts and visualizations:
   - Bar charts, line charts, tables, etc.
   - Drag and drop fields
2. Customize the design
3. Add filters and interactive elements

### 6.4 Configure Automatic Refresh

1. In Looker Studio, go to your data source
2. Click the three dots (⋮) → "Manage added data sources"
3. Click on your data source
4. Configure refresh schedule:
   - Google Sheets: Can refresh every 15 minutes (free tier)
   - Set refresh frequency as needed

### 6.5 Embed Dashboard on Your Website

1. In Looker Studio, open your report
2. Click "Share" (top right)
3. Set sharing to "Anyone with the link can view"
4. Click "Embed report"
5. Copy the iframe code
6. Add to your HTML:

```html
<iframe 
  src="https://lookerstudio.google.com/embed/reporting/YOUR_REPORT_ID/page/YOUR_PAGE_ID"
  width="100%" 
  height="600" 
  frameborder="0" 
  style="border: 0;">
</iframe>
```

---

## Troubleshooting

### Database Connection Issues

- **Error**: "Connection refused"
  - Check your DATABASE_URL is correct
  - Verify Neon project is active (not paused)
  - Check firewall settings

- **Error**: "Authentication failed"
  - Verify username and password are correct
  - Check if password needs to be URL-encoded

### Google Sheets Issues

- **Error**: "Permission denied"
  - Make sure you shared the spreadsheet with service account email
  - Verify service account has "Editor" access

- **Error**: "Spreadsheet not found"
  - Verify GOOGLE_SHEETS_SPREADSHEET_ID is correct
  - Check spreadsheet ID in the URL

### ETL Pipeline Issues

- **Error**: "Kaggle API authentication failed"
  - Verify KAGGLE_USERNAME and KAGGLE_KEY are set
  - Check Kaggle API credentials are valid

- **Error**: "Module not found"
  - Install dependencies: `pip install -r requirements.txt`

---

## Next Steps

1. ✅ Set up Neon database
2. ✅ Set up Google Sheets API
3. ✅ Configure environment variables
4. ✅ Deploy to Render
5. ✅ Set up scheduled ETL job
6. ✅ Connect Looker Studio
7. ✅ Build dashboards
8. ✅ Embed on your website

---

## Support

If you encounter issues:
1. Check error messages in console/logs
2. Verify all environment variables are set correctly
3. Test each component separately (database, Google Sheets, ETL)
4. Check Render logs for deployment issues

Good luck with your project! 🚀

