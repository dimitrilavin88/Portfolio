import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import kaggle
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount templates directory
templates = Jinja2Templates(directory="templates")

# Global variables for model and data
MODEL = None
SCALER = None
DF = None

def download_dataset():
    dataset_name = 'meraxes10/fantasy-premier-league-dataset-2024-2025'
    download_path = './data/'
    os.makedirs(download_path, exist_ok=True)
    os.environ["KAGGLE_USERNAME"] = os.getenv("KAGGLE_USERNAME")
    os.environ["KAGGLE_KEY"] = os.getenv("KAGGLE_KEY")
    kaggle.api.authenticate()
    kaggle.api.dataset_download_files(dataset_name, path=download_path, unzip=True)
    print("Dataset downloaded successfully!")

def initialize_model():
    global MODEL, SCALER, DF
    
    # Read the dataset
    df = pd.read_csv('./data/players.csv')
    
    # Select relevant features
    features = [
        'minutes', 'goals_scored', 'assists', 'clean_sheets',
        'goals_conceded', 'own_goals', 'penalties_saved',
        'penalties_missed', 'yellow_cards', 'red_cards',
        'saves', 'bonus', 'influence', 'creativity', 'threat'
    ]
    
    # Clean the data
    df = df.dropna(subset=features + ['value_season'])
    X = df[features]
    y = df['value_season']
    
    # Train the model
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Initialize and train XGBoost model
    model = xgb.XGBRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_scaled, y)
    
    # Store in global variables
    MODEL = model
    SCALER = scaler
    DF = df

@app.on_event("startup")
async def startup_event():
    download_dataset()
    initialize_model()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/top_players")
async def get_top_players():
    try:
        # Make predictions using the stored model
        X = DF[[
            'minutes', 'goals_scored', 'assists', 'clean_sheets',
            'goals_conceded', 'own_goals', 'penalties_saved',
            'penalties_missed', 'yellow_cards', 'red_cards',
            'saves', 'bonus', 'influence', 'creativity', 'threat'
        ]]
        X_scaled = SCALER.transform(X)
        predictions = MODEL.predict(X_scaled)
        DF['predicted_value'] = predictions
        
        # Add print statement to verify number of players
        top_players = DF.nlargest(25, 'predicted_value')[
            ['name', 'team', 'value_season', 'predicted_value']
        ]
        print(f"Number of players being sent: {len(top_players)}")  # Debug line
        
        return {
            "status": "success",
            "top_players": top_players.to_dict(orient='records')
        }
    except Exception as e:
        print(f"Error: {str(e)}")  # Debug line
        return {
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    # Use the environment variable PORT for binding the app to the correct port
    port = int(os.getenv("PORT", 8000))  # Default to 8000 if PORT is not set
    uvicorn.run(app, host="0.0.0.0", port=port)  # Ensure the app listens on all interfaces
