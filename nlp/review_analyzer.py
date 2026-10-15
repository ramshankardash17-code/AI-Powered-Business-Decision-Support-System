"""
Customer Review NLP & Complaint Topic Extraction Engine
Enterprise AI Business Decision Intelligence Platform
Analyzes Sentiment (Positive, Neutral, Negative) and Maps Complaint Topics:
(product quality, delivery delay, packaging, price, customer service)
"""
import re
import logging
from typing import Dict, Any, List, Tuple
import pandas as pd
from sqlalchemy import text
from database.connection import engine

logger = logging.getLogger(__name__)

TOPIC_KEYWORDS = {
    "delivery delay": [
        "delay", "late", "transit", "shipping", "courier", "slow", "days", "tracking", "arrived late"
    ],
    "product quality": [
        "defective", "broken", "quality", "malfunction", "cheap", "damaged", "poor", "faulty", "durability", "material"
    ],
    "packaging": [
        "box", "package", "packaging", "torn", "seal", "bubble wrap", "dented", "crushed"
    ],
    "price": [
        "expensive", "price", "overpriced", "cost", "value for money", "discount", "worth", "cheap"
    ],
    "customer service": [
        "support", "service", "helpdesk", "representative", "response", "call center", "refund delay"
    ]
}

POSITIVE_WORDS = {
    "excellent", "great", "loved", "perfect", "good", "happy", "smooth", "prompt", "fantastic", "best", "satisfied"
}
NEGATIVE_WORDS = {
    "terrible", "worst", "poor", "horrible", "disappointed", "bad", "useless", "waste", "defective", "broken", "delayed"
}

class ReviewNLPAnalyzer:
    def __init__(self):
        pass

    def classify_text(self, text_content: str) -> Tuple[str, str]:
        """Classifies sentiment and dominant topic using rule-based NLP"""
        clean_text = text_content.lower()
        words = set(re.findall(r"\b\w+\b", clean_text))

        pos_count = len(words.intersection(POSITIVE_WORDS))
        neg_count = len(words.intersection(NEGATIVE_WORDS))

        if neg_count > pos_count or "disappointed" in clean_text or "not recommend" in clean_text:
            sentiment = "Negative"
        elif pos_count > neg_count:
            sentiment = "Positive"
        else:
            sentiment = "Neutral"

        # Topic extraction
        matched_topics = {}
        for topic, keywords in TOPIC_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in clean_text)
            if matches > 0:
                matched_topics[topic] = matches

        dominant_topic = max(matched_topics.items(), key=lambda x: x[1])[0] if matched_topics else "product quality"
        return sentiment, dominant_topic

    def get_sentiment_by_category(self) -> List[Dict[str, Any]]:
        """Aggregates review sentiment and top topics by product category"""
        sql = """
        SELECT
            dp.category,
            r.sentiment,
            r.topic,
            COUNT(*) AS review_count,
            ROUND(AVG(r.rating), 2) AS avg_rating
        FROM reviews r
        JOIN dim_product dp ON r.product_id = dp.product_id
        GROUP BY dp.category, r.sentiment, r.topic
        ORDER BY dp.category, review_count DESC;
        """
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)

        return df.to_dict(orient="records")

    def get_complaint_topic_summary(self) -> List[Dict[str, Any]]:
        """Summarizes complaint topics for negative and neutral reviews"""
        sql = """
        SELECT
            r.topic,
            COUNT(*) AS complaint_count,
            ROUND(AVG(r.rating), 2) AS avg_rating
        FROM reviews r
        WHERE r.sentiment IN ('Negative', 'Neutral')
        GROUP BY r.topic
        ORDER BY complaint_count DESC;
        """
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn)

        total_complaints = max(1, df["complaint_count"].sum())
        df["share_pct"] = ((df["complaint_count"] / total_complaints) * 100).round(1)
        return df.to_dict(orient="records")

if __name__ == "__main__":
    nlp = ReviewNLPAnalyzer()
    print("Complaints Summary:", nlp.get_complaint_topic_summary())
