
import streamlit as st
import pandas as pd
import joblib
from datetime import datetime
import json
import hashlib
import os


# ================= AUTH SYSTEM =================
import json
USER_FILE = "user.json"

def load_user():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return None

def save_user(data):
    with open(USER_FILE, "w") as f:
        json.dump(data, f)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = None

# ================= ACTIVITY LOGGER =================
import datetime

LOG_FILE = "activity_log.json"

def load_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return []

def save_logs(logs):
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f)

def log_activity(action):
    logs = load_logs()
    logs.append({
        "user": st.session_state.get("username"),
        "action": action,
        "time": str(datetime.datetime.now())
    })
    save_logs(logs)



# ================= LOGIN =================

saved_user = load_user()

if not st.session_state.authenticated:

    st.markdown("## 🔐 Login / Register")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Continue"):

        # If no user exists → register automatically
        if saved_user is None:
            save_user({"username": username, "password": password})
            st.session_state.authenticated = True
            st.session_state.username = username
            st.success("🎉 Account created successfully!")
            st.rerun()

        # If user exists → validate
        else:
            if (
                username == saved_user["username"]
                and password == saved_user["password"]
            ):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

    st.stop()


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="BizSight AI | Learning Mode",
    page_icon="🧠",
    layout="wide"
)

# ================= UI CSS =================
st.markdown(
    """
<style>
.stApp {
    background: linear-gradient(135deg, #0a1128 0%, #03081e 100%);
    color: #e0e7ff;
}
.hero-box {
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    padding: 35px 45px;
    border-radius: 20px;
    margin-bottom: 30px;
}
.hero-title { font-size: 40px; font-weight: 800; color: white; margin-bottom: 0; }
.hero-subtitle { color: rgba(255,255,255,0.85); margin-top: 5px; }
.glass-card {
    background: rgba(255,255,255,0.04);
    padding: 25px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.12);
}
.metric-val { font-size: 40px; color: #22c55e; font-weight: 800; }
</style>
""",
    unsafe_allow_html=True,
)

# ================= MODEL =================
@st.cache_resource
def load_model():
    try:
        return joblib.load("model/sales_model.pkl")
    except Exception:
        return None

model = load_model()

# ================= SCHEMA MEMORY =================
SCHEMA_FILE = "schema_memory.json"
if not os.path.exists(SCHEMA_FILE):
    with open(SCHEMA_FILE, "w") as f:
        json.dump({}, f)


def load_schema():
    with open(SCHEMA_FILE, "r") as f:
        return json.load(f)


def save_schema(data):
    with open(SCHEMA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def schema_signature(df: pd.DataFrame) -> str:
    return hashlib.md5(
        ",".join([str(df[c].dtype) for c in df.columns]).encode()
    ).hexdigest()


def apply_schema(df: pd.DataFrame):
    memory = load_schema()
    sig = schema_signature(df)
    if sig in memory:
        return df.rename(columns=memory[sig]), True
    return df, False


# ================= SESSION =================
if "df" not in st.session_state:
    st.session_state.df = None
if "query" not in st.session_state:
    st.session_state.query = None

# ================= HERO =================
st.markdown(
    """
<div class="hero-box">
    <h1 class="hero-title">BizSight AI 🧠</h1>
    <p class="hero-subtitle">Self-Learning Sales Intelligence Platform</p>
</div>
""",
    unsafe_allow_html=True,
)
col1, col2 = st.columns([8,1])

with col2:
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

st.markdown(f"👤 Logged in as: **{st.session_state.username}**")


# ================= RESET =================
if st.button("🔄 Reset System"):
    st.session_state.clear()
    st.rerun()

# ================= DATA INPUT =================
st.markdown("## 📥 Upload Any CSV")

dataset_name = st.text_input("Enter Dataset Name to Save (optional)", placeholder="e.g. Q1_Sales")

file = st.file_uploader("Upload CSV (any format)", type=["csv"])

if file is not None:
    df_raw = pd.read_csv(file)
    required = {"date", "product", "region", "revenue"}

    df_mapped, known = apply_schema(df_raw)

    if known and required.issubset(df_mapped.columns):
        st.success("✅ Data format recognized automatically")
        df = df_mapped
    else:
        st.warning("🤖 I don’t understand this format yet. Teach me once.")

        mapping = {}
        for col in required:
            mapping[col] = st.selectbox(
                f"Which column represents '{col}'?",
                df_raw.columns,
                key=f"map_{col}",
            )

        if st.button("🧠 Teach System"):
            rename_map = {v: k for k, v in mapping.items()}
            sig = schema_signature(df_raw)
            memory = load_schema()
            memory[sig] = rename_map
            save_schema(memory)

            df = df_raw.rename(columns=rename_map)
            st.success("🎉 Learned! I’ll remember this format.")
            st.rerun()
        else:
            st.stop()

    # -------- Clean Data --------
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0)

    st.session_state.df = df

    log_activity("Uploaded new dataset")


    # -------- Manual Save Button --------
    if dataset_name:
        if st.button("💾 Save Dataset"):
            DATA_FOLDER = "saved_datasets"
            os.makedirs(DATA_FOLDER, exist_ok=True)

            save_path = os.path.join(DATA_FOLDER, dataset_name + ".csv")
            df.to_csv(save_path, index=False)

            st.success(f"Dataset saved as {dataset_name}.csv")
            log_activity(f"Saved dataset as {dataset_name}")




# ================= DATA STORAGE SYSTEM =================
os.makedirs("saved_datasets", exist_ok=True)
os.makedirs("logs", exist_ok=True)

DATA_FOLDER = "saved_datasets"
os.makedirs(DATA_FOLDER, exist_ok=True)

st.markdown("## 💾 Dataset Manager")


saved_files = os.listdir(DATA_FOLDER)

selected_dataset = st.selectbox(
    "Load Saved Dataset",
    ["None"] + saved_files
)
# -------- LOAD --------
if selected_dataset != "None":
    try:
        df_loaded = pd.read_csv(
            os.path.join(DATA_FOLDER, selected_dataset)
        )

        # SAFE TYPE CONVERSION
        df_loaded["date"] = pd.to_datetime(
            df_loaded["date"], errors="coerce"
        )

        df_loaded["revenue"] = pd.to_numeric(
            df_loaded["revenue"], errors="coerce"
        ).fillna(0)

        # REMOVE INVALID DATES
        df_loaded = df_loaded.dropna(subset=["date"])

        st.session_state.df = df_loaded

        st.success(f"Loaded dataset: {selected_dataset}")
        log_activity(f"Loaded dataset: {selected_dataset}")

    except Exception as e:
        st.error(f"Error loading dataset: {e}")


# -------- DELETE --------
if selected_dataset != "None":
    if st.button("🗑️ Delete Selected Dataset"):
        try:
            file_path = os.path.join(DATA_FOLDER, selected_dataset)

            if os.path.exists(file_path):
                os.remove(file_path)
                st.success(f"{selected_dataset} deleted successfully")
                log_activity(f"Deleted dataset: {selected_dataset}")
                st.rerun()
            else:
                st.warning("File not found.")

        except Exception as e:
            st.error(f"Error deleting dataset: {e}")


# ================= ACTIVITY HISTORY =================

st.markdown("## 📊 Activity History")

logs = load_logs()

if logs:
    df_logs = pd.DataFrame(logs[::-1])
    st.dataframe(df_logs)
else:
    st.info("No activity yet.")





# ================= STOP =================
df = st.session_state.df
if df is None:
    st.info("Upload data to continue")
    st.stop()

# ================= SUMMARY =================
st.markdown("---")
st.markdown("## 📊 Data Summary")

c1, c2, c3 = st.columns(3)
c1.metric("Total Records", len(df))
c2.metric("Total Revenue", f"₹{int(df['revenue'].sum()):,}")
c3.metric("Regions", df["region"].nunique())

with st.expander("👀 View Data"):
    st.dataframe(df, use_container_width=True)

# ================= AUTO ALERTS =================
st.markdown("## 🚨 Smart Alerts")

df_alert = df.dropna(subset=["date"]).copy()
df_alert["month"] = df_alert["date"].dt.to_period("M")

monthly_sales = (
    df_alert.groupby("month")["revenue"]
    .sum()
    .sort_index()
)

alerts = []

if len(monthly_sales) >= 2:
    last = monthly_sales.iloc[-1]
    prev = monthly_sales.iloc[-2]

    change_pct = (last - prev) / prev if prev != 0 else 0

    if change_pct < -0.2:
        alerts.append(
            f"📉 Revenue dropped {abs(change_pct)*100:.1f}% compared to last month"
        )

# ---- Region alerts ----
region_avg = df.groupby("region")["revenue"].mean()

for region, value in region_avg.items():
    if value < region_avg.mean() * 0.7:
        alerts.append(f"⚠️ Region '{region}' consistently underperforming")

# ---- Product alerts ----
product_avg = df.groupby("product")["revenue"].mean()

for prod, value in product_avg.items():
    if value < product_avg.mean() * 0.7:
        alerts.append(f"⚠️ Product '{prod}' sales are below average")

# ---- UI ----
if alerts:
    for a in alerts:
        st.warning(a)
else:
    st.success("✅ No critical alerts detected")

# ================= EXPORT REPORT =================
st.markdown("## 📤 Export Business Report")

report = {
    "Generated On": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    "Total Records": len(df),
    "Total Revenue": int(df["revenue"].sum()),
}

# Add forecast if available
if "forecast_value" in st.session_state:
    report["Forecast Month"] = st.session_state["forecast_month"]
    report["Forecast Revenue"] = st.session_state["forecast_value"]

# Add top product if available
if "top_product" in st.session_state:
    report["Top Product"] = st.session_state["top_product"]
    report["Top Product Revenue"] = st.session_state["top_product_revenue"]

# Add risk info if available
if "risk_region" in st.session_state:
    report["Risk Region"] = st.session_state["risk_region"]
    report["Risk Revenue"] = st.session_state["risk_revenue"]
    report["Risk Level"] = st.session_state["risk_level"]
    report["Suggested Action"] = st.session_state["risk_suggestion"]

report_df = pd.DataFrame(report.items(), columns=["Metric", "Value"])
st.dataframe(report_df, use_container_width=True)

csv = report_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Download Business Insight Report",
    csv,
    "bizsight_business_report.csv",
    "text/csv",
)



# ================= ACTIONS =================

st.markdown("## 💬 Ask BizSight")

user_query = st.text_input(
    "Ask a business question (e.g. top product, risk region, forecast)",
    placeholder="Type here..."
)
if user_query:
    q = user_query.lower()

    if any(k in q for k in ["forecast", "predict", "next month"]):
        st.session_state.query = "forecast"

    elif any(k in q for k in ["top", "best", "highest"]):
        st.session_state.query = "top"

    elif any(k in q for k in ["risk", "weak", "problem"]):
        st.session_state.query = "risk"

    else:
        st.warning("🤔 I couldn't understand. Try asking about forecast, top product, or risk.")

st.markdown("## ⚡ Insights")
b1, b2, b3 , b4= st.columns(4)

if b1.button("📈 Forecast Next Month"):
    st.session_state.query = "forecast"
if b2.button("🏆 Top Products"):
    st.session_state.query = "top"
if b3.button("⚠️ Risk Analysis"):
    st.session_state.query = "risk"
if b4.button("⚖️ Compare Mode"):
    st.session_state.query = "compare"

# ================= LOGIC =================
query = st.session_state.query

# ---------- FORECAST ----------
if query == "forecast":
    df_calc = df.dropna(subset=["date"]).copy()
    df_calc["month"] = df_calc["date"].dt.to_period("M").astype(str)

    monthly = (
        df_calc.groupby("month")["revenue"].sum().sort_index()
    )

    if len(monthly) == 0:
        st.error("❌ Not enough data for forecasting")
        st.stop()

    avg_rev = monthly.tail(3).mean()

    if model is not None:
        try:
             X_pred = pd.DataFrame([[float(avg_rev)]], columns=["avg_revenue"])
             pred = int(model.predict(X_pred)[0])

        except Exception:
            pred = int(avg_rev * 1.10)
    else:
        pred = int(avg_rev * 1.10)

    last_month = pd.Period(monthly.index[-1], freq="M")
    next_month = str(last_month + 1)

    forecast_df = monthly.copy()
    forecast_df.loc[next_month] = pred

    # Calculate growth %
    last_actual = monthly.iloc[-1]
    growth_pct = ((pred - last_actual) / last_actual) * 100 if last_actual != 0 else 0

    st.session_state["growth_pct"] = growth_pct



    st.markdown("### 📈 Monthly Sales + Forecast")
    st.bar_chart(forecast_df)
# Moving average trend (3-month)
    trend = monthly.rolling(window=3).mean()

    trend_df = pd.DataFrame({
    "Sales": monthly,
    "Trend (3M Avg)": trend
    })

    st.markdown("### 📊 Sales Trend Analysis")
    st.line_chart(trend_df)
   

    st.markdown(
        f"""
    <div class="glass-card">
        <p>Predicted Sales for <b>{next_month}</b></p>
        <h2 class="metric-val">₹{pred:,}</h2>
        <p><b>Expected Growth:</b> {growth_pct:.2f}%</p>
        <p style="font-size:0.85em;">Based on recent monthly trend</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    lower = int(pred * 0.9)
    upper = int(pred * 1.1)

    st.markdown(
    f"""
    <div class="glass-card" style="margin-top:15px;">
        <p>🎯 Forecast Confidence</p>
        <p>Expected Range:</p>
        <h3>₹{lower:,} – ₹{upper:,}</h3>
    </div>
    """,
    unsafe_allow_html=True,
)
    
    # ================= WHAT-IF SIMULATION =================
    st.markdown("## 🧪 What-If Simulation")

    marketing_boost = st.slider("📢 Marketing Impact (%)", -20, 30, 0)

    simulated_revenue = int(pred * (1 + marketing_boost / 100))

    log_activity("Used what-if simulation")


    growth_sim = ((simulated_revenue - pred) / pred) * 100 if pred != 0 else 0

    st.markdown(
    f"""
    <div class="glass-card" style="margin-top:15px;">
        <p>Simulated Revenue</p>
        <h2 class="metric-val">₹{simulated_revenue:,}</h2>
        <p>Impact vs Base Forecast: {growth_sim:.1f}%</p>
    </div>
    """,
    unsafe_allow_html=True,
)
    log_activity("Used what-if simulation")

    
# ================= TARGET MODE =================
    st.markdown("## 🎯 Revenue Target Planner")

    target_growth = st.slider("Desired Growth (%)", -10, 50, 10)

    target_revenue = int(pred * (1 + target_growth / 100))

    gap = target_revenue - pred

    st.markdown(
    f"""
    <div class="glass-card" style="margin-top:15px;">
        <p>Target Revenue Required</p>
        <h2 class="metric-val">₹{target_revenue:,}</h2>
        <p>Additional Revenue Needed: ₹{gap:,}</p>
    </div>
    """,
    unsafe_allow_html=True,
)




        # Save forecast for export
    st.session_state["forecast_month"] = next_month
    st.session_state["forecast_value"] = pred

    log_activity("Generated sales forecast")



# ---------- TOP ----------
elif query == "top":
    st.subheader("🏆 Revenue by Product")

    prod_series = (
        df.groupby("product")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    if len(prod_series) == 0:
        st.info("No product revenue data available.")
    else:
        st.bar_chart(prod_series)

        # -------- Top product --------
        top_product = prod_series.index[0]
        top_value = int(prod_series.iloc[0])

        st.markdown(
            f"""
            <div class="glass-card" style="margin-top:20px;">
                <p style="font-size:1.1em;">🔥 Top Performing Product</p>
                <h2 class="metric-val">{top_product}</h2>
                <p><b>Revenue:</b> ₹{top_value:,}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.session_state["top_product"] = top_product
        st.session_state["top_product_revenue"] = top_value


        # -------- Monthly trend --------
        df_prod = df.dropna(subset=["date"]).copy()
        df_prod["month"] = df_prod["date"].dt.to_period("M").astype(str)

        prod_monthly = (
            df_prod[df_prod["product"] == top_product]
            .groupby("month")["revenue"]
            .sum()
            .sort_index()
        )

        if len(prod_monthly) > 1:
            st.markdown("### 📅 Monthly Trend — Top Product")
            st.line_chart(prod_monthly)
        else:
            st.info("Not enough monthly data to show trend.")



# ---------- RISK ----------

elif query == "risk":
    st.subheader("⚠️ Region Risk Analysis")

    region_sales = df.groupby("region")["revenue"].sum().sort_values()
    st.bar_chart(region_sales)

    worst_region = region_sales.index[0]
    worst_value = float(region_sales.iloc[0])
    avg_value = region_sales.mean()

    # -------- Trend analysis (last 2 months) --------
    df_trend = df.dropna(subset=["date"]).copy()
    df_trend["month"] = df_trend["date"].dt.to_period("M")

    region_monthly = (
        df_trend[df_trend["region"] == worst_region]
        .groupby("month")["revenue"]
        .sum()
        .sort_index()
    )

    trend_label = "➖ Stable"
    if len(region_monthly) >= 2:
        last = region_monthly.iloc[-1]
        prev = region_monthly.iloc[-2]
        change = (last - prev) / prev if prev != 0 else 0

        if change > 0.05:
            trend_label = "⬆️ Improving"
        elif change < -0.05:
            trend_label = "⬇️ Declining"

    # -------- Risk level --------
    ratio = worst_value / avg_value

    if ratio < 0.7:
        risk_level = "HIGH 🔴"
    elif ratio < 0.9:
        risk_level = "MEDIUM 🟡"
    else:
        risk_level = "LOW 🟢"

    # -------- Auto business suggestion --------
    if "HIGH" in risk_level:
        suggestion = "Increase regional marketing spend, review pricing, and run targeted promotions."
    elif "MEDIUM" in risk_level:
        suggestion = "Optimize distribution channels and run short-term promotional campaigns."
    else:
        suggestion = "Maintain current strategy and monitor performance closely."

    # -------- Risk card --------
    st.markdown(
        f"""
        <div class="glass-card" style="margin-top:20px;">
            <p style="font-size:1.1em;">⚠️ Highest Risk Region</p>
            <h2 class="metric-val" style="color:#ef4444;">{worst_region}</h2>
            <p><b>Revenue:</b> ₹{int(worst_value):,}</p>
            <p><b>Risk Level:</b> {risk_level}</p>
            <p><b>Trend:</b> {trend_label}</p>
            <p><b>Suggested Action:</b> 💡 {suggestion}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.session_state["risk_region"] = worst_region
    st.session_state["risk_revenue"] = int(worst_value)
    st.session_state["risk_level"] = risk_level
    st.session_state["risk_suggestion"] = suggestion


    # -------- Drill-down: Product split in risky region --------
    df_region = df[df["region"] == worst_region]

    product_split = (
        df_region.groupby("product")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    if len(product_split) > 0:
        st.markdown("### 📦 Product Contribution — Risk Region")
        st.bar_chart(product_split)

    log_activity("Ran region risk analysis")


# --------- COMPARE MODE ---------
elif query == "compare":
    st.subheader("⚖️ Comparison Mode")

    compare_type = st.radio(
        "Compare by",
        ["Product", "Region"],
        horizontal=True
    )

    col_name = "product" if compare_type == "Product" else "region"

    options = df[col_name].dropna().unique().tolist()

    selected = st.multiselect(
        f"Select 2 {compare_type}s to compare",
        options,
        max_selections=2
    )

    if len(selected) == 2:
        a, b = selected

        comp_data = (
            df[df[col_name].isin(selected)]
            .groupby(col_name)["revenue"]
            .sum()
        )

        st.bar_chart(comp_data)

        val_a = int(comp_data[a])
        val_b = int(comp_data[b])

        winner = a if val_a > val_b else b

        st.markdown(
            f"""
            <div class="glass-card" style="margin-top:20px;">
                <p style="font-size:1.1em;">🏆 Winner</p>
                <h2 class="metric-val">{winner}</h2>
                <p>{a}: ₹{val_a:,}</p>
                <p>{b}: ₹{val_b:,}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # -------- Monthly trend --------
        df_trend = df.dropna(subset=["date"]).copy()
        df_trend["month"] = df_trend["date"].dt.to_period("M").astype(str)

        trend = (
            df_trend[df_trend[col_name].isin(selected)]
            .groupby(["month", col_name])["revenue"]
            .sum()
            .unstack()
            .fillna(0)
        )

        st.markdown("### 📈 Monthly Trend Comparison")
        st.line_chart(trend)

    else:
        st.info("Please select exactly 2 items to compare.")


# ================= AUTO BUSINESS INSIGHTS =================
st.markdown("## 🧠 CEO Insights")

insights = []

if "top_product" in st.session_state:
    insights.append(
        f"🏆 Top product is **{st.session_state['top_product']}** generating ₹{st.session_state['top_product_revenue']:,}."
    )

if "risk_region" in st.session_state:
    insights.append(
        f"⚠️ **{st.session_state['risk_region']}** is a {st.session_state['risk_level']} risk region. Action advised."
    )

if "forecast_value" in st.session_state:
    insights.append(
        f"🔮 Sales forecast for **{st.session_state['forecast_month']}** is ₹{st.session_state['forecast_value']:,}."
    )

if insights:
    st.markdown(
        f"""
        <div class="glass-card">
            <h3>📌 Executive Summary</h3>
            <ul>
                {''.join([f"<li>{i}</li>" for i in insights])}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.info("Run insights (forecast / top / risk) to generate CEO summary.")


# ================= MODEL EVALUATION =================
st.markdown("## 🧪 Model Evaluation")

df_eval = df.dropna(subset=["date"]).copy()
df_eval["month"] = df_eval["date"].dt.to_period("M").astype(str)

monthly_actual = (
    df_eval.groupby("month")["revenue"]
    .sum()
    .sort_index()
)

if model is not None and len(monthly_actual) >= 4:
    eval_actual = monthly_actual.tail(4).values
    eval_pred = []

    for val in eval_actual:
        try:
            X_eval = pd.DataFrame([[val]], columns=["avg_revenue"])
            eval_pred.append(float(model.predict(X_eval)[0]))

        except:
            eval_pred.append(val * 1.10)

    mae = sum(abs(a - p) for a, p in zip(eval_actual, eval_pred)) / len(eval_actual)
    rmse = (
        sum((a - p) ** 2 for a, p in zip(eval_actual, eval_pred)) / len(eval_actual)
    ) ** 0.5

    c1, c2 = st.columns(2)
    c1.metric("MAE", f"₹{int(mae):,}")
    c2.metric("RMSE", f"₹{int(rmse):,}")

    eval_df = pd.DataFrame(
        {"Actual": eval_actual, "Predicted": eval_pred},
        index=monthly_actual.tail(4).index,
    )

    st.markdown("### 📊 Actual vs Predicted (Recent Months)")
    st.line_chart(eval_df)

else:
    st.info("Not enough data or model unavailable for evaluation.")


# ================= STRATEGIC ACTION PLAN =================
st.markdown("## 🎯 Strategic Action Plan")

actions = []

# Forecast based action
if "forecast_value" in st.session_state and "growth_pct" in st.session_state:
    growth_pct = st.session_state["growth_pct"]

    if growth_pct > 10:
        actions.append("🚀 High projected growth. Increase inventory & marketing budget.")

    elif growth_pct < -5:
        actions.append("🔎 Moderate softness projected. Monitor performance and adjust strategy accordingly.")



# Risk based action
if "risk_level" in st.session_state:
    if "HIGH" in st.session_state["risk_level"]:
        actions.append("🔴 Immediate intervention required in risky region.")
    elif "MEDIUM" in st.session_state["risk_level"]:
        actions.append("🟡 Monitor risky region performance closely.")

# Product dominance check
product_share = df.groupby("product")["revenue"].sum()
if len(product_share) > 0:
    top_share = product_share.max() / product_share.sum()

    if top_share > 0.5:
        actions.append("📦 Revenue heavily dependent on one product. Diversification recommended.")

# Display
if actions:
    st.markdown(
        f"""
        <div class="glass-card">
            <h3>📊 AI-Generated Business Strategy</h3>
            <ul>
                {''.join([f"<li>{a}</li>" for a in actions])}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.info("No major strategic changes recommended at this time.")

# ================= FOOTER =================

st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#64748b;font-size:0.8em;'>BizSight AI • Self-Learning Analytics Engine</p>",
    unsafe_allow_html=True,
)

if __name__ == "__main__":
    pass





















