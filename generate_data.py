import pandas as pd
import numpy as np

np.random.seed(42)

dates = pd.date_range(start="2022-01-01", periods=36, freq="M")
products = ["Laptop", "Mobile", "Headphones"]
regions = ["North", "South", "East", "West"]

rows = []

for date in dates:
    for product in products:
        for region in regions:
            price = np.random.randint(5000, 60000)
            quantity = np.random.randint(20, 150)
            revenue = price * quantity

            rows.append([
                date,
                product,
                region,
                price,
                quantity,
                revenue
            ])

df = pd.DataFrame(rows, columns=[
    "date", "product", "region", "price", "quantity", "revenue"
])

df.to_csv("data/sales_data.csv", index=False)

print("✅ Sales data generated successfully")
