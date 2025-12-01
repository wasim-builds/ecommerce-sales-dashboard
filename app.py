import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 1. Page Config (Must be the first line)
st.set_page_config(
    page_title="SuperStore Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR UI POLISH ---
# This forces the text to be visible even in Light Mode
st.markdown("""
<style>
    /* Metric Cards Styling */
    div[data-testid="stMetric"] {
        background-color: #222222 !important; /* Dark Card Background */
        border: 1px solid #333333 !important;
        padding: 15px 25px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    }
    
    /* FORCE TEXT COLORS TO BE VISIBLE */
    /* This targets the label (e.g., "Total Sales") */
    div[data-testid="stMetric"] label {
        color: #e0e0e0 !important; 
    }
    /* This targets the value (e.g., "$506,464") */
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #ffffff !important; 
    }
    /* This targets the delta (e.g., "12% vs Last Year") */
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
        color: #00ff00 !important; /* Bright Green for positive growth */
    }
    
    /* Title Gradient */
    .title-text {
        font-size: 50px;
        font-weight: bold;
        background: -webkit-linear-gradient(45deg, #00C9FF, #92FE9D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 2. Data Loading (Same as before)
@st.cache_data
def load_data():
    rows = 500
    dates = pd.date_range(start="2024-01-01", periods=rows)
    categories = ["Furniture", "Office Supplies", "Technology"]
    sub_categories = {
        "Furniture": ["Chairs", "Tables", "Bookcases"],
        "Office Supplies": ["Paper", "Binders", "Art", "Fasteners"],
        "Technology": ["Phones", "Accessories", "Copiers"]
    }
    regions = ["East", "West", "Central", "South"]
    
    data = []
    for date in dates:
        cat = np.random.choice(categories)
        sub_cat = np.random.choice(sub_categories[cat])
        sales = np.random.randint(50, 2000)
        profit = sales * np.random.uniform(-0.1, 0.4) 
        region = np.random.choice(regions)
        data.append([date, region, cat, sub_cat, sales, profit])
        
    df = pd.DataFrame(data, columns=["Order Date", "Region", "Category", "Sub-Category", "Sales", "Profit"])
    return df

df = load_data()

# 3. Sidebar Styling & Filters
st.sidebar.title("🔍 Filter Options")
st.sidebar.markdown("Use the filters below to refine the dashboard view.")

region = st.sidebar.multiselect(
    "Select Region:",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

category = st.sidebar.multiselect(
    "Select Category:",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

# Apply Filters
df_selection = df.query("Region == @region & Category == @category")

if df_selection.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop()

# 4. Main Page Header
st.markdown('<p class="title-text">🛒 SuperStore Analytics</p>', unsafe_allow_html=True)
st.markdown("### Executive Overview")

# 5. KPI Cards (Styled via CSS above)
total_sales = int(df_selection["Sales"].sum())
total_profit = int(df_selection["Profit"].sum())
profit_margin = round((total_profit / total_sales) * 100, 1) if total_sales > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"${total_sales:,}", "12% vs Last Year")
col2.metric("Total Profit", f"${total_profit:,}", "8% vs Last Year")
col3.metric("Profit Margin", f"{profit_margin}%", "2% vs Last Year")

st.markdown("---")

# 6. Advanced Visualizations (Dark Mode Enabled)

# Helper to style plots
def style_plot(fig):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"), # Default to white text for charts
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

row1_col1, row1_col2 = st.columns(2)

# Chart 1: Sales by Sub-Category (Gradient Bars)
# FIX: Select [['Sales']] before summing to prevent TypeError
sales_by_subcat = df_selection.groupby(by=["Sub-Category"])[["Sales"]].sum().sort_values(by="Sales")

fig_subcat = px.bar(
    sales_by_subcat,
    x="Sales",
    y=sales_by_subcat.index,
    orientation="h",
    title="<b>🏆 Top Selling Sub-Categories</b>",
    color="Sales",
    color_continuous_scale="Bluyl", # Cyber-like gradient
)
fig_subcat = style_plot(fig_subcat)
fig_subcat.update_coloraxes(showscale=False) # Hide the color bar for a cleaner look
row1_col1.plotly_chart(fig_subcat, use_container_width=True)

# Chart 2: Sales by Region (Donut Chart)
fig_region = px.pie(
    df_selection,
    values='Sales',
    names='Region',
    title="<b>🌍 Sales Distribution by Region</b>",
    hole=0.6, # Makes it a Donut chart
    color_discrete_sequence=px.colors.qualitative.Pastel
)
fig_region = style_plot(fig_region)
row1_col2.plotly_chart(fig_region, use_container_width=True)

# Chart 3: Time Series (Neon Line)
st.subheader("📈 Revenue Trend Over Time")
df_selection["Month"] = df_selection["Order Date"].dt.to_period("M").astype(str)

# FIX: Select [['Sales']] before summing
sales_by_month = df_selection.groupby(by=["Month"])[["Sales"]].sum()

fig_monthly = px.area( # Changed to Area chart for a modern look
    sales_by_month,
    x=sales_by_month.index,
    y="Sales",
    markers=True,
)
fig_monthly.update_traces(line_color='#00C9FF', fillcolor='rgba(0, 201, 255, 0.2)')
fig_monthly = style_plot(fig_monthly)
fig_monthly.update_xaxes(showgrid=False)
fig_monthly.update_yaxes(showgrid=True, gridcolor='#333333')

st.plotly_chart(fig_monthly, use_container_width=True)

# 7. Data Table
with st.expander("📂 View Detailed Data Source"):
    st.dataframe(
        df_selection.sort_values(by="Order Date", ascending=False),
        use_container_width=True
    )