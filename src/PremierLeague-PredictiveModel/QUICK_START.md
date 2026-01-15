# Quick Start Guide
## Premier League MVP Predictor - Looker Studio Integration

This guide provides a quick overview of what has been set up and the next steps.

---

## ✅ What Has Been Created

1. **Database Schema** (`database_schema.sql`)
   - SQL schema for Neon PostgreSQL database
   - Tables: `players`, `player_history`, `predictions`, `data_updates`

2. **ETL Pipeline** (`etl_pipeline.py`)
   - Extracts data from Kaggle
   - Transforms and cleans data
   - Loads to Neon PostgreSQL database
   - Also loads to Google Sheets (for Looker Studio)

3. **Updated Dependencies** (`requirements.txt`)
   - Added: `psycopg2-binary`, `gspread`, `google-auth`, etc.

4. **Documentation**
   - `SETUP_GUIDE.md` - Complete setup instructions
   - `ENVIRONMENT_VARIABLES.md` - Environment variables reference
   - `RENDER_DEPLOYMENT.md` - Render deployment guide
   - `QUICK_START.md` - This file

---

## 📋 Next Steps Checklist

### Step 1: Set Up Neon Database ⏳
- [ ] Create Neon account and project
- [ ] Get connection string (pooled version)
- [ ] Run `database_schema.sql` to create tables
- [ ] Save connection string for environment variable

### Step 2: Set Up Google Sheets API ⏳
- [ ] Create Google Cloud project
- [ ] Enable Google Sheets API
- [ ] Create service account
- [ ] Download service account JSON key
- [ ] Create Google Sheets spreadsheet
- [ ] Share spreadsheet with service account email
- [ ] Save spreadsheet ID

### Step 3: Configure Environment Variables ⏳
- [ ] Set up `.env` file for local development (optional)
- [ ] Set environment variables in Render dashboard:
  - [ ] `KAGGLE_USERNAME`
  - [ ] `KAGGLE_KEY`
  - [ ] `DATABASE_URL` (Neon connection string)
  - [ ] `GOOGLE_SHEETS_SPREADSHEET_ID`
  - [ ] `GOOGLE_SERVICE_ACCOUNT_JSON` (minified JSON string)

### Step 4: Test ETL Pipeline Locally ⏳
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Run ETL pipeline: `python etl_pipeline.py`
- [ ] Verify data in Neon database
- [ ] Verify data in Google Sheets

### Step 5: Deploy to Render ⏳
- [ ] Push code to GitHub (if using Git)
- [ ] Set environment variables in Render
- [ ] Verify deployment
- [ ] Test ETL pipeline on Render

### Step 6: Set Up Scheduled Execution ⏳
- [ ] Choose scheduling option:
  - [ ] Option A: Render Cron Jobs (paid)
  - [ ] Option B: External cron service (free, e.g., cron-job.org)
  - [ ] Option C: GitHub Actions (if code is on GitHub)
- [ ] Configure schedule (e.g., daily at 2 AM)
- [ ] Test scheduled execution

### Step 7: Connect Looker Studio ⏳
- [ ] Go to https://lookerstudio.google.com/
- [ ] Create new data source → Google Sheets
- [ ] Select your spreadsheet
- [ ] Build dashboard with visualizations
- [ ] Configure automatic refresh (every 15 minutes)
- [ ] Get embed code
- [ ] Add to your website

### Step 8: Embed on Website ⏳
- [ ] Get embed code from Looker Studio
- [ ] Add iframe to your HTML page
- [ ] Test embedded dashboard
- [ ] Verify updates work

---

## 🚀 Quick Commands

### Local Development

```bash
# Navigate to project directory
cd src/PremierLeague-PredictiveModel

# Install dependencies
pip install -r requirements.txt

# Run ETL pipeline
python etl_pipeline.py

# Test database connection
# (Use Neon SQL Editor or SQL client)
```

### Render Deployment

1. **Set Environment Variables**:
   - Go to Render dashboard
   - Navigate to your service
   - Environment tab → Add variables

2. **Deploy**:
   - Push code to GitHub (auto-deploys)
   - Or manually deploy via Render dashboard

3. **Run ETL Pipeline**:
   - Option A: Create API endpoint (see RENDER_DEPLOYMENT.md)
   - Option B: Use external cron service
   - Option C: Use GitHub Actions

---

## 📚 Documentation Reference

- **Complete Setup**: See `SETUP_GUIDE.md`
- **Environment Variables**: See `ENVIRONMENT_VARIABLES.md`
- **Render Deployment**: See `RENDER_DEPLOYMENT.md`

---

## ⚠️ Important Notes

1. **Google Sheets JSON Key**:
   - For local: Use `service_account_key.json` file
   - For Render: Convert JSON to minified string and set as `GOOGLE_SERVICE_ACCOUNT_JSON`

2. **Database Connection**:
   - Use **pooled connection string** from Neon (recommended for production)
   - Save password securely (you won't see it again!)

3. **Scheduled Execution**:
   - Render free tier doesn't support cron jobs
   - Use external cron service (free) or GitHub Actions

4. **Looker Studio Refresh**:
   - Free tier refreshes every 15 minutes
   - Dashboard will automatically update after refresh

---

## 🆘 Troubleshooting

### ETL Pipeline Fails

**Check**:
- All environment variables are set
- Database connection string is correct
- Google Sheets service account has access
- Kaggle API credentials are valid

**Common Errors**:
- "Connection refused" → Check DATABASE_URL
- "Permission denied" → Check Google Sheets sharing
- "Authentication failed" → Check credentials

### Data Not Updating

**Check**:
- ETL pipeline ran successfully (check logs)
- Looker Studio refresh is configured
- Data source is connected correctly
- Wait for refresh interval (15 minutes for free tier)

---

## ✅ Success Criteria

You'll know everything is working when:

1. ✅ ETL pipeline runs without errors
2. ✅ Data appears in Neon database
3. ✅ Data appears in Google Sheets
4. ✅ Looker Studio dashboard shows data
5. ✅ Dashboard updates automatically
6. ✅ Embedded dashboard works on your website

---

## 🎯 Next Actions

1. **Start with Step 1**: Set up Neon database
2. **Then Step 2**: Set up Google Sheets API
3. **Then Step 3**: Configure environment variables
4. **Test locally** before deploying to Render
5. **Deploy and schedule** ETL pipeline
6. **Connect Looker Studio** and build dashboards
7. **Embed** on your website

---

Good luck! 🚀

For detailed instructions, see the other documentation files.

