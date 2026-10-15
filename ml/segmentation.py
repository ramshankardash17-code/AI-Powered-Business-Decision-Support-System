"""
Customer Segmentation Engine (RFM + K-Means Clustering)
Enterprise AI Business Decision Intelligence Platform
Maps Clusters to Actionable Business Segments: Champions, High Value, Potential Loyalists,
Discount Seekers, At Risk, and Dormant
"""
import logging
from typing import Dict, Any, List
import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sqlalchemy import text
from config.settings import settings
from database.connection import engine

logger = logging.getLogger(__name__)

RFM_COLS = ["recency_days", "frequency_orders", "monetary_total", "avg_discount_rate"]

class CustomerSegmentationEngine:
    def __init__(self, n_clusters: int = 5):
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.models_dir = settings.MODELS_DIR

    def train_and_segment(self) -> Dict[str, Any]:
        """Runs RFM clustering and updates database customer segments"""
        logger.info("Executing RFM K-Means Customer Segmentation...")
        sql = "SELECT * FROM customer_ml_features;"
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)

        X = df[RFM_COLS].fillna(0)
        # Log-transform monetary and frequency to handle positive skewness
        X_trans = X.copy()
        X_trans["monetary_total"] = np.log1p(X_trans["monetary_total"])
        X_trans["frequency_orders"] = np.log1p(X_trans["frequency_orders"])
        
        X_scaled = self.scaler.fit_transform(X_trans)
        cluster_labels = self.kmeans.fit_predict(X_scaled)
        df["cluster"] = cluster_labels

        # Calculate cluster centroids to assign meaningful business labels
        cluster_stats = df.groupby("cluster").agg(
            recency=("recency_days", "mean"),
            frequency=("frequency_orders", "mean"),
            monetary=("monetary_total", "mean"),
            discount=("avg_discount_rate", "mean"),
            size=("customer_id", "count")
        ).reset_index()

        # Business mapping heuristic based on centroid ranking
        segment_names = {}
        for _, row in cluster_stats.iterrows():
            c_id = int(row["cluster"])
            m = row["monetary"]
            r = row["recency"]
            f = row["frequency"]
            d = row["discount"]

            if m > 30000 and r < 90:
                name = "Champions"
            elif m > 18000 and f >= 4:
                name = "High Value Loyalists"
            elif d > 0.18:
                name = "Discount Seekers"
            elif r > 150:
                name = "At Risk / Dormant"
            else:
                name = "Potential Loyalists"
            segment_names[c_id] = name

        df["rfm_segment"] = df["cluster"].map(segment_names)
        
        # Save model artifacts
        joblib.dump(self.kmeans, self.models_dir / "kmeans_segmentation.joblib")
        joblib.dump(self.scaler, self.models_dir / "kmeans_scaler.joblib")

        # Update database
        cols = [
            "customer_id", "recency_days", "frequency_orders", "monetary_total", "avg_order_value",
            "total_returns", "return_rate", "avg_discount_rate", "negative_reviews_count",
            "avg_delivery_delay", "tenure_days", "rfm_segment", "churn_probability",
            "churn_risk_level", "predicted_clv", "is_high_value_high_churn"
        ]
        df[cols].to_sql("customer_ml_features", con=engine, if_exists="replace", index=False)
        logger.info("Successfully updated customer segments in database.")

        # Summary for UI
        summary = df.groupby("rfm_segment").agg(
            customer_count=("customer_id", "count"),
            avg_monetary=("monetary_total", "mean"),
            avg_frequency=("frequency_orders", "mean"),
            avg_recency=("recency_days", "mean"),
            avg_churn_prob=("churn_probability", "mean")
        ).round(2).reset_index()

        return {
            "n_clusters": self.n_clusters,
            "segments_summary": summary.to_dict(orient="records"),
            "total_customers_segmented": len(df)
        }

if __name__ == "__main__":
    seg = CustomerSegmentationEngine()
    print("Segmentation Summary:", seg.train_and_segment())
