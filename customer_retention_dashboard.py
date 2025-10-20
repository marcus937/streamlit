import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import requests

st.set_page_config(page_title="Customer Retention Dashboard", layout="wide")
st.title("Customer Retention KPIs")

# Date input sidebar
with st.sidebar:
    st.header("Filters")
    start_date = st.date_input("Start Date", datetime.today() - timedelta(days=180))
    end_date = st.date_input("End Date", datetime.today())

params = {"from": start_date.isoformat(), "to": end_date.isoformat()}
BASE_URL = "https://your-api-endpoint.com"  # Replace with actual endpoint

@st.cache_data(show_spinner=False)
def fetch_metric(metric_id):
    url = f"{BASE_URL}/metrics/{metric_id}"
    try:
        res = requests.post(url, json={"params": params})
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"Error fetching {metric_id}: {e}")
        return {"rows": []}

# Fetch metrics
retention_data = fetch_metric("retention_rate")
churn_data = fetch_metric("churn_rate")
net_new_data = fetch_metric("net_new_customers")
cohort_data = fetch_metric("retention_by_cohort")

# KPI cards
col1, col2, col3 = st.columns(3)
col1.metric("Retention Rate", f"{retention_data['rows'][0]['value']:.1f}%") if retention_data['rows'] else col1.warning("No data")
col2.metric("Churn Rate", f"{churn_data['rows'][0]['value']:.1f}%") if churn_data['rows'] else col2.warning("No data")
col3.metric("Net New Customers", f"{net_new_data['rows'][0]['value']}") if net_new_data['rows'] else col3.warning("No data")

# Cohort heatmap
st.subheader("Cohort Retention Heatmap")
if cohort_data['rows']:
    df = pd.DataFrame(cohort_data['rows'])
    pivot = df.pivot(index="cohort_month", columns="retention_month", values="retention_pct")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="Blues", ax=ax)
    st.pyplot(fig)
else:
    st.info("No cohort retention data available for the selected period.")
