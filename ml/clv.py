"""
Customer Lifetime Value (CLV) & High-Value Risk Engine
Enterprise AI Business Decision Intelligence Platform
Predicts 12-Month Future Value and Tags HIGH VALUE + HIGH CHURN RISK Customers
"""
import logging
from typing import Dict, Any, List
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sqlalchemy import text
from config.settings import settings
from database.connection import engine

logger = logging.getLogger(__name__)

CLV_FEATURES = [
    "frequency_orders",
    "monetary_total",
    "avg_order_value",
    "recency_days",
    "tenure_days",
    "avg_discount_rate",
    "return_rate"
]

class CustomerLifetimeValueEngine:
    def __init__(self):
        self.model = GradientBoostingRegressor(n_estimators=80, max_depth=4, random_state=42)
        self.models_dir = settings.MODELS_DIR

    def train_and_predict(self) -> Dict[str, Any]:
        """Trains CLV regressor, predicts future 12-month value, and flags critical retention segments"""
        logger.info("Training Customer Lifetime Value (CLV) model...")
        sql = "SELECT * FROM customer_ml_features;"
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)

        # Future 12-month spending proxy: based on purchase velocity adjusted for churn retention
        annual_order_rate = (df["frequency_orders"] / np.maximum(df["tenure_days"] / 365.0, 0.25)).clip(0.5, 24.0)
        retention_factor = (1.0 - df["churn_probability"]).clip(0.1, 0.95)
        simulated_future_clv = (annual_order_rate * df["avg_order_value"] * retention_factor * np.random.uniform(0.9, 1.1, len(df))).round(2)
        
        df["target_future_clv"] = simulated_future_clv

        X = df[CLV_FEATURES].fillna(0)
        y = df["target_future_clv"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
        self.model.fit(X_train, y_train)

        preds = self.model.predict(X_test)
        rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
        r2 = float(r2_score(y_test, preds))

        # Predict future CLV across entire customer base
        all_preds = self.model.predict(X)
        df["predicted_clv"] = np.round(np.maximum(100.0, all_preds), 2)

        # Flag HIGH VALUE + HIGH CHURN RISK
        clv_75th = df["predicted_clv"].quantile(0.75)
        df["is_high_value_high_churn"] = (
            (df["predicted_clv"] >= clv_75th) & (df["churn_risk_level"] == "High")
        )

        joblib.dump(self.model, self.models_dir / "clv_model.joblib")

        # Update database
        cols = [
            "customer_id", "recency_days", "frequency_orders", "monetary_total", "avg_order_value",
            "total_returns", "return_rate", "avg_discount_rate", "negative_reviews_count",
            "avg_delivery_delay", "tenure_days", "rfm_segment", "churn_probability",
            "churn_risk_level", "predicted_clv", "is_high_value_high_churn"
        ]
        df[cols].to_sql("customer_ml_features", con=engine, if_exists="replace", index=False)
        logger.info("Successfully updated customer CLV and High-Value Risk flags.")

        high_val_high_churn_df = df[df["is_high_value_high_churn"]]

        return {
            "model_r2_score": round(r2, 4),
            "model_rmse": round(rmse, 2),
            "high_value_clv_threshold": round(float(clv_75th), 2),
            "total_high_value_high_churn_customers": int(len(high_val_high_churn_df)),
            "high_risk_clv_at_stake": round(float(high_val_high_churn_df["predicted_clv"].sum()), 2),
            "top_at_risk_customers": high_val_high_churn_df.sort_values(by="predicted_clv", ascending=False).head(10)[[
                "customer_id", "monetary_total", "predicted_clv", "churn_probability", "recency_days"
            ]].to_dict(orient="records")
        }

if __name__ == "__main__":
    clv_engine = CustomerLifetimeValueEngine()
    print("CLV Results:", clv_engine.train_and_predict())
