"""
Baseline & Statistical Demand Forecasting Models
Enterprise AI Business Decision Intelligence Platform
Implements Moving Average and Ridge Regression as Baselines for Model Comparison
"""
import logging
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sqlalchemy import text
from database.connection import engine

logger = logging.getLogger(__name__)

def mean_absolute_percentage_error(y_true, y_pred) -> float:
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    non_zero = y_true != 0
    if np.sum(non_zero) == 0:
        return 0.0
    return float(np.mean(np.abs((y_true[non_zero] - y_pred[non_zero]) / y_true[non_zero])) * 100)

class BaselineForecaster:
    def __init__(self):
        pass

    def load_daily_series(self) -> pd.DataFrame:
        """Fetches enterprise daily sales series"""
        sql = """
        SELECT
            dd.full_date,
            dd.day_of_week,
            dd.month,
            dd.is_weekend,
            dd.is_festive_season,
            ROUND(SUM(fs.net_sales), 2) AS sales_volume,
            ROUND(AVG(fs.discount_amount), 2) AS avg_discount,
            SUM(fs.quantity) AS units_sold
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        GROUP BY dd.full_date, dd.day_of_week, dd.month, dd.is_weekend, dd.is_festive_season
        ORDER BY dd.full_date ASC;
        """
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)
        df["date"] = pd.to_datetime(df["full_date"])
        return df

    def evaluate_baselines(self, test_days: int = 30) -> Dict[str, Any]:
        """Compares 7-day Moving Average vs 30-day Moving Average vs Ridge Regressor"""
        df = self.load_daily_series()
        if len(df) < 60:
            return {"error": "Need at least 60 days of historical sales data."}

        # Train / Test split
        train_df = df.iloc[:-test_days].copy()
        test_df = df.iloc[-test_days:].copy()

        y_test = test_df["sales_volume"].values

        # 1. 7-Day Moving Average Forecast
        ma7_pred = [train_df["sales_volume"].tail(7).mean()] * test_days
        ma7_rmse = float(np.sqrt(mean_squared_error(y_test, ma7_pred)))
        ma7_mae = float(mean_absolute_error(y_test, ma7_pred))
        ma7_mape = mean_absolute_percentage_error(y_test, ma7_pred)

        # 2. 30-Day Moving Average Forecast
        ma30_pred = [train_df["sales_volume"].tail(30).mean()] * test_days
        ma30_rmse = float(np.sqrt(mean_squared_error(y_test, ma30_pred)))
        ma30_mae = float(mean_absolute_error(y_test, ma30_pred))
        ma30_mape = mean_absolute_percentage_error(y_test, ma30_pred)

        # 3. Ridge Regression with Lags and Calendar Features
        df_feat = df.copy()
        for lag in [1, 7, 14, 30]:
            df_feat[f"lag_{lag}"] = df_feat["sales_volume"].shift(lag)
        df_feat = df_feat.dropna()

        feature_cols = ["day_of_week", "month", "is_weekend", "is_festive_season", "avg_discount", "lag_1", "lag_7", "lag_14", "lag_30"]
        train_feat = df_feat.iloc[:-test_days]
        test_feat = df_feat.iloc[-test_days:]

        ridge = Ridge(alpha=1.0)
        ridge.fit(train_feat[feature_cols], train_feat["sales_volume"])
        ridge_pred = ridge.predict(test_feat[feature_cols])

        ridge_rmse = float(np.sqrt(mean_squared_error(test_feat["sales_volume"], ridge_pred)))
        ridge_mae = float(mean_absolute_error(test_feat["sales_volume"], ridge_pred))
        ridge_mape = mean_absolute_percentage_error(test_feat["sales_volume"], ridge_pred)

        return {
            "7_Day_Moving_Average": {
                "rmse": round(ma7_rmse, 2),
                "mae": round(ma7_mae, 2),
                "mape_pct": round(ma7_mape, 2)
            },
            "30_Day_Moving_Average": {
                "rmse": round(ma30_rmse, 2),
                "mae": round(ma30_mae, 2),
                "mape_pct": round(ma30_mape, 2)
            },
            "Ridge_Lag_Regression": {
                "rmse": round(ridge_rmse, 2),
                "mae": round(ridge_mae, 2),
                "mape_pct": round(ridge_mape, 2)
            }
        }

if __name__ == "__main__":
    b = BaselineForecaster()
    print("Baseline Metrics:", b.evaluate_baselines())
