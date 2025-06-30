import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px

# Page Config
st.set_page_config(page_title="SmartExpiry Dashboard", layout="wide")
st.title("\U0001F9E0 SmartExpiry: AI-Powered Food Waste Reduction")
st.caption(f"\U0001F552 Last updated: {datetime.datetime.now().strftime('%d %b %Y, %I:%M %p')}")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("smartexpiry_enriched_inventory.csv")
    df["Expiry Date"] = pd.to_datetime(df["Expiry Date"])
    df["Days to Expiry"] = (df["Expiry Date"] - datetime.datetime.now()).dt.days
    df["Waste Risk Score"] = np.where(df["Predicted Unsold Units"] > 0, "High", "Low")
    df["Suggested Discount"] = df["Discount %"].astype(str) + "%"
    df["Donation Recommended"] = np.where(df["Days to Expiry"] <= 1, "Yes", "No")
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("\U0001F50D Filter Inventory")
selected_store = st.sidebar.selectbox("\U0001F3EC Select Store", ["All"] + sorted(df["Store Location"].unique()))
selected_category = st.sidebar.selectbox("\U0001F37D\ufe0f Select Category", ["All"] + sorted(df["Category"].unique()))
expiry_filter = st.sidebar.slider("⏳ Days to Expiry", 0, 30, (0, 7))

# Apply filters
filtered_df = df.copy()
if selected_store != "All":
    filtered_df = filtered_df[filtered_df["Store Location"] == selected_store]
if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]
filtered_df = filtered_df[(filtered_df["Days to Expiry"] >= expiry_filter[0]) & (filtered_df["Days to Expiry"] <= expiry_filter[1])]

# Charts Section
st.subheader("\U0001F4CA Visual Insights")
col1, col2 = st.columns(2)

with col1:
    risk_chart = filtered_df["Waste Risk Score"].value_counts().reset_index()
    risk_chart.columns = ["Risk", "Count"]
    fig_risk = px.pie(risk_chart, names="Risk", values="Count", title="Waste Risk Distribution")
    st.plotly_chart(fig_risk, use_container_width=True)

with col2:
    expiry_chart = filtered_df["Days to Expiry"].value_counts().sort_index().reset_index()
    expiry_chart.columns = ["Days to Expiry", "Item Count"]
    fig_exp = px.bar(expiry_chart, x="Days to Expiry", y="Item Count", title="Expiry Distribution (Days Left)")
    st.plotly_chart(fig_exp, use_container_width=True)

# Inventory Table
st.subheader("\U0001F4E6 Inventory Overview")
st.dataframe(filtered_df[[
    "Item", "Category", "Store Location", "Stock", "Expiry Date",
    "Days to Expiry", "Waste Risk Score", "Suggested Discount"
]], use_container_width=True)

# High-Risk Items
st.subheader("\U0001F525 Top 5 High-Risk Items")
top_risk_df = filtered_df[filtered_df["Waste Risk Score"] == "High"]
top_risk_df = top_risk_df.sort_values(by="Predicted Unsold Units", ascending=False).head(5)
st.table(top_risk_df[["Item", "Store Location", "Stock", "Days to Expiry", "Suggested Discount"]])

# ♻️ Donation Suggestions
st.subheader("♻️ Suggested Donations")
donation_df = filtered_df[filtered_df["Donation Recommended"] == "Yes"]

if not donation_df.empty:
    st.warning("🛒 Items that should be donated soon:")
    st.table(donation_df[["Item", "Stock", "Expiry Date", "Store Location"]])
    st.info("📍 Nearest NGO Partner: Robin Hood Army | 📞 +91-9876543210")
else:
    st.success("✅ No items require donation today.")

# 📥 Download Option
st.download_button(
    label="📥 Download Filtered Report",
    data=filtered_df.to_csv(index=False),
    file_name="SmartExpiry_Report.csv",
    mime="text/csv"
)

# Notes:
# Ensure the file "smartexpiry_enriched_inventory.csv" exists in the same directory as the script.
# You can create additional pages like forecast.py and connect them using Streamlit multipage structure (pages/ folder).  can we add login tabs