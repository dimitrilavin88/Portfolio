"""
ETL Pipeline for Premier League MVP Predictor
Extracts data from Kaggle, transforms it, and loads into:
1. Neon PostgreSQL Database
2. Google Sheets (for Looker Studio)

This script can be run manually or scheduled (e.g., via Render cron jobs)
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import kaggle
import psycopg2
import gspread
from google.oauth2.service_account import Credentials
import json
import time
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

class ETLPipeline:
    def __init__(self):
        """Initialize ETL pipeline with database and Google Sheets connections"""
        self.start_time = time.time()
        self.rows_inserted = 0
        self.rows_updated = 0
        
        # Initialize connections
        self.db_conn = None
        self.db_cursor = None
        self.gc = None  # Google Sheets client
        
        # Setup connections
        self._setup_database()
        self._setup_google_sheets()
    
    def _setup_database(self):
        """Setup PostgreSQL connection to Neon database"""
        try:
            # Get connection string from environment variable
            database_url = os.getenv("DATABASE_URL")
            
            if not database_url:
                raise ValueError("DATABASE_URL environment variable not set")
            
            # Connect to database
            self.db_conn = psycopg2.connect(database_url)
            self.db_cursor = self.db_conn.cursor()
            print("✅ Connected to Neon PostgreSQL database")
        except Exception as e:
            print(f"❌ Database connection error: {str(e)}")
            raise
    
    def _setup_google_sheets(self):
        """Setup Google Sheets API connection"""
        try:
            # Get service account key from environment variable (JSON string) or file
            service_account_info = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
            spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
            
            if not service_account_info and not os.path.exists("service_account_key.json"):
                print("⚠️  Google Sheets credentials not found. Skipping Google Sheets update.")
                return
            
            if not spreadsheet_id:
                print("⚠️  GOOGLE_SHEETS_SPREADSHEET_ID not set. Skipping Google Sheets update.")
                return
            
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
            
            self.gc = gspread.authorize(creds)
            self.spreadsheet_id = spreadsheet_id
            print("✅ Connected to Google Sheets")
        except Exception as e:
            print(f"⚠️  Google Sheets setup error: {str(e)}")
            print("Continuing without Google Sheets update...")
            self.gc = None
    
    def extract(self) -> pd.DataFrame:
        """Extract data from Kaggle dataset"""
        try:
            print("📥 Extracting data from Kaggle...")
            
            # Set Kaggle credentials from environment variables
            os.environ["KAGGLE_USERNAME"] = os.getenv("KAGGLE_USERNAME", "")
            os.environ["KAGGLE_KEY"] = os.getenv("KAGGLE_KEY", "")
            
            # Authenticate Kaggle API
            kaggle.api.authenticate()
            
            # Download dataset
            dataset_name = 'meraxes10/fantasy-premier-league-dataset-2025-2026'
            download_path = './data/'
            os.makedirs(download_path, exist_ok=True)
            
            kaggle.api.dataset_download_files(dataset_name, path=download_path, unzip=True)
            
            # Read the CSV file
            df = pd.read_csv('./data/players.csv')
            print(f"✅ Extracted {len(df)} rows from Kaggle")
            
            return df
        except Exception as e:
            print(f"❌ Extraction error: {str(e)}")
            raise
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform and clean the data"""
        try:
            print("🔄 Transforming data...")
            
            # Select relevant columns for our use case
            columns_to_keep = [
                'id', 'name', 'web_name', 'team', 'position', 'now_cost', 'value_season',
                'total_points', 'points_per_game', 'selected_by_percent', 'form', 'minutes',
                'goals_scored', 'assists', 'clean_sheets', 'goals_conceded', 'yellow_cards',
                'red_cards', 'saves', 'bonus', 'influence', 'creativity', 'threat', 'ict_index',
                'starts', 'expected_goals', 'expected_assists', 'expected_goal_involvements',
                'status', 'news'
            ]
            
            # Keep only columns that exist in the dataframe
            available_columns = [col for col in columns_to_keep if col in df.columns]
            df = df[available_columns].copy()
            
            # Rename 'id' to 'player_id' for consistency
            if 'id' in df.columns:
                df.rename(columns={'id': 'player_id'}, inplace=True)
            
            # Clean data types
            numeric_columns = ['now_cost', 'value_season', 'points_per_game', 'selected_by_percent',
                             'form', 'influence', 'creativity', 'threat', 'ict_index',
                             'expected_goals', 'expected_assists', 'expected_goal_involvements']
            
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            integer_columns = ['player_id', 'total_points', 'minutes', 'goals_scored', 'assists',
                             'clean_sheets', 'goals_conceded', 'yellow_cards', 'red_cards',
                             'saves', 'bonus', 'starts']
            
            for col in integer_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
            
            # Handle NaN values in text columns
            text_columns = ['name', 'web_name', 'team', 'position', 'status', 'news']
            for col in text_columns:
                if col in df.columns:
                    df[col] = df[col].fillna('').astype(str)
            
            # Replace NaN with None for database insertion
            df = df.replace({np.nan: None})
            
            print(f"✅ Transformed {len(df)} rows")
            return df
        
        except Exception as e:
            print(f"❌ Transformation error: {str(e)}")
            raise
    
    def load_to_database(self, df: pd.DataFrame):
        """Load data into Neon PostgreSQL database"""
        try:
            if not self.db_conn:
                print("⚠️  Database connection not available. Skipping database load.")
                return
            
            print("💾 Loading data to Neon PostgreSQL database...")
            
            # Get columns that exist in dataframe
            columns = [col for col in df.columns if col != 'created_at']
            
            # Create upsert query (insert or update on conflict)
            placeholders = ', '.join(['%s'] * len(columns))
            columns_str = ', '.join(columns)
            update_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'player_id'])
            
            query = f"""
                INSERT INTO players ({columns_str}, last_updated)
                VALUES ({placeholders}, CURRENT_TIMESTAMP)
                ON CONFLICT (player_id) 
                DO UPDATE SET {update_clause}, last_updated = CURRENT_TIMESTAMP
            """
            
            # Prepare data for insertion
            values = [tuple(row) for row in df[columns].values]
            
            # Execute batch insert using executemany (works better with ON CONFLICT)
            self.db_cursor.executemany(query, values)
            self.db_conn.commit()
            
            self.rows_inserted = len(df)
            print(f"✅ Loaded {self.rows_inserted} rows to database")
        
        except Exception as e:
            self.db_conn.rollback()
            print(f"❌ Database load error: {str(e)}")
            raise
    
    def load_to_google_sheets(self, df: pd.DataFrame):
        """Load data into Google Sheets"""
        try:
            if not self.gc:
                print("⚠️  Google Sheets client not available. Skipping Google Sheets update.")
                return
            
            print("📊 Loading data to Google Sheets...")
            
            # Open the spreadsheet
            spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
            
            # Try to open or create the worksheet
            try:
                worksheet = spreadsheet.worksheet("Players")
            except gspread.exceptions.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title="Players", rows=1000, cols=30)
            
            # Prepare data for Google Sheets
            # Select columns for Google Sheets (you can customize this)
            sheets_columns = [
                'player_id', 'name', 'web_name', 'team', 'position', 'now_cost', 'value_season',
                'total_points', 'points_per_game', 'selected_by_percent', 'form', 'minutes',
                'goals_scored', 'assists', 'clean_sheets', 'goals_conceded', 'yellow_cards',
                'red_cards', 'saves', 'bonus', 'influence', 'creativity', 'threat', 'ict_index',
                'starts', 'status'
            ]
            
            # Keep only columns that exist
            sheets_columns = [col for col in sheets_columns if col in df.columns]
            
            # Convert dataframe to list of lists
            data = df[sheets_columns].fillna('').values.tolist()
            headers = sheets_columns
            
            # Clear existing data and update
            worksheet.clear()
            worksheet.update([headers] + data, value_input_option='USER_ENTERED')
            
            print(f"✅ Loaded {len(data)} rows to Google Sheets")
        
        except Exception as e:
            print(f"⚠️  Google Sheets load error: {str(e)}")
            # Don't raise - allow pipeline to continue even if Google Sheets fails
    
    def log_update(self, status: str, error_message: Optional[str] = None):
        """Log ETL update to database"""
        try:
            if not self.db_conn:
                return
            
            duration = int(time.time() - self.start_time)
            
            query = """
                INSERT INTO data_updates 
                (update_type, rows_inserted, rows_updated, status, error_message, started_at, completed_at, duration_seconds)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            self.db_cursor.execute(query, (
                'full_refresh',
                self.rows_inserted,
                self.rows_updated,
                status,
                error_message,
                datetime.fromtimestamp(self.start_time),
                datetime.now(),
                duration
            ))
            self.db_conn.commit()
        
        except Exception as e:
            print(f"⚠️  Error logging update: {str(e)}")
    
    def run(self):
        """Run the complete ETL pipeline"""
        try:
            print("🚀 Starting ETL Pipeline...")
            print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Extract
            df = self.extract()
            
            # Transform
            df = self.transform(df)
            
            # Load to database
            self.load_to_database(df)
            
            # Load to Google Sheets
            self.load_to_google_sheets(df)
            
            # Log success
            self.log_update('success')
            
            duration = time.time() - self.start_time
            print(f"\n✅ ETL Pipeline completed successfully!")
            print(f"⏱️  Duration: {duration:.2f} seconds")
            print(f"📊 Rows processed: {self.rows_inserted}")
        
        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ ETL Pipeline failed: {error_msg}")
            self.log_update('failed', error_msg)
            raise
        
        finally:
            # Close connections
            if self.db_cursor:
                self.db_cursor.close()
            if self.db_conn:
                self.db_conn.close()
            print("🔌 Database connections closed")

def main():
    """Main entry point for the ETL pipeline"""
    pipeline = ETLPipeline()
    pipeline.run()

if __name__ == "__main__":
    main()

