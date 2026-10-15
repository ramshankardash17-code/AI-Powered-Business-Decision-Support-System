"""
Automated Modular ETL/ELT Pipeline
Enterprise AI Business Decision Intelligence Platform
Ingests Raw Data -> Performs Data Quality Validation -> Cleans & Transforms
-> Loads OLTP Layer -> Populates Star Schema -> Builds ML Feature Store
"""
import logging
from datetime import datetime
from typing import Dict, Any
import numpy as np
import pandas as pd
from sqlalchemy import text
from config.settings import settings
from database.connection import engine, SessionLocal, Base, DB_DIALECT
from database.models import (
    Supplier, Warehouse, Product, Customer, Order, OrderItem,
    Payment, Return, Review, Inventory, MarketingCampaign,
    DimCustomer, DimProduct, DimDate, DimLocation, DimSupplier, DimMarketingChannel,
    FactSales, FactOrders, FactReturns, FactInventory, FactMarketing,
    CustomerMLFeatures
)
from pipelines.generator import EcommerceDataGenerator
from pipelines.data_quality import DataQualityEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ETL_Pipeline")

class ETLPipeline:
    def __init__(self):
        self.dq_engine = DataQualityEngine()
        self.run_metadata = {}

    def run_pipeline(self, force_regenerate: bool = False) -> Dict[str, Any]:
        """Runs the end-to-end automated ETL pipeline"""
        start_time = datetime.utcnow()
        logger.info(f"=== Starting ETL Pipeline Run at {start_time.isoformat()} ===")
        self.run_metadata["start_time"] = start_time.isoformat()
        
        try:
            # 1. Initialize Tables in Database
            logger.info(f"Initializing database schemas on target dialect: {DB_DIALECT}...")
            Base.metadata.create_all(bind=engine)
            
            # 2. Extract / Load Raw Data
            raw_dir = settings.DATA_DIR / "raw"
            raw_files_exist = raw_dir.exists() and (raw_dir / "orders.csv").exists()
            
            if not raw_files_exist or force_regenerate:
                logger.info("Raw data missing or regeneration requested. Running synthetic data generator...")
                generator = EcommerceDataGenerator()
                raw_data = generator.generate_all()
            else:
                logger.info("Loading existing raw datasets from CSV...")
                raw_data = {
                    "suppliers": pd.read_csv(raw_dir / "suppliers.csv"),
                    "warehouses": pd.read_csv(raw_dir / "warehouses.csv"),
                    "products": pd.read_csv(raw_dir / "products.csv"),
                    "customers": pd.read_csv(raw_dir / "customers.csv"),
                    "marketing_campaigns": pd.read_csv(raw_dir / "marketing_campaigns.csv"),
                    "orders": pd.read_csv(raw_dir / "orders.csv"),
                    "order_items": pd.read_csv(raw_dir / "order_items.csv"),
                    "payments": pd.read_csv(raw_dir / "payments.csv"),
                    "returns": pd.read_csv(raw_dir / "returns.csv"),
                    "reviews": pd.read_csv(raw_dir / "reviews.csv"),
                    "inventory": pd.read_csv(raw_dir / "inventory.csv")
                }

            # 3. Data Quality Gate
            logger.info("Executing Data Quality Validation Gate...")
            dq_report = self.dq_engine.evaluate_datasets(raw_data)
            self.run_metadata["data_quality"] = dq_report
            if dq_report["overall_quality_score"] < settings.DATA_QUALITY_THRESHOLD:
                logger.warning(
                    f"Data Quality Score {dq_report['overall_quality_score']}% is below threshold {settings.DATA_QUALITY_THRESHOLD}%."
                )

            # 4. Load OLTP Layer
            logger.info("Loading operational data into OLTP tables...")
            self._load_oltp_tables(raw_data)

            # 5. Build and Populate Star Schema
            logger.info("Transforming OLTP data into Star Schema Dimensional Model...")
            self._populate_star_schema(raw_data)

            # 6. Feature Store Engineering
            logger.info("Generating customer ML features and persisting to Feature Store...")
            self._generate_ml_feature_store(raw_data)

            end_time = datetime.utcnow()
            duration_secs = (end_time - start_time).total_seconds()
            self.run_metadata["end_time"] = end_time.isoformat()
            self.run_metadata["duration_seconds"] = duration_secs
            self.run_metadata["status"] = "SUCCESS"
            logger.info(f"=== ETL Pipeline Completed Successfully in {duration_secs:.2f} seconds ===")
            return self.run_metadata

        except Exception as e:
            logger.error(f"ETL Pipeline execution failed: {e}", exc_info=True)
            self.run_metadata["status"] = "FAILED"
            self.run_metadata["error"] = str(e)
            raise e

    def _load_oltp_tables(self, raw_data: Dict[str, pd.DataFrame]):
        """Bulk loads cleaned records into OLTP tables with fast chunking"""
        table_mapping = [
            ("suppliers", "suppliers"),
            ("warehouses", "warehouses"),
            ("products", "products"),
            ("customers", "customers"),
            ("orders", "orders"),
            ("order_items", "order_items"),
            ("payments", "payments"),
            ("returns", "returns"),
            ("reviews", "reviews"),
            ("inventory", "inventory"),
            ("marketing_campaigns", "marketing_campaigns")
        ]
        
        for key, tbl_name in table_mapping:
            df = raw_data[key].copy()
            # Fast to_sql with if_exists='replace'
            df.to_sql(tbl_name, con=engine, if_exists="replace", index=False, chunksize=1000)
            logger.info(f"Loaded {len(df):,} rows into OLTP table '{tbl_name}'")

    def _populate_star_schema(self, raw_data: Dict[str, pd.DataFrame]):
        """Populates Dimensions and Fact tables for BI and Analytics"""
        # A. Dim Date
        orders = raw_data["orders"]
        min_date = pd.to_datetime(orders["order_date"].min())
        max_date = pd.to_datetime(orders["order_date"].max())
        date_range = pd.date_range(min_date, max_date)
        
        dim_dates = []
        for d in date_range:
            dim_dates.append({
                "date_key": int(d.strftime("%Y%m%d")),
                "full_date": d.strftime("%Y-%m-%d"),
                "day": d.day,
                "month": d.month,
                "month_name": d.strftime("%B"),
                "quarter": d.quarter,
                "year": d.year,
                "day_of_week": d.weekday(),
                "day_name": d.strftime("%A"),
                "is_weekend": d.weekday() in [5, 6],
                "is_festive_season": d.month in [10, 11, 12]
            })
        dim_date_df = pd.DataFrame(dim_dates)
        dim_date_df.to_sql("dim_date", con=engine, if_exists="replace", index=False)
        logger.info(f"Loaded {len(dim_date_df):,} rows into 'dim_date'")

        # B. Dim Customer
        cust = raw_data["customers"].copy()
        dim_cust = pd.DataFrame({
            "customer_id": cust["customer_id"],
            "full_name": cust["first_name"] + " " + cust["last_name"],
            "email": cust["email"],
            "gender": cust["gender"],
            "age_group": pd.cut(cust["age"], bins=[0, 25, 40, 55, 100], labels=["18-25", "26-40", "41-55", "55+"]).astype(str),
            "region": cust["region"],
            "city": cust["city"],
            "signup_date": cust["signup_date"],
            "customer_segment": cust["persona"]
        })
        dim_cust.to_sql("dim_customer", con=engine, if_exists="replace", index=False)
        logger.info(f"Loaded {len(dim_cust):,} rows into 'dim_customer'")

        # C. Dim Product
        prods = raw_data["products"].copy()
        dim_prod = pd.DataFrame({
            "product_id": prods["product_id"],
            "product_name": prods["name"],
            "category": prods["category"],
            "subcategory": prods["subcategory"],
            "retail_price": prods["retail_price"],
            "cost_price": prods["cost_price"],
            "target_margin": prods["target_margin"],
            "supplier_id": prods["supplier_id"]
        })
        dim_prod.to_sql("dim_product", con=engine, if_exists="replace", index=False)
        logger.info(f"Loaded {len(dim_prod):,} rows into 'dim_product'")

        # D. Dim Location
        cities = cust[["city", "region"]].drop_duplicates().copy()
        cities["tier"] = np.where(cities["city"].isin(["Mumbai", "Delhi", "Bengaluru", "Kolkata", "Chennai", "Hyderabad"]), "Tier 1", "Tier 2")
        cities.to_sql("dim_location", con=engine, if_exists="replace", index=False)

        # E. Dim Supplier
        supp = raw_data["suppliers"].copy()
        supp.to_sql("dim_supplier", con=engine, if_exists="replace", index=False)

        # F. Dim Marketing Channel
        channels_df = pd.DataFrame({
            "channel_name": ["Google Search", "Meta Ads", "Email Newsletter", "Influencer Marketing", "Affiliate"],
            "channel_type": ["Paid Search", "Paid Social", "Owned Retention", "Influencer", "Affiliate"]
        })
        channels_df.to_sql("dim_marketing_channel", con=engine, if_exists="replace", index=False)

        # G. Fact Sales
        items = raw_data["order_items"].copy()
        orders_sub = orders[["order_id", "customer_id", "order_date", "region"]].copy()
        fact_sales = items.merge(orders_sub, on="order_id", how="inner")
        fact_sales["date_key"] = pd.to_datetime(fact_sales["order_date"]).dt.strftime("%Y%m%d").astype(int)
        fact_sales["gross_sales"] = fact_sales["unit_price"] * fact_sales["quantity"]
        fact_sales["net_sales"] = fact_sales["total_amount"]
        fact_sales["cogs"] = fact_sales["unit_cost"] * fact_sales["quantity"]
        fact_sales["profit"] = fact_sales["profit_amount"]
        fact_sales["profit_margin"] = (fact_sales["profit"] / fact_sales["net_sales"]).round(4)
        
        cols_fact_sales = [
            "order_item_id", "order_id", "date_key", "customer_id", "product_id", 
            "region", "quantity", "gross_sales", "discount_amount", "net_sales", "cogs", "profit", "profit_margin"
        ]
        fact_sales[cols_fact_sales].to_sql("fact_sales", con=engine, if_exists="replace", index=False, chunksize=1000)
        logger.info(f"Loaded {len(fact_sales):,} rows into 'fact_sales'")

        # H. Fact Orders
        fact_orders = orders.copy()
        fact_orders["date_key"] = pd.to_datetime(fact_orders["order_date"]).dt.strftime("%Y%m%d").astype(int)
        fact_orders["is_returned"] = fact_orders["status"] == "Returned"
        cols_fact_orders = [
            "order_id", "date_key", "customer_id", "warehouse_id", "region",
            "total_amount", "discount_amount", "shipping_fee", "delivery_days", "is_returned", "status"
        ]
        fact_orders[cols_fact_orders].to_sql("fact_orders", con=engine, if_exists="replace", index=False, chunksize=1000)
        logger.info(f"Loaded {len(fact_orders):,} rows into 'fact_orders'")

        # I. Fact Returns
        rets = raw_data["returns"].copy()
        rets["date_key"] = pd.to_datetime(rets["return_date"]).dt.strftime("%Y%m%d").astype(int)
        cols_fact_returns = ["return_id", "order_id", "product_id", "customer_id", "date_key", "refund_amount", "reason"]
        rets[cols_fact_returns].to_sql("fact_returns", con=engine, if_exists="replace", index=False)
        logger.info(f"Loaded {len(rets):,} rows into 'fact_returns'")

        # J. Fact Inventory
        inv = raw_data["inventory"].copy()
        inv["date_key"] = int(datetime.utcnow().strftime("%Y%m%d"))
        inv["is_stockout_risk"] = inv["current_stock"] < inv["reorder_level"]
        inv["shortage_units"] = np.maximum(0, (inv["safety_stock"] * 2) - inv["current_stock"])
        cols_fact_inv = [
            "inventory_id", "product_id", "warehouse_id", "date_key",
            "current_stock", "safety_stock", "reorder_level", "is_stockout_risk", "shortage_units"
        ]
        inv[cols_fact_inv].to_sql("fact_inventory", con=engine, if_exists="replace", index=False)
        logger.info(f"Loaded {len(inv):,} rows into 'fact_inventory'")

        # K. Fact Marketing
        mkt = raw_data["marketing_campaigns"].copy()
        mkt["start_date_key"] = pd.to_datetime(mkt["start_date"]).dt.strftime("%Y%m%d").astype(int)
        mkt.to_sql("fact_marketing", con=engine, if_exists="replace", index=False)
        logger.info(f"Loaded {len(mkt):,} rows into 'fact_marketing'")

    def _generate_ml_feature_store(self, raw_data: Dict[str, pd.DataFrame]):
        """Calculates RFM metrics and initial customer features for Machine Learning"""
        orders = raw_data["orders"].copy()
        returns = raw_data["returns"].copy()
        reviews = raw_data["reviews"].copy()
        customers = raw_data["customers"].copy()
        
        max_date = pd.to_datetime(orders["order_date"].max())
        orders["order_dt"] = pd.to_datetime(orders["order_date"])
        
        # Customer-level aggregations
        cust_orders = orders.groupby("customer_id").agg(
            last_order_date=("order_dt", "max"),
            frequency_orders=("order_id", "count"),
            monetary_total=("total_amount", "sum"),
            avg_order_value=("total_amount", "mean"),
            avg_discount_amt=("discount_amount", "mean"),
            avg_delivery_delay=("delivery_days", "mean")
        ).reset_index()
        
        cust_orders["recency_days"] = (max_date - cust_orders["last_order_date"]).dt.days
        cust_orders["avg_discount_rate"] = (cust_orders["avg_discount_amt"] / cust_orders["avg_order_value"].replace(0, 1)).clip(0, 1).round(3)

        # Returns per customer
        cust_returns = returns.groupby("customer_id").size().reset_index(name="total_returns")
        cust_features = cust_orders.merge(cust_returns, on="customer_id", how="left").fillna({"total_returns": 0})
        cust_features["return_rate"] = (cust_features["total_returns"] / cust_features["frequency_orders"]).clip(0, 1).round(3)

        # Negative reviews per customer
        neg_reviews = reviews[reviews["sentiment"] == "Negative"].groupby("customer_id").size().reset_index(name="negative_reviews_count")
        cust_features = cust_features.merge(neg_reviews, on="customer_id", how="left").fillna({"negative_reviews_count": 0})

        # Customer tenure
        customers["signup_dt"] = pd.to_datetime(customers["signup_date"])
        cust_features = cust_features.merge(customers[["customer_id", "signup_dt"]], on="customer_id", how="left")
        cust_features["tenure_days"] = (max_date - cust_features["signup_dt"]).dt.days.clip(lower=1)

        # Basic baseline segment
        cust_features["rfm_segment"] = np.where(
            cust_features["monetary_total"] > 25000, "Champions",
            np.where(cust_features["recency_days"] > 180, "At Risk",
            np.where(cust_features["frequency_orders"] >= 6, "Loyal", "Casual"))
        )
        
        # Baseline churn probability heuristic before ML model training
        cust_features["churn_probability"] = (
            (cust_features["recency_days"] / 365.0).clip(0, 0.6) +
            (cust_features["return_rate"] * 0.2) +
            (cust_features["negative_reviews_count"] * 0.1)
        ).clip(0.05, 0.95).round(3)
        
        cust_features["churn_risk_level"] = np.where(
            cust_features["churn_probability"] >= 0.70, "High",
            np.where(cust_features["churn_probability"] >= 0.40, "Medium", "Low")
        )
        
        cust_features["predicted_clv"] = (
            cust_features["avg_order_value"] * (cust_features["frequency_orders"] / np.maximum(1, cust_features["tenure_days"] / 365.0)) * 2.5
        ).round(2)
        
        cust_features["is_high_value_high_churn"] = (
            (cust_features["monetary_total"] > 15000) & (cust_features["churn_risk_level"] == "High")
        )

        cols_to_save = [
            "customer_id", "recency_days", "frequency_orders", "monetary_total", "avg_order_value",
            "total_returns", "return_rate", "avg_discount_rate", "negative_reviews_count",
            "avg_delivery_delay", "tenure_days", "rfm_segment", "churn_probability",
            "churn_risk_level", "predicted_clv", "is_high_value_high_churn"
        ]
        
        cust_features[cols_to_save].to_sql("customer_ml_features", con=engine, if_exists="replace", index=False)
        logger.info(f"Loaded {len(cust_features):,} rows into 'customer_ml_features' feature store")

if __name__ == "__main__":
    pipeline = ETLPipeline()
    pipeline.run_pipeline(force_regenerate=True)
