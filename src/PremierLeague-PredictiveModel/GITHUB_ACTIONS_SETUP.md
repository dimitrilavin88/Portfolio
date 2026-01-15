# GitHub Actions Setup Guide

This guide explains how to set up GitHub Actions to automatically run your ETL and predictions pipeline.

## Overview

GitHub Actions will call your Render API endpoints on a schedule to:
1. Run the ETL pipeline (extract data from Kaggle, load to Neon & Google Sheets)
2. Generate predictions (train model, create predictions, update database & Google Sheets)

## Prerequisites

- ✅ Your FastAPI app deployed on Render
- ✅ API endpoints `/api/run-etl` and `/api/run-predictions` working
- ✅ GitHub repository with Actions enabled

## Step 1: Add GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** (top menu)
3. Click **Secrets and variables** → **Actions** (left sidebar)
4. Click **New repository secret**

### Required Secrets

#### 1. `RENDER_APP_URL`
- **Name:** `RENDER_APP_URL`
- **Value:** Your Render app URL (without trailing slash)
- **Example:** `https://premier-league-predictor.onrender.com`

**How to find it:**
- Go to Render dashboard → Your service → Settings
- Copy the URL from "Service URL" or "Custom Domain"

#### 2. `ETL_API_KEY` (Optional but Recommended)
- **Name:** `ETL_API_KEY`
- **Value:** Your API key (must match the one in Render)
- **Example:** `your-secret-api-key-12345`

**If you haven't set an API key yet:**
1. Generate a secure random string (e.g., use `openssl rand -hex 32`)
2. Add it to Render: Environment tab → `ETL_API_KEY=your-key`
3. Add it to GitHub Secrets: `ETL_API_KEY=your-key`

**Note:** If you don't set this, the workflow will still work, but your endpoints won't be secured.

## Step 2: Verify Render Configuration

Make sure your Render app has these environment variables set:

- `KAGGLE_USERNAME`
- `KAGGLE_KEY`
- `DATABASE_URL`
- `GOOGLE_SHEETS_SPREADSHEET_ID`
- `GOOGLE_SERVICE_ACCOUNT_JSON`
- `ETL_API_KEY` (if using authentication)

## Step 3: Test the Workflow

### Manual Test

1. Go to your GitHub repository
2. Click **Actions** tab
3. Select **ETL and Predictions Pipeline** from the left sidebar
4. Click **Run workflow** button (top right)
5. Select branch: `master` or `main`
6. Click **Run workflow**
7. Watch the execution in real-time

### Check Results

- ✅ **Green checkmark** = Success
- ❌ **Red X** = Failure (check logs for errors)

Click on a workflow run to see detailed logs:
- Each step shows what it's doing
- Response from Render API is displayed
- Errors are clearly marked

## Step 4: Customize Schedule

The workflow is currently set to run **every 15 minutes**. To change this:

1. Edit `.github/workflows/etl-pipeline.yml`
2. Find the `schedule` section:
   ```yaml
   schedule:
     - cron: '*/15 * * * *'  # Every 15 minutes
   ```
3. Change the cron expression

### Common Schedules

| Schedule | Cron Expression | Description |
|----------|----------------|-------------|
| Every 15 minutes | `*/15 * * * *` | Current setting |
| Every 30 minutes | `*/30 * * * *` | Less frequent |
| Every hour | `0 * * * *` | Hourly |
| Every 6 hours | `0 */6 * * *` | 4 times per day |
| Daily at 2 AM | `0 2 * * *` | Once per day |
| Daily at midnight | `0 0 * * *` | Once per day |

**Cron format:** `minute hour day month day-of-week`

**Note:** GitHub Actions may have slight delays (up to a few minutes) due to queue times.

## Step 5: Monitor Workflow Runs

### View History

1. Go to **Actions** tab
2. Click on **ETL and Predictions Pipeline**
3. See all past runs with their status

### Set Up Notifications

1. Go to repository **Settings** → **Notifications**
2. Enable email notifications for workflow failures
3. Or use GitHub mobile app for push notifications

## Troubleshooting

### ❌ Workflow fails: "Connection refused" or timeout

**Possible causes:**
- Render app is sleeping (free tier)
- Incorrect Render URL
- Render app is down

**Solutions:**
- First request after sleep may take 30-60 seconds (Render cold start)
- Verify URL in Render dashboard
- Check Render service status

### ❌ Workflow fails: 401 Unauthorized

**Cause:** API key mismatch

**Solution:**
- Verify `ETL_API_KEY` in GitHub Secrets matches Render environment variable
- Check for extra spaces or newlines in the secret
- If not using authentication, the workflow handles empty API key

### ❌ Workflow fails: 404 Not Found

**Cause:** Incorrect endpoint URL

**Solution:**
- Verify endpoints exist: `/api/run-etl` and `/api/run-predictions`
- Check Render logs to see if endpoints are registered
- Test endpoints manually: `curl -X POST https://your-app.onrender.com/api/run-etl`

### ❌ Workflow fails: 500 Internal Server Error

**Cause:** Error in ETL or predictions script

**Solution:**
- Check Render logs for detailed error messages
- Verify all environment variables are set correctly
- Test endpoints manually to see error details

### ⚠️ Workflow runs but data doesn't update

**Possible causes:**
- ETL runs but fails silently
- Database connection issues
- Google Sheets API errors

**Solution:**
- Check Render application logs
- Verify database and Google Sheets credentials
- Check workflow logs for response details

## Advanced Configuration

### Run Only ETL (Skip Predictions)

Edit the workflow and comment out the `run-predictions` job:

```yaml
# run-predictions:
#   name: Run Predictions Generation
#   ...
```

### Run on Push to Main

Uncomment the push trigger:

```yaml
on:
  schedule:
    - cron: '*/15 * * * *'
  workflow_dispatch:
  push:
    branches:
      - master
      - main
```

### Add Slack/Discord Notifications

Add a notification step after each job:

```yaml
- name: Notify on Success
  if: success()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## Security Best Practices

1. **Never commit secrets** - Always use GitHub Secrets
2. **Use API keys** - Protect your endpoints with authentication
3. **Rotate keys regularly** - Change API keys periodically
4. **Monitor logs** - Check for unauthorized access attempts
5. **Limit permissions** - Use least privilege principle

## Cost Considerations

- **GitHub Actions:** Free tier includes 2,000 minutes/month
- **Render:** Free tier has usage limits
- **Frequency:** Running every 15 minutes = ~2,880 runs/month
- **Recommendation:** Consider hourly or daily schedule for free tier

## Support

If you encounter issues:
1. Check workflow logs in GitHub Actions
2. Check Render application logs
3. Verify all secrets are set correctly
4. Test endpoints manually with curl

---

**Next Steps:**
- ✅ Set up GitHub Secrets
- ✅ Test workflow manually
- ✅ Monitor first few automated runs
- ✅ Adjust schedule if needed

