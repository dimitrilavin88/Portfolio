# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automating the Premier League MVP Predictor pipeline.

## Workflows

### `etl-pipeline.yml`

Automates the ETL (Extract, Transform, Load) and predictions generation pipeline.

**Features:**
- Runs every 15 minutes on a schedule
- Can be triggered manually from GitHub Actions UI
- Calls Render API endpoints to trigger ETL and predictions
- Sequential execution: ETL runs first, then predictions

**Schedule:**
- Currently set to run every 15 minutes (`*/15 * * * *`)
- You can modify the cron schedule in the workflow file

**Required GitHub Secrets:**

1. **`RENDER_APP_URL`**
   - Your Render application URL
   - Example: `https://your-app-name.onrender.com`
   - No trailing slash

2. **`ETL_API_KEY`** (Optional but recommended)
   - API key for securing the endpoints
   - Must match the `ETL_API_KEY` environment variable set in Render
   - If not set in Render, you can leave this empty (but it's not secure)

## Setup Instructions

### 1. Add GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

   - **Name:** `RENDER_APP_URL`
     **Value:** `https://your-render-app.onrender.com`
   
   - **Name:** `ETL_API_KEY`
     **Value:** (Your API key, or leave empty if not using authentication)

### 2. Configure Render Environment Variables

Make sure your Render app has the `ETL_API_KEY` environment variable set (if you're using authentication):

1. Go to Render dashboard
2. Navigate to your service
3. Go to **Environment** tab
4. Add: `ETL_API_KEY=your-secret-key-here`

### 3. Test the Workflow

1. Go to **Actions** tab in GitHub
2. Select **ETL and Predictions Pipeline**
3. Click **Run workflow** → **Run workflow**
4. Monitor the execution

### 4. Customize Schedule

To change the schedule, edit `.github/workflows/etl-pipeline.yml`:

```yaml
schedule:
  - cron: '*/15 * * * *'  # Every 15 minutes
```

**Common cron schedules:**
- Every hour: `0 * * * *`
- Every 6 hours: `0 */6 * * *`
- Daily at 2 AM: `0 2 * * *`
- Every 30 minutes: `*/30 * * * *`

**Cron format:** `minute hour day month day-of-week`

## Monitoring

- Check workflow runs in the **Actions** tab
- Failed runs will show error messages
- Successful runs will show response data from the API

## Troubleshooting

### Workflow fails with "Connection refused" or timeout
- Check that your Render app URL is correct
- Ensure your Render app is running (not sleeping)
- Render free tier apps sleep after inactivity - first request may take longer

### Workflow fails with 401 Unauthorized
- Check that `ETL_API_KEY` secret matches the value in Render
- If not using authentication, remove the `X-API-Key` header from the workflow

### Workflow fails with 404 Not Found
- Verify the endpoint URLs are correct: `/api/run-etl` and `/api/run-predictions`
- Check that your FastAPI app is deployed correctly on Render

### Predictions run before ETL completes
- The workflow uses `needs: run-etl` to ensure sequential execution
- There's a 5-second delay between ETL and predictions
- If ETL takes longer than expected, increase the delay

