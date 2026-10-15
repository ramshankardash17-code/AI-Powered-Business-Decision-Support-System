"""
Product Return Propensity & Risk Prediction Module
Enterprise AI Business Decision Intelligence Platform
Predicts likelihood of an item being returned based on product, order, delivery, and customer traits
"""
import logging
from typing import Dict, Any, List
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score
from sqlalchemy import text
from config.settings import settings
from database.connection import engine

logger = logging.getLogger(__name__)

class ReturnPredictionEngine:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
        self.models_dir = settings.MODELS_DIR
        self.cat_mappings = {}

    def train_return_model(self) -> Dict[str, Any]:
        """Trains Return Prediction Classifier using historical order items and returns"""
        logger.info("Training Return Propensity Prediction Model...")
        sql = """
        SELECT
            oi.order_item_id,
            oi.order_id,
            oi.product_id,
            dp.category,
            oi.unit_price,
            oi.discount_amount,
            fo.delivery_days,
            cmf.return_rate AS customer_return_history,
            CASE WHEN fr.return_id IS NOT NULL THEN 1 ELSE 0 END AS is_returned
        FROM order_items oi
        JOIN dim_product dp ON oi.product_id = dp.product_id
        JOIN fact_orders fo ON oi.order_id = fo.order_id
        JOIN customer_ml_features cmf ON fo.customer_id = cmf.customer_id
        LEFT JOIN fact_returns fr ON oi.order_id = fr.order_id AND oi.product_id = fr.product_id;
        """
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)

        # One-hot encode category
        cat_dummies = pd.get_dummies(df["category"], prefix="cat", drop_first=True, dtype=int)
        self.cat_mappings = cat_dummies.columns.tolist()

        X = pd.concat([
            df[["unit_price", "discount_amount", "delivery_days", "customer_return_history"]],
            cat_dummies
        ], axis=1).fillna(0)
        y = df["is_returned"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )
        self.model.fit(X_train, y_train)

        probs = self.model.predict_proba(X_test)[:, 1]
        preds = self.model.predict(X_test)

        auc = roc_auc_score(y_test, probs)
        f1 = f1_score(y_test, preds)
        prec = precision_score(y_test, preds, zero_division=0)
        rec = recall_score(y_test, preds, zero_division=0)

        # Feature importance
        fi = pd.DataFrame({
            "feature": X.columns,
            "importance": self.model.feature_importances_
        }).sort_values(by="importance", ascending=False).to_dict(orient="records")

        # Save artifacts
        joblib.dump({
            "model": self.model,
            "feature_names": X.columns.tolist()
        }, self.models_dir / "return_predictor.joblib")

        logger.info(f"Return Model trained. ROC-AUC: {auc:.4f}, F1: {f1:.4f}")

        return {
            "roc_auc": round(float(auc), 4),
            "f1_score": round(float(f1), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "feature_importance": fi,
            "training_samples": len(X_train),
            "test_samples": len(X_test)
        }

    def predict_return_risk(self, item_features: Dict[str, Any]) -> Dict[str, Any]:
        """Inference for a new order item"""
        artifact_path = self.models_dir / "return_predictor.joblib"
        if not artifact_path.exists():
            self.train_return_model()
        artifact = joblib.load(artifact_path)
        model = artifact["model"]
        expected_cols = artifact["feature_names"]

        row = {col: 0 for col in expected_cols}
        row["unit_price"] = item_features.get("unit_price", 1500.0)
        row["discount_amount"] = item_features.get("discount_amount", 0.0)
        row["delivery_days"] = item_features.get("delivery_days", 3)
        row["customer_return_history"] = item_features.get("customer_return_history", 0.05)

        cat_col = f"cat_{item_features.get('category', 'Electronics')}"
        if cat_col in row:
            row[cat_col] = 1

        X_in = pd.DataFrame([row])[expected_cols]
        prob = float(model.predict_proba(X_in)[0, 1])
        risk_cat = "High" if prob >= 0.35 else ("Medium" if prob >= 0.18 else "Low")

        return {
            "return_probability": round(prob, 3),
            "risk_category": risk_cat,
            "key_risk_factors": [
                f"Category '{item_features.get('category')}' return propensity",
                f"Delivery transit duration ({item_features.get('delivery_days', 3)} days)",
                f"Customer historical return rate ({item_features.get('customer_return_history', 0.05)*100:.1f}%)"
            ]
        }

if __name__ == "__main__":
    ret_engine = ReturnPredictionEngine()
    print("Return Model Evaluation:", ret_engine.train_return_model())
