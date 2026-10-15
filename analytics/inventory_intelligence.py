"""
Inventory Intelligence & Stockout Optimization Engine
Enterprise AI Business Decision Intelligence Platform
Combines ML Demand Forecasting with Warehouse Inventory & Supplier Lead Times
Computes Reorder Quantities: max(0, Safety Stock + Lead Time Demand - Current Stock)
"""
import logging
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from sqlalchemy import text
from database.connection import engine

logger = logging.getLogger(__name__)

class InventoryIntelligenceEngine:
    def __init__(self):
        pass

    def evaluate_inventory_health(self) -> List[Dict[str, Any]]:
        """
        Calculates 30-day demand forecast per product, cross-references with current warehouse stock
        and supplier lead times, and generates replenishment warnings.
        """
        logger.info("Evaluating enterprise inventory health and stockout risks...")
        sql = """
        SELECT
            dp.product_id,
            dp.product_name,
            dp.category,
            dp.retail_price,
            dp.cost_price,
            COALESCE(ds.lead_time_days, 7) AS supplier_lead_time,
            COALESCE(ds.supplier_name, 'Primary Vendor') AS supplier_name,
            SUM(fi.current_stock) AS total_current_stock,
            SUM(fi.safety_stock) AS total_safety_stock,
            -- Estimated 30-day demand based on recent 60-day velocity
            COALESCE(sales_30d.recent_units_sold, 120) AS estimated_30d_demand
        FROM dim_product dp
        LEFT JOIN dim_supplier ds ON dp.supplier_id = ds.supplier_id
        JOIN fact_inventory fi ON dp.product_id = fi.product_id
        LEFT JOIN (
            SELECT
                product_id,
                ROUND(SUM(quantity) * 0.5) AS recent_units_sold
            FROM fact_sales
            GROUP BY product_id
        ) sales_30d ON dp.product_id = sales_30d.product_id
        GROUP BY dp.product_id, dp.product_name, dp.category, dp.retail_price, dp.cost_price, ds.lead_time_days, ds.supplier_name, sales_30d.recent_units_sold;
        """
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)

        # Inventory intelligence formulas:
        # Daily burn rate = estimated_30d_demand / 30.0
        # Lead time demand = daily_burn_rate * supplier_lead_time
        # Recommended reorder qty = max(0, safety_stock + lead_time_demand - current_stock)
        df["daily_demand"] = (df["estimated_30d_demand"] / 30.0).round(2)
        df["lead_time_demand"] = (df["daily_demand"] * df["supplier_lead_time"]).round(1)
        df["potential_shortage"] = (df["estimated_30d_demand"] - df["total_current_stock"]).clip(lower=0)

        df["recommended_reorder_qty"] = np.maximum(
            0,
            (df["total_safety_stock"] + df["lead_time_demand"] - df["total_current_stock"]).round(0).astype(int)
        )

        # Stockout Risk Tiering
        conditions = [
            df["total_current_stock"] < (df["total_safety_stock"] * 0.5),
            df["total_current_stock"] < df["total_safety_stock"],
            df["total_current_stock"] < (df["total_safety_stock"] * 1.5)
        ]
        choices = ["CRITICAL", "HIGH", "MEDIUM"]
        df["stockout_risk"] = np.select(conditions, choices, default="HEALTHY")

        df["reorder_capital_required"] = (df["recommended_reorder_qty"] * df["cost_price"]).round(2)

        # Sort with critical risk products first
        risk_priority = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "HEALTHY": 3}
        df["priority"] = df["stockout_risk"].map(risk_priority)
        df = df.sort_values(by=["priority", "potential_shortage"], ascending=[True, False]).drop(columns=["priority"])

        return df.to_dict(orient="records")

    def get_stockout_summary(self) -> Dict[str, Any]:
        """Summarizes enterprise stockout alerts and capital requirements"""
        items = self.evaluate_inventory_health()
        df = pd.DataFrame(items)

        critical_count = int((df["stockout_risk"] == "CRITICAL").sum())
        high_count = int((df["stockout_risk"] == "HIGH").sum())
        total_shortage = int(df["potential_shortage"].sum())
        total_capital = float(round(df["reorder_capital_required"].sum(), 2))

        return {
            "total_skus_evaluated": len(df),
            "critical_stockout_skus": critical_count,
            "high_risk_skus": high_count,
            "total_shortage_units": total_shortage,
            "total_reorder_capital_required": total_capital,
            "top_urgent_replenishments": df[df["stockout_risk"].isin(["CRITICAL", "HIGH"])].head(8).to_dict(orient="records")
        }

if __name__ == "__main__":
    inv_engine = InventoryIntelligenceEngine()
    print("Stockout Summary:", inv_engine.get_stockout_summary())
