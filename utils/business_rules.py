import pandas as pd

def get_business_insights(df, next_month_prediction):
    insights = []

    df["date"] = pd.to_datetime(df["date"])

    # 1️⃣ Recent trend (last 3 months)
    recent_sales = df.groupby("date")["revenue"].sum().tail(3).mean()

    if next_month_prediction < recent_sales:
        insights.append("⚠️ Risk Alert: Sales expected to decline next month")
    else:
        insights.append("📈 Sales trend looks positive for next month")

    # 2️⃣ High performing product
    product_growth = (
        df.groupby("product")["revenue"].sum()
        .sort_values()
        .pct_change()
    )

    if product_growth.max() > 0.2:
        top_product = product_growth.idxmax()
        insights.append(f"🔥 High performing product: {top_product}")

    # 3️⃣ Weak region
    region_sales = df.groupby("region")["revenue"].sum()
    weak_region = region_sales.idxmin()
    insights.append(f"📉 Region at risk: {weak_region}")

    return insights

