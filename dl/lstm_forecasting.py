"""
Deep Learning Demand Forecasting (PyTorch LSTM Sequence Model)
Enterprise AI Business Decision Intelligence Platform
Uses 30-Day Sequence History with Multi-Variate Features
Compares Performance Directly Against Moving Averages and Ridge Regression
"""
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sqlalchemy import text
from config.settings import settings
from database.connection import engine
from dl.baseline_forecast import BaselineForecaster, mean_absolute_percentage_error

logger = logging.getLogger(__name__)

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class SalesDemandLSTM(nn.Module):
    def __init__(self, input_dim: int = 5, hidden_dim: int = 64, num_layers: int = 2, output_dim: int = 1):
        super(SalesDemandLSTM, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, output_dim)
        )

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

class DemandForecastingPipeline:
    def __init__(self, seq_length: int = 30):
        self.seq_length = seq_length
        self.scaler = MinMaxScaler()
        self.model = None
        self.models_dir = settings.MODELS_DIR
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.model_path = self.models_dir / "lstm_demand_forecaster.pt"

    def load_data(self) -> pd.DataFrame:
        """Fetches daily series from fact_sales and dim_date"""
        sql = """
        SELECT
            dd.full_date,
            ROUND(SUM(fs.net_sales), 2) AS sales_volume,
            ROUND(AVG(fs.discount_amount), 2) AS avg_discount,
            AVG(dd.day_of_week) AS day_of_week,
            MAX(CASE WHEN dd.is_weekend = 1 OR dd.is_weekend = TRUE THEN 1 ELSE 0 END) AS is_weekend,
            MAX(CASE WHEN dd.is_festive_season = 1 OR dd.is_festive_season = TRUE THEN 1 ELSE 0 END) AS is_festive
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        GROUP BY dd.full_date
        ORDER BY dd.full_date ASC;
        """
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)
        return df

    def create_sequences(self, data: np.ndarray, seq_len: int) -> Tuple[np.ndarray, np.ndarray]:
        xs, ys = [], []
        for i in range(len(data) - seq_len):
            x = data[i:(i + seq_len), :]
            y = data[i + seq_len, 0] # target is sales_volume (index 0)
            xs.append(x)
            ys.append(y)
        return np.array(xs), np.array(ys)

    def train_and_evaluate(self, epochs: int = 25, test_days: int = 30) -> Dict[str, Any]:
        """
        Trains PyTorch LSTM sequence model and runs benchmark comparison against Baselines
        """
        logger.info(f"Training LSTM Sequence Demand Forecaster (Seq Length: {self.seq_length})...")
        df = self.load_data()
        
        feature_cols = ["sales_volume", "avg_discount", "day_of_week", "is_weekend", "is_festive"]
        raw_vals = df[feature_cols].values
        
        # Scale features
        scaled_vals = self.scaler.fit_transform(raw_vals)
        sales_min = self.scaler.data_min_[0]
        sales_max = self.scaler.data_max_[0]

        X, y = self.create_sequences(scaled_vals, self.seq_length)
        
        # Train / Test split
        X_train, X_test = X[:-test_days], X[-test_days:]
        y_train, y_test = y[:-test_days], y[-test_days:]

        train_dataset = TensorDataset(torch.tensor(X_train, dtype=torch.float32), torch.tensor(y_train, dtype=torch.float32))
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

        self.model = SalesDemandLSTM(input_dim=len(feature_cols), hidden_dim=64, num_layers=2).to(device)
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.005)

        self.model.train()
        for epoch in range(epochs):
            for batch_x, batch_y in train_loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                optimizer.zero_grad()
                out = self.model(batch_x).squeeze(-1)
                loss = criterion(out, batch_y)
                loss.backward()
                optimizer.step()

        # Evaluate on test set
        self.model.eval()
        with torch.no_grad():
            test_x_tensor = torch.tensor(X_test, dtype=torch.float32).to(device)
            scaled_preds = self.model(test_x_tensor).cpu().numpy().squeeze(-1)

        # Inverse transform target
        y_test_orig = y_test * (sales_max - sales_min) + sales_min
        preds_orig = scaled_preds * (sales_max - sales_min) + sales_min

        lstm_rmse = float(np.sqrt(mean_squared_error(y_test_orig, preds_orig)))
        lstm_mae = float(mean_absolute_error(y_test_orig, preds_orig))
        lstm_mape = mean_absolute_percentage_error(y_test_orig, preds_orig)

        # Baseline comparisons
        baseline_forecaster = BaselineForecaster()
        baseline_metrics = baseline_forecaster.evaluate_baselines(test_days=test_days)

        # Determine winner
        all_models = {
            "LSTM Sequence Model (Deep Learning)": {"rmse": round(lstm_rmse, 2), "mae": round(lstm_mae, 2), "mape_pct": round(lstm_mape, 2)},
            "Ridge Lag Regression": baseline_metrics["Ridge_Lag_Regression"],
            "7-Day Moving Average": baseline_metrics["7_Day_Moving_Average"],
            "30-Day Moving Average": baseline_metrics["30_Day_Moving_Average"]
        }
        best_model_name = min(all_models.items(), key=lambda x: x[1]["rmse"])[0]

        # Save model weights
        torch.save({
            "model_state_dict": self.model.state_dict(),
            "scaler": self.scaler,
            "seq_length": self.seq_length
        }, self.model_path)

        logger.info(f"Demand Forecasting benchmarks completed. Best Model: {best_model_name} (LSTM RMSE: {lstm_rmse:.2f})")

        return {
            "comparison_benchmarks": all_models,
            "champion_forecasting_model": best_model_name,
            "lstm_metrics": {
                "rmse": round(lstm_rmse, 2),
                "mae": round(lstm_mae, 2),
                "mape_pct": round(lstm_mape, 2)
            },
            "sequence_window_days": self.seq_length,
            "evaluation_horizon_days": test_days
        }

    def generate_future_forecast(self, horizon_days: int = 30) -> List[Dict[str, Any]]:
        """Generates future sales forecast with confidence intervals"""
        df = self.load_data()
        feature_cols = ["sales_volume", "avg_discount", "day_of_week", "is_weekend", "is_festive"]
        raw_vals = df[feature_cols].values
        
        if self.model is None:
            if self.model_path.exists():
                checkpoint = torch.load(self.model_path, map_location=device)
                self.scaler = checkpoint["scaler"]
                self.model = SalesDemandLSTM(input_dim=len(feature_cols), hidden_dim=64, num_layers=2).to(device)
                self.model.load_state_dict(checkpoint["model_state_dict"])
                self.model.eval()
            else:
                self.train_and_evaluate(epochs=20)

        scaled_vals = self.scaler.transform(raw_vals)
        sales_min = self.scaler.data_min_[0]
        sales_max = self.scaler.data_max_[0]

        current_seq = scaled_vals[-self.seq_length:].copy()
        last_date = pd.to_datetime(df["full_date"].iloc[-1])
        
        forecast_results = []
        self.model.eval()

        with torch.no_grad():
            for day in range(1, horizon_days + 1):
                f_date = last_date + pd.Timedelta(days=day)
                x_in = torch.tensor(current_seq, dtype=torch.float32).unsqueeze(0).to(device)
                pred_scaled = self.model(x_in).cpu().item()

                pred_val = max(1000.0, pred_scaled * (sales_max - sales_min) + sales_min)
                
                # Confidence interval (standard error estimate ~ 12%)
                margin = pred_val * 0.12
                lower_bound = max(0.0, round(pred_val - margin, 2))
                upper_bound = round(pred_val + margin, 2)

                forecast_results.append({
                    "forecast_date": f_date.strftime("%Y-%m-%d"),
                    "predicted_sales": round(pred_val, 2),
                    "lower_confidence_bound": lower_bound,
                    "upper_confidence_bound": upper_bound,
                    "day_name": f_date.strftime("%A")
                })

                # Roll sequence forward
                is_wknd = 1.0 if f_date.weekday() in [5, 6] else 0.0
                is_fest = 1.0 if f_date.month in [10, 11, 12] else 0.0
                new_row = np.array([pred_scaled, current_seq[-1, 1], f_date.weekday(), is_wknd, is_fest])
                current_seq = np.vstack([current_seq[1:], new_row])

        return forecast_results

if __name__ == "__main__":
    dl_pipeline = DemandForecastingPipeline(seq_length=30)
    eval_res = dl_pipeline.train_and_evaluate(epochs=15)
    print("Forecasting Benchmarks:", eval_res)
    future = dl_pipeline.generate_future_forecast(horizon_days=14)
    print("Next 14 Days Sample Forecast:", future[:3])
