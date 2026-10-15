"""
Customer Churn Prediction & Explainability Module
Enterprise AI Business Decision Intelligence Platform
Compares Logistic Regression, Random Forest, and XGBoost
Extracts Feature Importances / Explainability & Persists Trained Models
"""
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    roc_auc_score, f1_score, precision_score, recall_score, confusion_matrix, average_precision_score
)
from sklearn.preprocessing import StandardScaler
from sqlalchemy import text
from config.settings import settings
from database.connection import engine

logger = logging.getLogger(__name__)

FEATURE_COLS = [
    "recency_days",
    "frequency_orders",
    "monetary_total",
    "avg_order_value",
    "total_returns",
    "return_rate",
    "avg_discount_rate",
    "negative_reviews_count",
    "avg_delivery_delay",
    "tenure_days"
]

class ChurnModelPipeline:
    def __init__(self):
        self.models_dir = settings.MODELS_DIR
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.scaler = StandardScaler()
        self.best_model = None
        self.best_model_name = ""

    def load_feature_dataset(self) -> pd.DataFrame:
        """Loads customer features from feature store"""
        sql = "SELECT * FROM customer_ml_features;"
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)
            
        # Ground truth churn label proxy:
        # A customer is churned if recency > 120 days or (recency > 60 and high returns/negative reviews)
        churn_condition = (
            (df["recency_days"] > 140) | 
            ((df["recency_days"] > 75) & ((df["return_rate"] > 0.25) | (df["negative_reviews_count"] >= 2)))
        )
        df["churn_label"] = np.where(churn_condition, 1, 0)
        return df

    def train_and_compare(self) -> Dict[str, Any]:
        """
        Trains LogisticRegression, RandomForest, and XGBoost.
        Evaluates metrics (Precision, Recall, F1, ROC-AUC, PR-AUC).
        Selects champion model based on evaluation.
        """
        logger.info("Training and comparing Churn Prediction candidate models...")
        df = self.load_feature_dataset()
        
        X = df[FEATURE_COLS].fillna(0)
        y = df["churn_label"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )

        # Scale features for linear model
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        candidate_models = {
            "Logistic Regression": (
                LogisticRegression(max_iter=1000, random_state=42),
                X_train_scaled,
                X_test_scaled
            ),
            "Random Forest": (
                RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42),
                X_train,
                X_test
            ),
            "XGBoost": (
                XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=42, eval_metric="logloss"),
                X_train,
                X_test
            )
        }

        results = {}
        best_auc = -1.0

        for name, (model, tr_x, te_x) in candidate_models.items():
            model.fit(tr_x, y_train)
            preds = model.predict(te_x)
            probs = model.predict_proba(te_x)[:, 1]

            auc = roc_auc_score(y_test, probs)
            pr_auc = average_precision_score(y_test, probs)
            f1 = f1_score(y_test, preds)
            prec = precision_score(y_test, preds, zero_division=0)
            rec = recall_score(y_test, preds, zero_division=0)
            cm = confusion_matrix(y_test, preds).tolist()

            results[name] = {
                "roc_auc": round(float(auc), 4),
                "pr_auc": round(float(pr_auc), 4),
                "f1_score": round(float(f1), 4),
                "precision": round(float(prec), 4),
                "recall": round(float(rec), 4),
                "confusion_matrix": cm
            }

            if auc > best_auc:
                best_auc = auc
                self.best_model_name = name
                self.best_model = model

        logger.info(f"Selected Champion Model: '{self.best_model_name}' with ROC-AUC: {best_auc:.4f}")

        # Save artifacts
        model_path = self.models_dir / "churn_champion_model.joblib"
        scaler_path = self.models_dir / "churn_scaler.joblib"
        joblib.dump({"model_name": self.best_model_name, "model": self.best_model}, model_path)
        joblib.dump(self.scaler, scaler_path)

        # Feature Importance
        feature_importance = self._extract_feature_importance(self.best_model, self.best_model_name)

        # Update probabilities in customer_ml_features table
        self._update_database_predictions(df, X)

        return {
            "candidate_evaluations": results,
            "champion_model": self.best_model_name,
            "best_roc_auc": round(float(best_auc), 4),
            "feature_importance": feature_importance,
            "test_sample_size": len(y_test),
            "train_sample_size": len(y_train)
        }

    def _extract_feature_importance(self, model, model_name: str) -> List[Dict[str, Any]]:
        """Extracts explainable importance weights from champion model"""
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        elif hasattr(model, "coef_"):
            importances = np.abs(model.coef_[0])
        else:
            importances = np.ones(len(FEATURE_COLS)) / len(FEATURE_COLS)

        fi_df = pd.DataFrame({
            "feature": FEATURE_COLS,
            "importance": importances
        }).sort_values(by="importance", ascending=False)
        fi_df["importance"] = (fi_df["importance"] / fi_df["importance"].sum()).round(4)
        return fi_df.to_dict(orient="records")

    def _update_database_predictions(self, full_df: pd.DataFrame, X: pd.DataFrame):
        """Scores all customers with champion model and updates database"""
        if self.best_model_name == "Logistic Regression":
            X_scored = self.scaler.transform(X)
        else:
            X_scored = X

        probs = self.best_model.predict_proba(X_scored)[:, 1]
        full_df["churn_probability"] = np.round(probs, 3)
        full_df["churn_risk_level"] = np.where(
            full_df["churn_probability"] >= 0.70, "High",
            np.where(full_df["churn_probability"] >= 0.35, "Medium", "Low")
        )
        full_df["is_high_value_high_churn"] = (
            (full_df["monetary_total"] > 15000) & (full_df["churn_risk_level"] == "High")
        )

        cols = [
            "customer_id", "recency_days", "frequency_orders", "monetary_total", "avg_order_value",
            "total_returns", "return_rate", "avg_discount_rate", "negative_reviews_count",
            "avg_delivery_delay", "tenure_days", "rfm_segment", "churn_probability",
            "churn_risk_level", "predicted_clv", "is_high_value_high_churn"
        ]
        full_df[cols].to_sql("customer_ml_features", con=engine, if_exists="replace", index=False)
        logger.info("Updated customer_ml_features with trained model churn probabilities.")

    def predict_single(self, customer_features: Dict[str, float]) -> Dict[str, Any]:
        """Real-time inference endpoint for single customer scoring"""
        if self.best_model is None:
            model_path = self.models_dir / "churn_champion_model.joblib"
            if model_path.exists():
                artifact = joblib.load(model_path)
                self.best_model = artifact["model"]
                self.best_model_name = artifact["model_name"]
                self.scaler = joblib.load(self.models_dir / "churn_scaler.joblib")
            else:
                self.train_and_compare()

        input_df = pd.DataFrame([customer_features])[FEATURE_COLS].fillna(0)
        if self.best_model_name == "Logistic Regression":
            X_in = self.scaler.transform(input_df)
        else:
            X_in = input_df

        prob = float(self.best_model.predict_proba(X_in)[0, 1])
        risk_level = "High" if prob >= 0.70 else ("Medium" if prob >= 0.35 else "Low")

        # Top local drivers
        drivers = []
        if customer_features.get("recency_days", 0) > 120:
            drivers.append("High days since last order (Inactivity)")
        if customer_features.get("return_rate", 0) > 0.20:
            drivers.append("Elevated return propensity")
        if customer_features.get("negative_reviews_count", 0) > 0:
            drivers.append("Recorded negative feedback / complaints")
        if customer_features.get("avg_delivery_delay", 0) > 6:
            drivers.append("Experienced fulfillment delivery delays")

        return {
            "churn_probability": round(prob, 3),
            "churn_risk_level": risk_level,
            "model_used": self.best_model_name,
            "primary_drivers": drivers or ["Normal customer order cadence"]
        }

if __name__ == "__main__":
    churn_pipeline = ChurnModelPipeline()
    res = churn_pipeline.train_and_compare()
    print("Churn Model Comparison:", res)
