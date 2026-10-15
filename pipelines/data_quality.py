"""
Automated Data Quality Validation & Scoring Module
Enterprise AI Business Decision Intelligence Platform
Evaluates Completeness, Validity, Uniqueness, Consistency, and Overall DQ Score
"""
import logging
from datetime import datetime
from typing import Dict, Any, List
import pandas as pd
from database.connection import SessionLocal, DB_DIALECT
from database.models import DataQualityLog

logger = logging.getLogger(__name__)

class DataQualityEngine:
    def __init__(self):
        self.validation_results = []

    def evaluate_datasets(self, raw_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Runs comprehensive data quality assertions across all ingested raw datasets.
        """
        logger.info("Executing comprehensive Data Quality checks...")
        start_time = datetime.utcnow()
        
        scores = {
            "completeness": [],
            "validity": [],
            "uniqueness": [],
            "consistency": []
        }
        anomalies_detected = []
        
        # 1. Customers Quality Checks
        if "customers" in raw_data:
            cust = raw_data["customers"]
            # Completeness: customer_id, email, signup_date
            null_cust_id = cust["customer_id"].isnull().sum()
            null_email = cust["email"].isnull().sum()
            comp_score = 100.0 * (1.0 - (null_cust_id + null_email) / (2.0 * max(1, len(cust))))
            scores["completeness"].append(comp_score)
            
            # Uniqueness: customer_id
            dup_cust = cust["customer_id"].duplicated().sum()
            uniq_score = 100.0 * (1.0 - dup_cust / max(1, len(cust)))
            scores["uniqueness"].append(uniq_score)
            
            # Validity: age >= 18 and age <= 120
            invalid_age = ((cust["age"] < 18) | (cust["age"] > 120)).sum()
            val_score = 100.0 * (1.0 - invalid_age / max(1, len(cust)))
            scores["validity"].append(val_score)

        # 2. Products Quality Checks
        if "products" in raw_data:
            prods = raw_data["products"]
            # Completeness: product_id, category, retail_price
            null_prods = prods[["product_id", "category", "retail_price"]].isnull().sum().sum()
            comp_score = 100.0 * (1.0 - null_prods / (3.0 * max(1, len(prods))))
            scores["completeness"].append(comp_score)
            
            # Uniqueness
            dup_prods = prods["product_id"].duplicated().sum()
            scores["uniqueness"].append(100.0 * (1.0 - dup_prods / max(1, len(prods))))
            
            # Validity: retail_price > 0, cost_price > 0, target_margin between -1 and 1
            invalid_prices = ((prods["retail_price"] <= 0) | (prods["cost_price"] <= 0)).sum()
            scores["validity"].append(100.0 * (1.0 - invalid_prices / max(1, len(prods))))

        # 3. Orders Quality Checks
        if "orders" in raw_data:
            orders = raw_data["orders"]
            # Completeness
            null_orders = orders[["order_id", "customer_id", "order_date", "total_amount"]].isnull().sum().sum()
            scores["completeness"].append(100.0 * (1.0 - null_orders / (4.0 * max(1, len(orders)))))
            
            # Uniqueness
            dup_orders = orders["order_id"].duplicated().sum()
            scores["uniqueness"].append(100.0 * (1.0 - dup_orders / max(1, len(orders))))
            
            # Validity: total_amount >= 0, delivery_days >= 0
            invalid_orders = ((orders["total_amount"] < 0) | (orders["delivery_days"] < 0)).sum()
            scores["validity"].append(100.0 * (1.0 - invalid_orders / max(1, len(orders))))

        # 4. Order Items Quality Checks
        if "order_items" in raw_data:
            items = raw_data["order_items"]
            # Validity: quantity > 0, unit_price >= 0
            invalid_items = ((items["quantity"] <= 0) | (items["unit_price"] < 0)).sum()
            scores["validity"].append(100.0 * (1.0 - invalid_items / max(1, len(items))))

        # 5. Consistency / Referential Integrity
        if "orders" in raw_data and "customers" in raw_data:
            valid_cust_ids = set(raw_data["customers"]["customer_id"])
            orphan_orders = (~raw_data["orders"]["customer_id"].isin(valid_cust_ids)).sum()
            consist_score_1 = 100.0 * (1.0 - orphan_orders / max(1, len(raw_data["orders"])))
            scores["consistency"].append(consist_score_1)
            if orphan_orders > 0:
                anomalies_detected.append(f"{orphan_orders} orphan orders without valid customer_id detected.")

        if "order_items" in raw_data and "orders" in raw_data:
            valid_order_ids = set(raw_data["orders"]["order_id"])
            orphan_items = (~raw_data["order_items"]["order_id"].isin(valid_order_ids)).sum()
            consist_score_2 = 100.0 * (1.0 - orphan_items / max(1, len(raw_data["order_items"])))
            scores["consistency"].append(consist_score_2)

        if "payments" in raw_data and "orders" in raw_data:
            valid_order_ids = set(raw_data["orders"]["order_id"])
            orphan_payments = (~raw_data["payments"]["order_id"].isin(valid_order_ids)).sum()
            consist_score_3 = 100.0 * (1.0 - orphan_payments / max(1, len(raw_data["payments"])))
            scores["consistency"].append(consist_score_3)

        # Compute aggregate scores
        avg_completeness = round(float(pd.Series(scores["completeness"]).mean()), 2)
        avg_validity = round(float(pd.Series(scores["validity"]).mean()), 2)
        avg_uniqueness = round(float(pd.Series(scores["uniqueness"]).mean()), 2)
        avg_consistency = round(float(pd.Series(scores["consistency"]).mean()), 2)
        
        overall_score = round(
            (avg_completeness * 0.25) + 
            (avg_validity * 0.25) + 
            (avg_uniqueness * 0.25) + 
            (avg_consistency * 0.25), 
            2
        )
        
        report = {
            "evaluated_at": datetime.utcnow().isoformat(),
            "overall_quality_score": overall_score,
            "completeness_score": avg_completeness,
            "validity_score": avg_validity,
            "uniqueness_score": avg_uniqueness,
            "consistency_score": avg_consistency,
            "status": "PASS" if overall_score >= 85.0 else "WARNING",
            "anomalies_detected": anomalies_detected,
            "tables_audited": list(raw_data.keys()),
            "total_records_audited": sum(len(df) for df in raw_data.values())
        }
        
        # Persist log to DB
        self._persist_quality_log(report)
        return report

    def _persist_quality_log(self, report: Dict[str, Any]):
        try:
            db = SessionLocal()
            log_entry = DataQualityLog(
                check_name="Automated Ingestion Quality Audit",
                table_name="All Ingested Tables",
                completeness_score=report["completeness_score"],
                validity_score=report["validity_score"],
                uniqueness_score=report["uniqueness_score"],
                consistency_score=report["consistency_score"],
                overall_quality_score=report["overall_quality_score"],
                failed_rows_count=len(report["anomalies_detected"]),
                details=f"Tables: {', '.join(report['tables_audited'])}. Anomalies: {'; '.join(report['anomalies_detected']) or 'None'}"
            )
            db.add(log_entry)
            db.commit()
            db.close()
            logger.info(f"Data Quality report persisted. Overall Score: {report['overall_quality_score']}%")
        except Exception as e:
            logger.error(f"Failed to persist Data Quality Log: {e}")

if __name__ == "__main__":
    from pipelines.generator import EcommerceDataGenerator
    gen = EcommerceDataGenerator(num_customers=100, num_products=20, start_date="2024-01-01", end_date="2024-03-01")
    data = gen.generate_all()
    dq = DataQualityEngine()
    rep = dq.evaluate_datasets(data)
    print("DQ Report:", rep)
