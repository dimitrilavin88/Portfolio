"""
Generate Predictions Script
Loads data from the database, trains the model, and stores predictions
"""

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
import json

# Load environment variables from .env file
load_dotenv()

def get_database_connection():
    """Get PostgreSQL database connection"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    return psycopg2.connect(database_url)

def load_data_from_database():
    """Load player data from the database"""
    conn = get_database_connection()
    try:
        # Load all available feature columns from database
        query = """
            SELECT 
                player_id, name, team, position,
                minutes, goals_scored, assists, clean_sheets,
                goals_conceded, yellow_cards, red_cards,
                saves, bonus, influence, creativity, threat,
                value_season
            FROM players
            WHERE minutes IS NOT NULL
        """
        df = pd.read_sql_query(query, conn)
        print(f"✅ Loaded {len(df)} players from database")
        return df
    finally:
        conn.close()

def train_model(df):
    """Train the XGBoost model"""
    # Select features for training (using features available in database)
    # Note: Using a subset of features that are in the database
    features = [
        'minutes', 'goals_scored', 'assists', 'clean_sheets',
        'goals_conceded', 'yellow_cards', 'red_cards',
        'saves', 'bonus', 'influence', 'creativity', 'threat'
    ]
    
    # Verify all features exist in dataframe
    available_features = [f for f in features if f in df.columns]
    if len(available_features) != len(features):
        missing = set(features) - set(available_features)
        print(f"⚠️  Warning: Missing features {missing}, using available features")
        features = available_features
    
    # Remove rows with missing values in features or target
    df_clean = df.dropna(subset=features + ['value_season'])
    
    if len(df_clean) == 0:
        raise ValueError("No valid data for training after cleaning")
    
    X = df_clean[features]
    y = df_clean['value_season']
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train model
    model = xgb.XGBRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_scaled, y)
    
    print(f"✅ Model trained on {len(df_clean)} players")
    return model, scaler, features

def generate_predictions(model, scaler, features, df):
    """Generate predictions for all players"""
    # Filter to players with all required features
    df_features = df.dropna(subset=features).copy()
    
    # Prepare features
    X = df_features[features]
    X_scaled = scaler.transform(X)
    
    # Generate predictions
    predictions = model.predict(X_scaled)
    
    # Add predictions to dataframe (convert to Python float to avoid numpy type issues)
    df_features['predicted_value'] = predictions.astype(float)
    
    print(f"✅ Generated {len(predictions)} predictions")
    return df_features[['player_id', 'predicted_value']]

def store_predictions(df_predictions, model_version="v1.0"):
    """Store predictions in the database - updates existing predictions to avoid duplicates"""
    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # First, delete existing predictions for this model_version to avoid duplicates
        delete_query = "DELETE FROM predictions WHERE model_version = %s"
        cursor.execute(delete_query, (model_version,))
        deleted_count = cursor.rowcount
        if deleted_count > 0:
            print(f"   Deleted {deleted_count} old predictions for model version {model_version}")
        
        # Insert new predictions
        insert_query = """
            INSERT INTO predictions (player_id, predicted_value, model_version, prediction_date)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        """
        
        # Prepare data for insertion (similar to ETL pipeline approach)
        # Convert DataFrame to list of tuples
        predictions_data = [
            (int(row[0]), float(row[1]), model_version)
            for row in df_predictions[['player_id', 'predicted_value']].values
        ]
        
        cursor.executemany(insert_query, predictions_data)
        conn.commit()
        
        print(f"✅ Stored {len(predictions_data)} predictions in database")
    
    except Exception as e:
        conn.rollback()
        print(f"❌ Error storing predictions: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def get_all_predictions_with_players():
    """Get all predictions joined with player data from database"""
    conn = get_database_connection()
    try:
        # Get the most recent predictions for each player
        query = """
            WITH latest_predictions AS (
                SELECT 
                    player_id,
                    MAX(prediction_date) as latest_date
                FROM predictions
                GROUP BY player_id
            )
            SELECT 
                p.player_id,
                p.name,
                p.team,
                p.position,
                p.value_season,
                pred.predicted_value,
                pred.model_version,
                pred.prediction_date
            FROM predictions pred
            JOIN players p ON pred.player_id = p.player_id
            JOIN latest_predictions lp ON pred.player_id = lp.player_id 
                AND pred.prediction_date = lp.latest_date
            ORDER BY pred.predicted_value DESC
        """
        df = pd.read_sql_query(query, conn)
        print(f"✅ Fetched {len(df)} predictions with player data")
        return df
    except Exception as e:
        print(f"⚠️  Error fetching predictions: {str(e)}")
        # Return empty dataframe with expected columns
        return pd.DataFrame(columns=['player_id', 'name', 'team', 'position', 
                                     'value_season', 'predicted_value', 'model_version', 'prediction_date'])
    finally:
        conn.close()

def get_top_predictions(limit=25):
    """Get top predictions from database (for verification) - only latest per player"""
    conn = get_database_connection()
    try:
        query = """
            WITH latest_predictions AS (
                SELECT 
                    player_id,
                    MAX(prediction_date) as latest_date
                FROM predictions
                GROUP BY player_id
            )
            SELECT 
                p.player_id,
                p.name,
                p.team,
                p.position,
                p.value_season,
                pred.predicted_value,
                pred.model_version,
                pred.prediction_date
            FROM predictions pred
            JOIN players p ON pred.player_id = p.player_id
            JOIN latest_predictions lp ON pred.player_id = lp.player_id 
                AND pred.prediction_date = lp.latest_date
            ORDER BY pred.predicted_value DESC
            LIMIT %s
        """
        df = pd.read_sql_query(query, conn, params=(limit,))
        return df
    finally:
        conn.close()

def setup_google_sheets():
    """Setup Google Sheets API connection"""
    try:
        # Get service account key from environment variable (JSON string) or file
        service_account_info = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
        
        if not service_account_info and not os.path.exists("service_account_key.json"):
            print("⚠️  Google Sheets credentials not found. Skipping Google Sheets update.")
            return None, None
        
        if not spreadsheet_id:
            print("⚠️  GOOGLE_SHEETS_SPREADSHEET_ID not set. Skipping Google Sheets update.")
            return None, None
        
        # Load service account credentials
        if service_account_info:
            # Credentials from environment variable (for Render deployment)
            creds_dict = json.loads(service_account_info)
            creds = Credentials.from_service_account_info(
                creds_dict,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
        else:
            # Credentials from file (for local development)
            creds = Credentials.from_service_account_file(
                "service_account_key.json",
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
        
        gc = gspread.authorize(creds)
        print("✅ Connected to Google Sheets")
        return gc, spreadsheet_id
    except Exception as e:
        print(f"⚠️  Google Sheets setup error: {str(e)}")
        print("Continuing without Google Sheets update...")
        return None, None

def load_predictions_to_google_sheets(df_predictions):
    """Load predictions to Google Sheets as a separate worksheet"""
    try:
        gc, spreadsheet_id = setup_google_sheets()
        
        if not gc or not spreadsheet_id:
            print("⚠️  Google Sheets client not available. Skipping Google Sheets update.")
            return
        
        # Check if dataframe is empty
        if df_predictions.empty:
            print("⚠️  No predictions data to load. DataFrame is empty.")
            return
        
        print(f"📊 Loading {len(df_predictions)} predictions to Google Sheets...")
        
        # Open the spreadsheet
        spreadsheet = gc.open_by_key(spreadsheet_id)
        
        # Try to open or create the "Predictions" worksheet
        try:
            worksheet = spreadsheet.worksheet("Predictions")
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title="Predictions", rows=1000, cols=20)
        
        # Prepare data for Google Sheets
        # Select columns to include
        sheets_columns = [
            'player_id', 'name', 'team', 'position', 
            'value_season', 'predicted_value', 'model_version', 'prediction_date'
        ]
        
        # Keep only columns that exist
        sheets_columns = [col for col in sheets_columns if col in df_predictions.columns]
        
        if not sheets_columns:
            print("⚠️  No matching columns found in predictions data")
            print(f"Available columns: {df_predictions.columns.tolist()}")
            return
        
        # Create a copy for formatting (convert Timestamp to string)
        df_formatted = df_predictions[sheets_columns].copy()
        
        # Convert Timestamp/datetime columns to string
        for col in df_formatted.columns:
            if pd.api.types.is_datetime64_any_dtype(df_formatted[col]):
                df_formatted[col] = df_formatted[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            elif hasattr(df_formatted[col].dtype, 'name') and 'datetime' in str(df_formatted[col].dtype):
                df_formatted[col] = df_formatted[col].astype(str)
        
        # Fill NaN values and convert to list of lists
        df_formatted = df_formatted.fillna('')
        data = df_formatted.values.tolist()
        headers = sheets_columns
        
        # Clear existing data and update
        worksheet.clear()
        worksheet.update([headers] + data, value_input_option='USER_ENTERED')
        
        print(f"✅ Loaded {len(data)} prediction rows to Google Sheets")
    
    except Exception as e:
        print(f"⚠️  Google Sheets load error: {str(e)}")
        import traceback
        traceback.print_exc()
        # Don't raise - allow script to continue even if Google Sheets fails

def main():
    """Main function to generate and store predictions"""
    print("🚀 Starting Prediction Generation...")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Load data from database
        df = load_data_from_database()
        
        # Train model
        model, scaler, features = train_model(df)
        
        # Generate predictions
        df_predictions = generate_predictions(model, scaler, features, df)
        
        # Store predictions in database
        model_version = "v1.0"
        store_predictions(df_predictions, model_version)
        
        # Prepare predictions with player data for Google Sheets
        print("\n📥 Preparing predictions with player data for Google Sheets...")
        print(f"   Predictions dataframe shape: {df_predictions.shape}")
        print(f"   Player dataframe shape: {df.shape}")
        
        # Ensure player_id types match for merge
        df_predictions['player_id'] = df_predictions['player_id'].astype(int)
        df['player_id'] = df['player_id'].astype(int)
        
        # Merge predictions with player data from the original dataframe
        df_predictions_full = df_predictions.merge(
            df[['player_id', 'name', 'team', 'position', 'value_season']],
            on='player_id',
            how='left'
        )
        
        print(f"   After merge shape: {df_predictions_full.shape}")
        print(f"   Columns: {df_predictions_full.columns.tolist()}")
        
        # Check if merge worked
        if df_predictions_full.empty:
            print("⚠️  Warning: Merged dataframe is empty!")
        elif df_predictions_full['name'].isna().all():
            print("⚠️  Warning: Merge didn't work - no player names found!")
        
        # Add model_version and prediction_date
        df_predictions_full['model_version'] = model_version
        df_predictions_full['prediction_date'] = datetime.now()
        
        # Reorder columns for Google Sheets
        df_predictions_full = df_predictions_full[[
            'player_id', 'name', 'team', 'position', 
            'value_season', 'predicted_value', 'model_version', 'prediction_date'
        ]]
        
        print(f"   Final dataframe shape: {df_predictions_full.shape}")
        print(f"   Sample data:\n{df_predictions_full.head()}")
        
        # Load predictions to Google Sheets
        load_predictions_to_google_sheets(df_predictions_full)
        
        # Show top predictions
        print("\n📊 Top 10 Predictions:")
        top_predictions = get_top_predictions(limit=10)
        print(top_predictions[['name', 'team', 'value_season', 'predicted_value']].to_string(index=False))
        
        print(f"\n✅ Prediction generation completed successfully!")
        print(f"📊 Total predictions stored: {len(df_predictions)}")
    
    except Exception as e:
        print(f"\n❌ Prediction generation failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()

