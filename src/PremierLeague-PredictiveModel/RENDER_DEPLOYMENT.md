# Render Deployment Guide
## Premier League MVP Predictor - ETL Pipeline

This guide covers deploying the ETL pipeline to Render and setting up scheduled execution.

---

## Current Setup

Your FastAPI app is already deployed on Render. Now we need to:

1. Add ETL pipeline dependencies to requirements.txt ✅
2. Set up environment variables in Render
3. Optionally create an ETL endpoint in FastAPI
4. Set up scheduled execution (cron job)

---

## Step 1: Update Render Service Configuration

### 1.1 Add Environment Variables

1. Go to your Render dashboard: https://dashboard.render.com/
2. Navigate to your FastAPI service
3. Click on "Environment" tab
4. Add the following environment variables:

```
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
DATABASE_URL=postgresql://user:password@host.neon.tech/neondb?sslmode=require
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"...","private_key_id":"...","private_key":"...","client_email":"...","client_id":"...","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"..."}
```

**Important Notes**:
- For `GOOGLE_SERVICE_ACCOUNT_JSON`, paste the entire JSON as a **single line** (minified)
- You can use Render's UI to add it, or use the Render CLI
- Make sure there are no line breaks in the JSON string

### 1.2 Verify Environment Variables

- All variables should be visible in the Environment tab
- Render will automatically restart your service after adding variables

---

## Step 2: Update Code on Render

### 2.1 Push Code to GitHub

Make sure your code (including `etl_pipeline.py` and `database_schema.sql`) is pushed to GitHub:

```bash
git add .
git commit -m "Add ETL pipeline and database schema"
git push origin main
```

Render will automatically detect the push and redeploy.

### 2.2 Verify Deployment

1. Check Render logs to ensure deployment succeeded
2. Verify all dependencies installed correctly
3. Check for any errors in the logs

---

## Step 3: Set Up Scheduled ETL Execution

Render doesn't support cron jobs in the free tier. Here are your options:

### Option A: Render Cron Jobs (Paid Feature)

If you have a paid Render plan:

1. In Render dashboard, go to "Cron Jobs"
2. Click "New Cron Job"
3. Configure:
   - **Name**: "Premier League ETL"
   - **Schedule**: `0 2 * * *` (runs daily at 2 AM UTC)
   - **Command**: `cd src/PremierLeague-PredictiveModel && python etl_pipeline.py`
   - **Environment**: Same as your FastAPI service

### Option B: External Cron Service (Free - Recommended)

Use a free external cron service:

#### Using cron-job.org

1. Go to https://cron-job.org/
2. Sign up (free)
3. Create a new cron job
4. You'll need to create an API endpoint in your FastAPI app (see Option C)

#### Using GitHub Actions (If code is on GitHub)

Create `.github/workflows/etl.yml`:

```yaml
name: ETL Pipeline

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:  # Allow manual trigger

jobs:
  etl:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          cd src/PremierLeague-PredictiveModel
          pip install -r requirements.txt
      - name: Run ETL Pipeline
        env:
          KAGGLE_USERNAME: ${{ secrets.KAGGLE_USERNAME }}
          KAGGLE_KEY: ${{ secrets.KAGGLE_KEY }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          GOOGLE_SHEETS_SPREADSHEET_ID: ${{ secrets.GOOGLE_SHEETS_SPREADSHEET_ID }}
          GOOGLE_SERVICE_ACCOUNT_JSON: ${{ secrets.GOOGLE_SERVICE_ACCOUNT_JSON }}
        run: |
          cd src/PremierLeague-PredictiveModel
          python etl_pipeline.py
```

Add secrets in GitHub repository settings.

### Option C: Create ETL API Endpoint (Recommended for External Cron)

Add an ETL endpoint to your FastAPI app that external services can call:

**Add to `premierleague_MLModel.py`**:

```python
from etl_pipeline import ETLPipeline

@app.post("/api/run-etl")
async def run_etl():
    """
    Run ETL pipeline via API endpoint.
    Can be called by external cron services.
    """
    try:
        pipeline = ETLPipeline()
        pipeline.run()
        return {
            "status": "success",
            "message": "ETL pipeline completed successfully",
            "rows_processed": pipeline.rows_inserted
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
```

Then set up external cron to call:
- `https://your-app.onrender.com/api/run-etl`

**Security Note**: Add authentication to this endpoint to prevent unauthorized access:

```python
API_KEY = os.getenv("ETL_API_KEY", "")

@app.post("/api/run-etl")
async def run_etl(api_key: str = Header(None)):
    if api_key != API_KEY:
        return {"status": "error", "message": "Unauthorized"}, 401
    # ... rest of the code
```

### Option D: Manual Execution (For Testing)

1. Use Render Shell (if available)
2. Or SSH into Render instance
3. Run: `python src/PremierLeague-PredictiveModel/etl_pipeline.py`

---

## Step 4: Monitor ETL Pipeline

### 4.1 Check Render Logs

1. Go to Render dashboard
2. Click on your service
3. View "Logs" tab
4. Look for ETL pipeline output

### 4.2 Verify Data Updates

1. **Neon Database**:
   - Go to Neon SQL Editor
   - Run: `SELECT COUNT(*) FROM players;`
   - Check `data_updates` table for recent runs

2. **Google Sheets**:
   - Open your spreadsheet
   - Verify data has been updated
   - Check last update timestamp

3. **Looker Studio**:
   - Refresh your data source
   - Verify charts show updated data

---

## Recommended Setup

For a free solution, I recommend:

1. **Option C** (ETL API Endpoint) + **Option B** (External Cron)
   - Add ETL endpoint to FastAPI
   - Use cron-job.org to call the endpoint
   - Set up authentication for security

2. **GitHub Actions** (If code is on GitHub)
   - Use GitHub Actions workflow
   - Run ETL pipeline directly
   - No need for API endpoint

---

## Troubleshooting

### ETL Pipeline Fails on Render

**Check logs**:
- Database connection issues
- Google Sheets API errors
- Missing environment variables
- Kaggle API authentication

**Common fixes**:
- Verify all environment variables are set
- Check DATABASE_URL format (use pooled connection)
- Verify Google service account JSON is minified correctly
- Test locally first

### Scheduled Job Not Running

- Verify cron job is configured correctly
- Check external service (cron-job.org) logs
- Verify endpoint URL is correct
- Check authentication if using API endpoint

### Data Not Updating

- Check ETL pipeline logs
- Verify database connection
- Check Google Sheets permissions
- Verify spreadsheet ID is correct

---

## Next Steps

1. ✅ Set environment variables in Render
2. ✅ Deploy updated code
3. ✅ Set up scheduled execution (choose one option)
4. ✅ Monitor first ETL run
5. ✅ Verify data in database and Google Sheets
6. ✅ Connect Looker Studio
7. ✅ Build dashboards

---

## Security Best Practices

1. **Never commit** credentials to Git
2. Use environment variables for all secrets
3. Add authentication to ETL endpoint (if using Option C)
4. Use service accounts with minimal permissions
5. Rotate credentials periodically
6. Monitor logs for suspicious activity

---

Good luck with your deployment! 🚀

