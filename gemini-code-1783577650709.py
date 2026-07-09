import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="Business Performance Dashboard",
    page_icon="📊",
    layout="wide"
)

# 1. Load and clean data
@st.cache_data
def load_data():
    # Load dataset
    df = pd.read_csv("mock_dataset.csv")
    
    # Clean whitespace from string columns and headers
    df.columns = df.columns.str.strip()
    string_cols = df.select_dtypes(include=['object']).columns
    for col in string_cols:
        df[col] = df[col].astype(str).str.strip()
        
    # Convert dates
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Year-Month'] = df['Order Date'].dt.to_period('M').astype(str)
    
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Missing 'mock_dataset.csv'. Please ensure the file is in the same directory as this script.")
    st.stop()

# 2. Sidebar Filters
st.sidebar.header("Filter Dashboard")

# Region Filter
regions = ["All"] + sorted(df['Region & District'].str.split(',').str[0].unique().tolist())
selected_region = st.sidebar.selectbox("Select Region", regions)

# Product Category Filter
categories = ["All"] + sorted(df['Product Category'].unique().tolist())
selected_category = st.sidebar.selectbox("Select Product Category", categories)

# Filter Logic
filtered_df = df.copy()
if selected_region != "All":
    filtered_df = filtered_df[filtered_df['Region & District'].str.startswith(selected_region)]
if selected_category != "All":
    filtered_df = filtered_df[filtered_df['Product Category'] == selected_category]

# 3. Main Dashboard Layout
st.title("📊 Business Performance Dashboard")
st.markdown("Interactive analysis of sales, profits, and product segments.")
st.markdown("---")

# KPI Metrics Row
col1, col2, col3, col4 = st.columns(4)

total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
total_orders = filtered_df['Order ID'].nunique()
avg_margin = filtered_df['Product Base Margin'].mean()

with col1:
    st.metric(label="Total Sales", value=f"${total_sales:,.2f}")
with col2:
    st.metric(label="Total Profit", value=f"${total_profit:,.2f}", delta=f"{ (total_profit/total_sales)*100:.1f}% Margin")
with col3:
    st.metric(label="Orders Placed", value=f"{total_orders:,}")
with col4:
    st.metric(label="Avg Base Margin", value=f"{avg_margin:.2%}" if not pd.isna(avg_margin) else "N/A")

st.markdown("---")

# Charts Row 1: Trend and Category Breakdown
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Monthly Sales Trend")
    trend_df = filtered_df.groupby('Year-Month')['Sales'].sum().reset_index().sort_values('Year-Month')
    fig_trend = px.line(trend_df, x='Year-Month', y='Sales', markers=True, title="Sales Over Time")
    st.plotly_chart(fig_trend, use_container_width=True)

with chart_col2:
    st.subheader("Profit by Product Sub-Category")
    subcat_df = filtered_df.groupby('Product Sub-Category')['Profit'].sum().reset_index().sort_values('Profit', ascending=True)
    fig_subcat = px.bar(subcat_df, x='Profit', y='Product Sub-Category', orientation='h', title="Profitability by Sub-Category")
    st.plotly_chart(fig_subcat, use_container_width=True)

# Charts Row 2: Segment Breakdown & Data Preview
chart_col3, chart_col4 = st.columns([1, 2])

with chart_col3:
    st.subheader("Sales by Customer Segment")
    segment_df = filtered_df.groupby('Customer Segment')['Sales'].sum().reset_index()
    fig_seg = px.pie(segment_df, values='Sales', names='Customer Segment', hole=0.4)
    st.plotly_chart(fig_seg, use_container_width=True)

with chart_col4:
    st.subheader("Filtered Data Preview")
    st.dataframe(
        filtered_df[['Order ID', 'Customer First Name', 'Customer Last Name', 'Product Name', 'Sales', 'Profit']], 
        hide_index=True, 
        use_container_width=True
    )