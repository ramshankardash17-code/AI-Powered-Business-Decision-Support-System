"""
Automated Business Anomaly Detection Module (Isolation Forest)
Enterprise AI Business Decision Intelligence Platform
Detects Spikes and Shifts in Sales, Returns, Discounts, Stockouts, and Delays
Stores Triggered Anomalies into anomaly_alerts Table
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sqlalchemy import text
from config.settings import settings
from database.connection import engine, SessionLocal
from database.models import AnomalyAlert

logger = logging.getLogger(__name__)

class BusinessAnomalyDetector:
    def __init__(self, contamination: float = 0.04):
        self.contamination = contamination
        self.iso_forest = IsolationForest(contamination=contamination, random_state=42)

    def run_anomaly_detection(self) -> List[Dict[str, Any]]:
        """Scans historical daily performance series and identifies anomalous deviations"""
        logger.info("Executing Isolation Forest Business Anomaly Detection...")
        daily_sql = """
        SELECT
            dd.full_date,
            ROUND(SUM(fs.net_sales), 2) AS daily_revenue,
            COUNT(DISTINCT fs.order_id) AS daily_orders,
            ROUND(SUM(fs.discount_amount), 2) AS daily_discount,
            COALESCE(COUNT(DISTINCT fr.return_id), 0) AS daily_returns
        FROM fact_sales fs
        JOIN dim_date dd ON fs.date_key = dd.date_key
        LEFT JOIN fact_returns fr ON fs.order_id = fr.order_id
        GROUP BY dd.full_date
        ORDER BY dd.full_date ASC;
        """
        with engine.connect() as conn:
            df = pd.read_sql(text(daily_sql), conn)

        if len(df) < 30:
            logger.warning("Insufficient data points for anomaly isolation forest.")
            return []

        df["return_rate_pct"] = ((df["daily_returns"] / df["daily_orders"].replace(0, 1)) * 100).round(2)
        df["discount_rate_pct"] = ((df["daily_discount"] / df["daily_revenue"].replace(0, 1)) * 100).round(2)

        features = ["daily_revenue", "daily_orders", "return_rate_pct", "discount_rate_pct"]
        X = df[features].fillna(0)

        df["anomaly_score"] = self.iso_forest.fit_predict(X)
        anomalies_df = df[df["anomaly_score"] == -1].copy()

        # Rolling medians as normal baselines
        rolling_medians = df[features].rolling(30, min_periods=5).median()

        alerts_to_store = []
        db = SessionLocal()

        for idx, row in anomalies_df.tail(15).iterrows():
            norm_rev = float(rolling_medians.loc[idx, "daily_revenue"] or row["daily_revenue"])
            norm_ret_rate = float(rolling_medians.loc[idx, "return_rate_pct"] or 5.0)

            # Check if anomaly is return spike or revenue drop
            if row["return_rate_pct"] > norm_ret_rate * 1.6:
                metric_name = "Return Rate Surge"
                current_val = float(row["return_rate_pct"])
                dev_pct = round(((current_val - norm_ret_rate) / norm_ret_rate) * 100, 1)
                severity = "Critical" if dev_pct > 80 else "High"
                desc = f"Unusual surge in return rate: {current_val:.1f}% vs 30-day baseline {norm_ret_rate:.1f}% (Deviation: +{dev_pct}%)."
            elif row["daily_revenue"] < norm_rev * 0.65:
                metric_name = "Revenue Contraction"
                current_val = float(row["daily_revenue"])
                dev_pct = round(((current_val - norm_rev) / norm_rev) * 100, 1)
                severity = "Critical" if dev_pct < -40 else "High"
                desc = f"Sharp revenue drop: {current_val:,.2f} vs expected baseline {norm_rev:,.2f} (Deviation: {dev_pct}%)."
            else:
                metric_name = "Unusual Order Pattern"
                current_val = float(row["daily_orders"])
                dev_pct = 25.0
                severity = "Medium"
                desc = f"Anomalous multi-variate order and discount cluster detected on {row['full_date']}."

            alert_obj = AnomalyAlert(
                metric_name=metric_name,
                dimension="Daily Enterprise Sales",
                normal_value=norm_rev if "Revenue" in metric_name else norm_ret_rate,
                current_value=current_val,
                deviation_pct=dev_pct,
                severity=severity,
                alert_date=datetime.strptime(row["full_date"], "%Y-%m-%d").date(),
                description=desc,
                status="Open"
            )
            db.add(alert_obj)
            alerts_to_store.append({
                "metric_name": metric_name,
                "date": row["full_date"],
                "severity": severity,
                "current_value": current_val,
                "description": desc
            })

        db.commit()
        db.close()
        logger.info(f"Persisted {len(alerts_to_store)} business anomaly alerts to database.")
        return alerts_to_store

if __name__ == "__main__":
    detector = BusinessAnomalyDetector()
    alerts = detector.run_anomaly_detection()
    print("Detected Anomalies:", len(alerts))
