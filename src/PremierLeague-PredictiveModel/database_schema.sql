-- Premier League MVP Predictor Database Schema
-- For Neon PostgreSQL Database

-- Create tables for storing player data, predictions, and ETL tracking

-- Main players table (current snapshot of player data)
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY,
    name VARCHAR(255),
    web_name VARCHAR(255),
    team VARCHAR(100),
    position VARCHAR(10),
    now_cost DECIMAL(10, 2),
    value_season DECIMAL(10, 2),
    total_points INTEGER,
    points_per_game DECIMAL(5, 2),
    selected_by_percent DECIMAL(5, 2),
    form DECIMAL(5, 2),
    minutes INTEGER,
    goals_scored INTEGER,
    assists INTEGER,
    clean_sheets INTEGER,
    goals_conceded INTEGER,
    yellow_cards INTEGER,
    red_cards INTEGER,
    saves INTEGER,
    bonus INTEGER,
    influence DECIMAL(10, 2),
    creativity DECIMAL(10, 2),
    threat DECIMAL(10, 2),
    ict_index DECIMAL(10, 2),
    starts INTEGER,
    expected_goals DECIMAL(5, 2),
    expected_assists DECIMAL(5, 2),
    expected_goal_involvements DECIMAL(5, 2),
    status VARCHAR(1),
    news TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Player history table (for tracking changes over time)
CREATE TABLE IF NOT EXISTS player_history (
    id SERIAL PRIMARY KEY,
    player_id INTEGER,
    name VARCHAR(255),
    team VARCHAR(100),
    position VARCHAR(10),
    value_season DECIMAL(10, 2),
    total_points INTEGER,
    goals_scored INTEGER,
    assists INTEGER,
    minutes INTEGER,
    snapshot_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE
);

-- Predictions table (stores model predictions)
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    player_id INTEGER,
    predicted_value DECIMAL(10, 2),
    model_version VARCHAR(50),
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence_score DECIMAL(5, 2),
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE
);

-- Data updates tracking table (for ETL monitoring)
CREATE TABLE IF NOT EXISTS data_updates (
    id SERIAL PRIMARY KEY,
    update_type VARCHAR(50), -- 'full_refresh', 'incremental', 'kaggle_download'
    rows_inserted INTEGER,
    rows_updated INTEGER,
    status VARCHAR(20), -- 'success', 'failed', 'in_progress'
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_seconds INTEGER
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_players_team ON players(team);
CREATE INDEX IF NOT EXISTS idx_players_position ON players(position);
CREATE INDEX IF NOT EXISTS idx_players_value_season ON players(value_season DESC);
CREATE INDEX IF NOT EXISTS idx_players_total_points ON players(total_points DESC);
CREATE INDEX IF NOT EXISTS idx_player_history_player_id ON player_history(player_id);
CREATE INDEX IF NOT EXISTS idx_player_history_snapshot_date ON player_history(snapshot_date);
CREATE INDEX IF NOT EXISTS idx_predictions_player_id ON predictions(player_id);
CREATE INDEX IF NOT EXISTS idx_predictions_prediction_date ON predictions(prediction_date);
CREATE INDEX IF NOT EXISTS idx_data_updates_completed_at ON data_updates(completed_at DESC);

