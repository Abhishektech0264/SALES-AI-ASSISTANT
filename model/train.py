import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

df = pd.read_csv("../data/sales_data.csv")
df["date"] = pd.to_datetime(df["date"])

df["month"] = df["date"].dt.month
df["year"] = df["date"].dt.year

monthly_df = df.groupby(["year", "month"]).agg({
    "revenue": "sum"
}).reset_index()

monthly_df["lag_1"] = monthly_df["revenue"].shift(1)
monthly_df["lag_3"] = monthly_df["revenue"].shift(3)
monthly_df = monthly_df.dropna()

X = monthly_df[["month", "year", "lag_1", "lag_3"]]
y = monthly_df["revenue"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False
)

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)

print("MAE:", mae)

joblib.dump(model, "sales_model.pkl")
print("✅ Model saved")
