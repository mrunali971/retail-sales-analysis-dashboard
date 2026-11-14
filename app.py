
import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

st.set_page_config(
    page_title="Retail Sales Analytics",
    page_icon="📊",
    layout="wide"
)

# ---------------- CUSTOM DESIGN ----------------
st.title("📊 Retail Sales Analytics Dashboard")
st.caption("Business intelligence | Revenue | Profitability | Performance")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("sales_data.csv")
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])

    required = [
        "Order_ID", "Order_Date", "Product", "Category",
        "Quantity", "Sales", "Profit", "Region"
    ]

    if not all(col in df.columns for col in required):
        raise ValueError("Required columns are missing.")

    if df[required].isnull().any().any():
        raise ValueError("Dataset contains missing values.")

    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Dataset error: {e}")
    st.stop()

# ---------------- SIDEBAR ----------------
st.sidebar.header("🔍 Dashboard Filters")

regions = st.sidebar.multiselect(
    "Select Region",
    sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique())
)

categories = st.sidebar.multiselect(
    "Select Category",
    sorted(df["Category"].unique()),
    default=sorted(df["Category"].unique())
)

start_date = st.sidebar.date_input(
    "Start Date", df["Order_Date"].min().date()
)

end_date = st.sidebar.date_input(
    "End Date", df["Order_Date"].max().date()
)

if start_date > end_date:
    st.error("Start date cannot be after end date.")
    st.stop()

data = df[
    (df["Region"].isin(regions)) &
    (df["Category"].isin(categories)) &
    (df["Order_Date"].dt.date >= start_date) &
    (df["Order_Date"].dt.date <= end_date)
].copy()

if data.empty:
    st.warning("No data available for selected filters.")
    st.stop()

# ---------------- CALCULATIONS ----------------
revenue = data["Sales"].sum()
profit = data["Profit"].sum()
orders = data["Order_ID"].nunique()
units = data["Quantity"].sum()

margin = (profit / revenue * 100) if revenue else 0

region_profit = data.groupby("Region")["Profit"].sum()
best_region = region_profit.idxmax()

product_profit = data.groupby("Product")["Profit"].sum()
best_product = product_profit.idxmax()

category_profit = data.groupby("Category")["Profit"].sum()
best_category = category_profit.idxmax()

# ---------------- KPI DASHBOARD ----------------
st.subheader("📌 Business Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Revenue", f"₹{revenue:,.0f}")
c2.metric("Total Profit", f"₹{profit:,.0f}")
c3.metric("Total Orders", f"{orders:,}")
c4.metric("Units Sold", f"{units:,}")

st.divider()

# ---------------- PROFITABILITY INSIGHTS ----------------
st.subheader("💡 Business Performance Insights")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Profit Margin", f"{margin:.2f}%")
c2.metric("Best Region", best_region)
c3.metric("Top Product", best_product)
c4.metric("Top Category", best_category)

st.divider()

# ---------------- MONTHLY SALES ----------------
st.subheader("📈 Monthly Sales Trend")

monthly = (
    data.groupby(data["Order_Date"].dt.to_period("M"))["Sales"]
    .sum()
    .reset_index()
)

monthly["Month"] = monthly["Order_Date"].astype(str)

fig1 = px.line(
    monthly,
    x="Month",
    y="Sales",
    markers=True,
    title="Monthly Revenue Trend"
)

st.plotly_chart(fig1, use_container_width=True)

# ---------------- CATEGORY AND REGION ----------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("🛍️ Sales by Category")

    category_sales = data.groupby("Category")["Sales"].sum().reset_index()

    fig2 = px.pie(
        category_sales,
        names="Category",
        values="Sales",
        hole=0.45,
        title="Revenue Contribution"
    )

    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.subheader("🌍 Regional Performance")

    region_sales = data.groupby("Region")["Sales"].sum().reset_index()

    fig3 = px.bar(
        region_sales,
        x="Region",
        y="Sales",
        color="Region",
        title="Revenue by Region"
    )

    st.plotly_chart(fig3, use_container_width=True)

# ---------------- PRODUCT ANALYSIS ----------------
st.subheader("🏆 Product Performance")

product_data = (
    data.groupby("Product")
    .agg(
        Total_Sales=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Units_Sold=("Quantity", "sum")
    )
    .reset_index()
    .sort_values("Total_Sales", ascending=False)
)

fig4 = px.bar(
    product_data,
    x="Product",
    y="Total_Sales",
    color="Total_Profit",
    title="Product-wise Revenue and Profit"
)

st.plotly_chart(fig4, use_container_width=True)

# ---------------- BUSINESS INSIGHTS ----------------
st.subheader("📊 Automated Business Insights")

st.write(
    f"• **{best_region}** is the highest profit-generating region."
)

st.write(
    f"• **{best_product}** is the most profitable product."
)

st.write(
    f"• **{best_category}** is the most profitable product category."
)

st.write(
    f"• Overall profit margin is **{margin:.2f}%**."
)

# ---------------- SQL ANALYSIS ----------------
st.divider()
st.subheader("🗄️ SQL Sales Analysis")

conn = sqlite3.connect(":memory:")
data.to_sql("sales", conn, index=False, if_exists="replace")

query = """
SELECT
    Category,
    SUM(Sales) AS Total_Revenue,
    SUM(Profit) AS Total_Profit,
    SUM(Quantity) AS Units_Sold,
    ROUND(SUM(Profit) * 100.0 / NULLIF(SUM(Sales), 0), 2)
        AS Profit_Margin
FROM sales
GROUP BY Category
ORDER BY Total_Revenue DESC
"""

sql_result = pd.read_sql_query(query, conn)

st.dataframe(sql_result, use_container_width=True)

conn.close()

# ---------------- DATA TABLE ----------------
with st.expander("📋 View Sales Dataset"):
    st.dataframe(data, use_container_width=True)

# ---------------- DOWNLOAD ----------------
st.download_button(
    "⬇️ Download Filtered Dataset",
    data=data.to_csv(index=False).encode("utf-8"),
    file_name="filtered_sales_data.csv",
    mime="text/csv"
)

st.success("Dashboard loaded successfully!")
