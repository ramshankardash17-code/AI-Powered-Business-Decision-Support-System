"""
Alerts & Data Quality Center API Router
Enterprise AI Business Decision Intelligence Platform
"""
from fastapi import APIRouter
from sqlalchemy import text
from database.connection import engine
from ml.anomaly import BusinessAnomalyDetector
from pipelines.data_quality import DataQualityEngine
from api.schemas import StandardResponse

router = APIRouter(prefix="/api/alerts", tags=["Anomalies & Data Quality"])

@router.get("/anomalies", response_model=StandardResponse)
def get_anomaly_alerts():
    """Returns detected operational anomalies across sales, returns, and inventory"""
    sql = "SELECT * FROM anomaly_alerts ORDER BY alert_date DESC, alert_id DESC LIMIT 25;"
    with engine.connect() as conn:
        import pandas as pd
        df = pd.read_sql(text(sql), conn)
    return StandardResponse(success=True, data=df.to_dict(orient="records"))

@router.post("/anomalies/scan", response_model=StandardResponse)
def trigger_anomaly_scan():
    """Executes fresh Isolation Forest anomaly detection scan"""
    detector = BusinessAnomalyDetector()
    alerts = detector.run_anomaly_detection()
    return StandardResponse(success=True, message=f"Scan complete. {len(alerts)} alerts triggered.", data=alerts)

@router.get("/data-quality", response_model=StandardResponse)
def get_data_quality_reports():
    """Returns recent Data Quality audit logs, completeness, validity, and uniqueness scores"""
    sql = "SELECT * FROM data_quality_logs ORDER BY evaluated_at DESC LIMIT 10;"
    with engine.connect() as conn:
        import pandas as pd
        df = pd.read_sql(text(sql), conn)
    return StandardResponse(success=True, data=df.to_dict(orient="records"))
