
import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

# Product details: category, price, profit margin
products = {
    "Laptop": ("Electronics", 45000, 0.15),
    "Mobile": ("Electronics", 15000, 0.18),
    "Monitor": ("Electronics", 12000, 0.14),
    "Mouse": ("Accessories", 500, 0.25),
    "Keyboard": ("Accessories", 1000, 0.22),
    "Headphones": ("Accessories", 2000, 0.20),
    "Chair": ("Furniture", 5000, 0.16),
    "Table": ("Furniture", 10000, 0.13),
    "Sofa": ("Furniture", 25000, 0.12)
}

regions = ["West", "East", "North", "South"]

# Generate dates between January 2025 and December 2026
start_date = datetime(2025, 1, 1)
end_date = datetime(2026, 12, 31)
total_days = (end_date - start_date).days

records = []

for i in range(1000):

    product = random.choice(list(products.keys()))
    category, price, margin = products[product]

    region = random.choice(regions)

    quantity = random.randint(1, 8)

    order_date = start_date + timedelta(
        days=random.randint(0, total_days)
    )

    # Seasonal variation
    seasonal_factor = 1.15 if order_date.month in [10, 11, 12] else 1

    sales = round(quantity * price * seasonal_factor)

    actual_margin = random.uniform(margin - 0.04, margin + 0.04)
    profit = round(sales * actual_margin)

    records.append({
        "Order_ID": 2001 + i,
        "Order_Date": order_date.strftime("%Y-%m-%d"),
        "Product": product,
        "Category": category,
        "Quantity": quantity,
        "Sales": sales,
        "Profit": profit,
        "Region": region
    })

# Create DataFrame
df = pd.DataFrame(records)

# Sort by order date
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df = df.sort_values("Order_Date")

# Save dataset
df.to_csv("sales_data.csv", index=False)

print("Dataset generated successfully!")
print("Total records:", len(df))
print("\nDataset preview:")
print(df.head())

print("\nDataset information:")
print(df.info())

print("\nTotal Revenue: ₹", df["Sales"].sum())
print("Total Profit: ₹", df["Profit"].sum())
