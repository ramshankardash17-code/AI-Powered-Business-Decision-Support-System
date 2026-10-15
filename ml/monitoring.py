"""
ML Model Performance & Data Drift Monitoring Module
Enterprise AI Business Decision Intelligence Platform
Calculates Population Stability Index (PSI), Feature Drift, and Logs Health Metrics
"""
import logging
from datetime import datetime
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from sqlalchemy import text
from config.settings import settings
from database.connection import engine, SessionLocal
from database.models import ModelMonitoringLog

logger = logging.getLogger(__name__)

def calculate_psi(expected: np.ndarray, actual: np.ndarray, num_buckets: int = 10) -> float:
    """
    Calculates Population Stability Index (PSI) between baseline and production distributions.
    PSI < 0.10: No significant shift
    0.10 <= PSI < 0.25: Moderate shift / warning
    PSI >= 0.25: Significant drift requiring retraining
    """
    if len(expected) == 0 or len(actual) == 0:
        return 0.0

    percentiles = np.linspace(0, 100, num_buckets + 1)
    bucket_bounds = np.percentile(expected, percentiles)
    bucket_bounds[0] = -np.inf
    bucket_bounds[-1] = np.inf

    expected_counts = np.histogram(expected, bins=bucket_bounds)[0]
    actual_counts = np.histogram(actual, bins=bucket_bounds)[0]

    expected_pct = np.maximum(expected_counts / len(expected), 1e-4)
    actual_pct = np.maximum(actual_counts / len(actual), 1e-4)

    psi_value = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
    return float(round(psi_value, 4))

class ModelMonitoringEngine:
    def __init__(self):
        self.drift_threshold = settings.DRIFT_ALERT_THRESHOLD

    def evaluate_churn_model_drift(self) -> Dict[str, Any]:
        """Audits churn probability predictions and primary feature distributions for drift"""
        logger.info("Auditing Churn Model performance and drift...")
        sql = "SELECT recency_days, return_rate, monetary_total, churn_probability FROM customer_ml_features;"
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)

        # Baseline split: 50% baseline vs 50% current batch
        mid_idx = len(df) // 2
        baseline_df = df.iloc[:mid_idx]
        current_df = df.iloc[mid_idx:]

        # Check PSI on prediction distribution
        prob_psi = calculate_psi(baseline_df["churn_probability"].values, current_df["churn_probability"].values)
        
        # Check KS test on primary input features
        feature_audits = []
        for feature in ["recency_days", "return_rate", "monetary_total"]:
            b_vals = baseline_df[feature].values
            c_vals = current_df[feature].values
            ks_stat, p_value = ks_2samp(b_vals, c_vals)
            f_psi = calculate_psi(b_vals, c_vals)
            drift_detected = bool(f_psi >= self.drift_threshold or p_value < 0.01)

            feature_audits.append({
                "feature": feature,
                "psi_score": f_psi,
                "ks_statistic": round(float(ks_stat), 4),
                "p_value": round(float(p_value), 4),
                "drift_detected": drift_detected,
                "status": "DRIFT WARNING" if drift_detected else "HEALTHY"
            })

        prediction_drift = bool(prob_psi >= self.drift_threshold)
        
        # Log to DB
        db = SessionLocal()
        log_entry = ModelMonitoringLog(
            model_name="Customer Churn Classifier (Champion)",
            model_version="v2.1.0-prod",
            metric_name="Prediction_PSI",
            metric_value=prob_psi,
            drift_detected=prediction_drift,
            psi_score=prob_psi,
            notes=f"Evaluated across {len(df)} customer samples. Prediction PSI: {prob_psi}."
        )
        db.add(log_entry)
        db.commit()
        db.close()

        return {
            "model_name": "Customer Churn Classifier",
            "model_version": "v2.1.0-prod",
            "evaluated_at": datetime.utcnow().isoformat(),
            "prediction_psi": prob_psi,
            "prediction_drift_detected": prediction_drift,
            "overall_status": "DRIFT WARNING" if prediction_drift else "HEALTHY",
            "drift_threshold": self.drift_threshold,
            "feature_drifts": feature_audits,
            "prediction_summary": {
                "mean_churn_prob": round(float(df["churn_probability"].mean()), 3),
                "high_risk_share_pct": round(float((df["churn_probability"] >= 0.70).mean() * 100), 2),
                "low_risk_share_pct": round(float((df["churn_probability"] < 0.35).mean() * 100), 2)
            }
        }

    def get_monitoring_history(self) -> List[Dict[str, Any]]:
        """Returns recent monitoring run logs"""
        sql = "SELECT * FROM model_monitoring_logs ORDER BY recorded_at DESC LIMIT 20;"
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)
        return df.to_dict(orient="records")

if __name__ == "__main__":
    monitor = ModelMonitoringEngine()
    print("Drift Audit:", monitor.evaluate_churn_model_drift())
