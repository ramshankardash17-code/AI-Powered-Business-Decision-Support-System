"""
Realistic Multi-Year Synthetic E-Commerce Data Generator
Enterprise AI Business Decision Intelligence Platform
"""
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Tuple
from config.settings import settings

# Set seed for reproducible realistic patterns
np.random.seed(42)
random.seed(42)

REGIONS = ["North", "South", "East", "West", "Central"]
CITIES = {
    "North": ["Delhi", "Noida", "Gurugram", "Jaipur", "Chandigarh", "Lucknow"],
    "South": ["Bengaluru", "Chennai", "Hyderabad", "Kochi", "Coimbatore"],
    "East": ["Kolkata", "Bhubaneswar", "Patna", "Guwahati", "Ranchi"],
    "West": ["Mumbai", "Pune", "Ahmedabad", "Surat", "Nagpur"],
    "Central": ["Bhopal", "Indore", "Raipur", "Gwalior", "Jabalpur"]
}

CATEGORIES = {
    "Electronics": {
        "subcategories": ["Smartphones", "Laptops", "Audio & Headphones", "Smartwatches", "Cameras"],
        "base_price_range": (3000, 85000),
        "return_propensity": 0.14,
        "margin_range": (0.12, 0.22)
    },
    "Apparel": {
        "subcategories": ["Men's Wear", "Women's Wear", "Footwear", "Ethnic Wear", "Activewear"],
        "base_price_range": (500, 4500),
        "return_propensity": 0.22, # High return rate due to size/fit
        "margin_range": (0.35, 0.55)
    },
    "Home & Kitchen": {
        "subcategories": ["Cookware", "Home Decor", "Small Appliances", "Bedding", "Furniture"],
        "base_price_range": (800, 15000),
        "return_propensity": 0.08,
        "margin_range": (0.28, 0.45)
    },
    "Beauty & Personal Care": {
        "subcategories": ["Skincare", "Haircare", "Fragrances", "Cosmetics", "Wellness"],
        "base_price_range": (300, 3500),
        "return_propensity": 0.04,
        "margin_range": (0.45, 0.65)
    },
    "Sports & Fitness": {
        "subcategories": ["Gym Equipment", "Yoga & Pilates", "Sporting Goods", "Supplements", "Outdoor Gear"],
        "base_price_range": (600, 22000),
        "return_propensity": 0.09,
        "margin_range": (0.25, 0.40)
    }
}

PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash on Delivery"]
CHANNELS = ["Google Search", "Meta Ads", "Email Newsletter", "Influencer Marketing", "Affiliate"]

class EcommerceDataGenerator:
    def __init__(
        self, 
        num_customers: int = 1500, 
        num_products: int = 120, 
        start_date: str = "2023-01-01", 
        end_date: str = "2025-12-31"
    ):
        self.num_customers = num_customers
        self.num_products = num_products
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")
        self.total_days = (self.end_date - self.start_date).days

    def generate_suppliers(self, n: int = 12) -> pd.DataFrame:
        suppliers = []
        for i in range(1, n + 1):
            region = random.choice(REGIONS)
            suppliers.append({
                "supplier_id": f"SUP_{i:03d}",
                "supplier_name": f"Apex Supply Group {i}",
                "contact_email": f"partner{i}@apexsupply.com",
                "region": region,
                "city": random.choice(CITIES[region]),
                "reliability_score": round(random.uniform(0.78, 0.99), 3),
                "lead_time_days": random.randint(3, 14),
                "contract_status": "Active"
            })
        return pd.DataFrame(suppliers)

    def generate_warehouses(self) -> pd.DataFrame:
        warehouses = [
            {"warehouse_id": "WH_MUM_01", "name": "West Hub Mumbai", "city": "Mumbai", "region": "West", "capacity_sqft": 150000},
            {"warehouse_id": "WH_DEL_02", "name": "North Hub Delhi", "city": "Delhi", "region": "North", "capacity_sqft": 180000},
            {"warehouse_id": "WH_BLR_03", "name": "South Hub Bengaluru", "city": "Bengaluru", "region": "South", "capacity_sqft": 160000},
            {"warehouse_id": "WH_KOL_04", "name": "East Hub Kolkata", "city": "Kolkata", "region": "East", "capacity_sqft": 110000},
            {"warehouse_id": "WH_IND_05", "name": "Central Hub Indore", "city": "Indore", "region": "Central", "capacity_sqft": 90000},
        ]
        return pd.DataFrame(warehouses)

    def generate_products(self, suppliers_df: pd.DataFrame) -> pd.DataFrame:
        products = []
        supplier_ids = suppliers_df["supplier_id"].tolist()
        
        prod_idx = 1
        for category, cat_data in CATEGORIES.items():
            subcats = cat_data["subcategories"]
            for subcat in subcats:
                # 4 products per subcategory
                for p_num in range(1, 5):
                    price_min, price_max = cat_data["base_price_range"]
                    margin_min, margin_max = cat_data["margin_range"]
                    
                    price = round(random.uniform(price_min, price_max), -1)
                    if price < 500:
                        price = max(199.0, price)
                    margin = random.uniform(margin_min, margin_max)
                    cost_price = round(price * (1.0 - margin), 2)
                    
                    # Specific flagged product for root cause demo: Product P_015 (High tech item with supply constraints)
                    is_problem_product = (prod_idx == 15)
                    
                    products.append({
                        "product_id": f"PROD_{prod_idx:04d}",
                        "name": f"{subcat} Elite Series {p_num}" if not is_problem_product else "HyperView Ultra 4K Smart OLED (Product X)",
                        "category": category,
                        "subcategory": subcat,
                        "retail_price": price,
                        "cost_price": cost_price,
                        "target_margin": round(margin, 3),
                        "supplier_id": random.choice(supplier_ids),
                        "weight_kg": round(random.uniform(0.2, 12.0), 2),
                        "return_propensity": 0.28 if is_problem_product else cat_data["return_propensity"],
                        "reorder_point": 100,
                        "is_active": True
                    })
                    prod_idx += 1
                    if prod_idx > self.num_products:
                        break
        return pd.DataFrame(products)

    def generate_customers(self) -> pd.DataFrame:
        customers = []
        genders = ["Male", "Female", "Non-Binary"]
        
        for i in range(1, self.num_customers + 1):
            region = random.choice(REGIONS)
            city = random.choice(CITIES[region])
            
            # Signup date distributed across historical window
            signup_days = random.randint(0, int(self.total_days * 0.75))
            signup_date = self.start_date + timedelta(days=signup_days)
            
            # Persona: 15% VIP High-Value, 25% Frequent buyers, 40% Casual, 20% Discount Seekers
            persona_rand = random.random()
            if persona_rand < 0.15:
                persona = "VIP"
                avg_basket = random.uniform(8000, 35000)
                freq_weight = 4.5
            elif persona_rand < 0.40:
                persona = "Loyal"
                avg_basket = random.uniform(3000, 12000)
                freq_weight = 2.8
            elif persona_rand < 0.80:
                persona = "Casual"
                avg_basket = random.uniform(1000, 5000)
                freq_weight = 1.0
            else:
                persona = "Discount Hunter"
                avg_basket = random.uniform(800, 4000)
                freq_weight = 1.5

            customers.append({
                "customer_id": f"CUST_{i:05d}",
                "first_name": f"Customer_{i}",
                "last_name": f"User_{i}",
                "email": f"user{i}@enterprise-commerce.io",
                "phone": f"+91-{random.randint(7000000000, 9999999999)}",
                "gender": random.choice(genders),
                "age": random.randint(18, 68),
                "region": region,
                "city": city,
                "persona": persona,
                "expected_basket": avg_basket,
                "order_freq_weight": freq_weight,
                "signup_date": signup_date.strftime("%Y-%m-%d"),
                "is_active": True
            })
        return pd.DataFrame(customers)

    def generate_marketing_campaigns(self) -> pd.DataFrame:
        campaigns = []
        camp_id = 1
        current_date = self.start_date
        
        while current_date < self.end_date:
            channel = random.choice(CHANNELS)
            duration_days = random.randint(7, 30)
            end_camp = min(current_date + timedelta(days=duration_days), self.end_date)
            
            spend = round(random.uniform(15000, 180000), 2)
            cpc = random.uniform(5.0, 25.0)
            clicks = int(spend / cpc)
            impressions = int(clicks / random.uniform(0.015, 0.055))
            conv_rate = random.uniform(0.02, 0.065)
            conversions = int(clicks * conv_rate)
            attributed_rev = round(conversions * random.uniform(1800, 6500), 2)
            roi = round((attributed_rev - spend) / spend, 3)

            campaigns.append({
                "campaign_id": f"CAMP_{camp_id:04d}",
                "campaign_name": f"{channel} Push - {current_date.strftime('%b %Y')}",
                "channel": channel,
                "start_date": current_date.strftime("%Y-%m-%d"),
                "end_date": end_camp.strftime("%Y-%m-%d"),
                "spend": spend,
                "impressions": impressions,
                "clicks": clicks,
                "conversions": conversions,
                "attributed_revenue": attributed_rev,
                "roi": roi
            })
            camp_id += 1
            current_date += timedelta(days=random.randint(5, 15))
        return pd.DataFrame(campaigns)

    def generate_orders_and_items(
        self, 
        customers_df: pd.DataFrame, 
        products_df: pd.DataFrame, 
        warehouses_df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        orders = []
        order_items = []
        payments = []
        returns = []
        reviews = []
        
        customer_records = customers_df.to_dict(orient="records")
        product_records = products_df.to_dict(orient="records")
        warehouse_ids = warehouses_df["warehouse_id"].tolist()
        
        order_counter = 1
        item_counter = 1
        return_counter = 1
        review_counter = 1
        
        # Iterate day by day to inject realistic seasonality and shock events
        current_date = self.start_date
        while current_date <= self.end_date:
            month = current_date.month
            day_of_week = current_date.weekday()
            
            # Base daily orders
            daily_multiplier = 1.0
            
            # Weekend lift
            if day_of_week in [5, 6]:
                daily_multiplier *= 1.3
                
            # Q4 Holiday / Festive Season (Oct - Dec)
            if month in [10, 11, 12]:
                daily_multiplier *= 1.85
                
            # Summer sale (May)
            elif month == 5:
                daily_multiplier *= 1.4
                
            # Simulate a realistic business shock: in Nov-Dec 2024, Product X (PROD_0015) experienced a severe stockout
            # and overall Electronics return rates spiked due to a batch quality issue
            is_shock_period = (current_date.year == 2024 and current_date.month in [10, 11])
            
            num_daily_orders = int(np.random.poisson(lam=28 * daily_multiplier))
            
            for _ in range(num_daily_orders):
                cust = random.choice(customer_records)
                cust_signup = datetime.strptime(cust["signup_date"], "%Y-%m-%d")
                if current_date < cust_signup:
                    continue
                
                # Check churn probability: if customer experienced recent delivery delay, they order less
                order_id = f"ORD_{order_counter:07d}"
                order_status = "Completed"
                
                # Number of items in order
                num_items = np.random.choice([1, 2, 3, 4, 5], p=[0.45, 0.30, 0.15, 0.07, 0.03])
                order_products = random.sample(product_records, k=min(num_items, len(product_records)))
                
                order_gross = 0.0
                order_discount = 0.0
                order_has_return = False
                
                delivery_days = random.randint(2, 9)
                # Introduce delivery delay shock in Central/South in late 2024
                if is_shock_period and cust["region"] in ["South", "Central"]:
                    delivery_days += random.randint(3, 8)
                
                shipping_fee = 0.0 if cust["persona"] == "VIP" else (99.0 if order_gross < 1000 else 0.0)
                
                for prod in order_products:
                    # Stockout check: If Product X during shock period, reduce fulfilled quantity or skip
                    if prod["product_id"] == "PROD_0015" and is_shock_period and random.random() < 0.65:
                        continue # Stockout! Lost sales
                    
                    qty = np.random.choice([1, 2, 3], p=[0.82, 0.14, 0.04])
                    unit_price = prod["retail_price"]
                    
                    # Discount rate
                    disc_rate = 0.0
                    if cust["persona"] == "Discount Hunter":
                        disc_rate = random.choice([0.15, 0.20, 0.25, 0.30])
                    elif month in [10, 11, 12]:
                        disc_rate = random.choice([0.05, 0.10, 0.15, 0.20])
                    elif random.random() < 0.25:
                        disc_rate = random.choice([0.05, 0.10])
                        
                    item_discount = round(unit_price * qty * disc_rate, 2)
                    item_total = round((unit_price * qty) - item_discount, 2)
                    item_cost = round(prod["cost_price"] * qty, 2)
                    item_profit = round(item_total - item_cost, 2)
                    
                    order_gross += (unit_price * qty)
                    order_discount += item_discount
                    
                    order_items.append({
                        "order_item_id": f"ITEM_{item_counter:08d}",
                        "order_id": order_id,
                        "product_id": prod["product_id"],
                        "quantity": qty,
                        "unit_price": unit_price,
                        "unit_cost": prod["cost_price"],
                        "discount_amount": item_discount,
                        "total_amount": item_total,
                        "profit_amount": item_profit
                    })
                    item_counter += 1
                    
                    # Return logic
                    p_return = prod["return_propensity"]
                    if is_shock_period and prod["category"] == "Electronics":
                        p_return *= 1.7 # Surge in returns during the problem period
                    if delivery_days > 6:
                        p_return *= 1.35
                        
                    if random.random() < p_return:
                        order_has_return = True
                        reason = random.choice([
                            "Defective product / malfunction",
                            "Size / fit not as expected",
                            "Late delivery - no longer needed",
                            "Product different from description",
                            "Damaged in transit",
                            "Found better price elsewhere"
                        ])
                        returns.append({
                            "return_id": f"RET_{return_counter:06d}",
                            "order_id": order_id,
                            "product_id": prod["product_id"],
                            "customer_id": cust["customer_id"],
                            "return_date": (current_date + timedelta(days=random.randint(3, 14))).strftime("%Y-%m-%d"),
                            "reason": reason,
                            "refund_amount": item_total,
                            "status": "Approved"
                        })
                        return_counter += 1

                if order_gross == 0:
                    continue # Empty order due to stockouts
                    
                final_order_total = round(order_gross - order_discount + shipping_fee, 2)
                wh_id = random.choice(warehouse_ids)
                
                orders.append({
                    "order_id": order_id,
                    "customer_id": cust["customer_id"],
                    "order_date": current_date.strftime("%Y-%m-%d"),
                    "total_amount": final_order_total,
                    "discount_amount": order_discount,
                    "shipping_fee": shipping_fee,
                    "warehouse_id": wh_id,
                    "delivery_days": delivery_days,
                    "status": "Returned" if (order_has_return and random.random() < 0.3) else "Delivered",
                    "region": cust["region"],
                    "city": cust["city"]
                })
                
                # Payment
                payments.append({
                    "payment_id": f"PAY_{order_counter:07d}",
                    "order_id": order_id,
                    "payment_method": random.choice(PAYMENT_METHODS),
                    "amount": final_order_total,
                    "payment_status": "Success" if random.random() < 0.985 else "Failed",
                    "payment_date": current_date.strftime("%Y-%m-%d")
                })
                
                # Reviews (35% of orders generate a review)
                if random.random() < 0.35 and order_products:
                    rev_prod = random.choice(order_products)
                    # Rating correlates with delivery delay and return
                    if order_has_return or delivery_days > 7:
                        rating = random.choice([1, 2, 2, 3])
                    elif cust["persona"] == "VIP":
                        rating = random.choice([4, 5, 5])
                    else:
                        rating = random.choice([1, 2, 3, 4, 4, 5, 5, 5])
                        
                    if rating <= 2:
                        sentiment = "Negative"
                        topic = random.choice(["product quality", "delivery delay", "packaging", "customer service"])
                        text = f"Very disappointed with the {rev_prod['name']}. Issue with {topic}. Would not recommend."
                    elif rating == 3:
                        sentiment = "Neutral"
                        topic = "price"
                        text = f"Decent quality for {rev_prod['name']}, but delivery took {delivery_days} days."
                    else:
                        sentiment = "Positive"
                        topic = "product quality"
                        text = f"Excellent {rev_prod['name']}! Works as advertised, very pleased with prompt delivery."
                        
                    reviews.append({
                        "review_id": f"REV_{review_counter:07d}",
                        "order_id": order_id,
                        "product_id": rev_prod["product_id"],
                        "customer_id": cust["customer_id"],
                        "rating": rating,
                        "sentiment": sentiment,
                        "topic": topic,
                        "review_text": text,
                        "review_date": (current_date + timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%d")
                    })
                    review_counter += 1

                order_counter += 1
            
            current_date += timedelta(days=1)
            
        return (
            pd.DataFrame(orders), 
            pd.DataFrame(order_items), 
            pd.DataFrame(payments), 
            pd.DataFrame(returns), 
            pd.DataFrame(reviews)
        )

    def generate_inventory(self, products_df: pd.DataFrame, warehouses_df: pd.DataFrame) -> pd.DataFrame:
        inventory = []
        inv_id = 1
        for _, prod in products_df.iterrows():
            for _, wh in warehouses_df.iterrows():
                # For Product X, simulate current critical stock shortage
                if prod["product_id"] == "PROD_0015":
                    stock = random.randint(15, 60) # Understocked!
                    safety_stock = 350
                else:
                    stock = random.randint(120, 1800)
                    safety_stock = random.randint(80, 250)
                    
                reorder_qty = max(0, (safety_stock * 2) - stock)
                
                inventory.append({
                    "inventory_id": f"INV_{inv_id:06d}",
                    "product_id": prod["product_id"],
                    "warehouse_id": wh["warehouse_id"],
                    "current_stock": stock,
                    "safety_stock": safety_stock,
                    "reorder_level": int(safety_stock * 1.5),
                    "recommended_reorder_qty": reorder_qty if stock < safety_stock * 1.5 else 0,
                    "last_restocked_date": (datetime.now() - timedelta(days=random.randint(3, 45))).strftime("%Y-%m-%d")
                })
                inv_id += 1
        return pd.DataFrame(inventory)

    def generate_all(self) -> Dict[str, pd.DataFrame]:
        print("Generating suppliers & warehouses...")
        suppliers_df = self.generate_suppliers()
        warehouses_df = self.generate_warehouses()
        
        print("Generating products & customers...")
        products_df = self.generate_products(suppliers_df)
        customers_df = self.generate_customers()
        
        print("Generating marketing campaigns...")
        marketing_df = self.generate_marketing_campaigns()
        
        print(f"Generating multi-year orders from {self.start_date.date()} to {self.end_date.date()}...")
        orders_df, order_items_df, payments_df, returns_df, reviews_df = self.generate_orders_and_items(
            customers_df, products_df, warehouses_df
        )
        
        print("Generating inventory snapshots...")
        inventory_df = self.generate_inventory(products_df, warehouses_df)
        
        datasets = {
            "suppliers": suppliers_df,
            "warehouses": warehouses_df,
            "products": products_df,
            "customers": customers_df,
            "marketing_campaigns": marketing_df,
            "orders": orders_df,
            "order_items": order_items_df,
            "payments": payments_df,
            "returns": returns_df,
            "reviews": reviews_df,
            "inventory": inventory_df
        }
        
        # Save raw CSVs to data/raw
        raw_dir = settings.DATA_DIR / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        for name, df in datasets.items():
            csv_path = raw_dir / f"{name}.csv"
            df.to_csv(csv_path, index=False)
            print(f"Saved {name}: {len(df):,} rows -> {csv_path}")
            
        return datasets

if __name__ == "__main__":
    generator = EcommerceDataGenerator()
    datasets = generator.generate_all()
    print("Synthetic data generation completed successfully!")
