# Inventory Management & Procurement Standard Operating Procedure (SOP-INV-2024-V2)

## 1. Safety Stock Policy & Service Level Targets
Our enterprise targets a 98.5% order fulfillment rate across core catalog items.
- **Safety Stock Formula**: Safety Stock (SS) = Z * sqrt(Lead Time * StdDev(Demand)^2 + Demand^2 * StdDev(Lead Time)^2).
- Standard policy dictates that high-velocity SKUs (Tier A) must maintain a minimum buffer equal to **1.5 times the 30-day average demand variance**.

## 2. Reorder Trigger & Automated Replenishment
A reorder trigger occurs when:
`Current Physical Inventory + Stock in Transit <= Reorder Level (ROL)`
Where:
`Reorder Level = (Daily Average Demand * Supplier Lead Time Days) + Safety Stock`

Recommended reorder quantity is defined as:
`Recommended Reorder Quantity = Safety Stock * 2 - Current Physical Stock`

## 3. Stockout Escalation Protocols
- **Critical Shortage**: Triggered when stock falls below 50% of minimum safety stock. The Supply Chain Director receives an automated alert, and emergency air-freight expedited procurement is authorized.
- **Lost Sales Accounting**: In the event of an out-of-stock condition on priority items (such as flagship electronics like HyperView 4K OLED / Product X), procurement must initiate secondary vendor allocation within 48 hours.
