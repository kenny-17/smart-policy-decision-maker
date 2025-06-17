# dashboard.py

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="EV Market Analysis Dashboard",
    page_icon="🚗",
    layout="wide"
)

# --- Database Connection ---
# Use st.cache_resource to only run this connection once.
@st.cache_resource
def get_connection():
    # IMPORTANT: Replace with your actual password and database name
    db_password = 'Ken@2004' # <-- CHANGE THIS
    db_name = 'policy_simulator_db'
    
    # --- Other details (should be correct) ---
    db_user = 'postgres'
    db_host = 'localhost'
    db_port = '5432'
    
    from urllib.parse import quote_plus
    db_password_encoded = quote_plus(db_password)
    
    return create_engine(f'postgresql+psycopg2://{db_user}:{db_password_encoded}@{db_host}:{db_port}/{db_name}')

engine = get_connection()

# --- Data Loading Functions ---
# Use st.cache_data to only load the data once.
@st.cache_data
def load_data(query):
    return pd.read_sql(query, engine)

# Load data from your views and tables
kpi_data = load_data("SELECT * FROM country_kpi_view;")
forecast_data = load_data("SELECT * FROM ev_sales_forecasts;")

# Convert year/date columns to datetime for plotting
kpi_data['year'] = pd.to_datetime(kpi_data['year'], format='%Y')
forecast_data['forecast_date'] = pd.to_datetime(forecast_data['forecast_date'])


# --- DASHBOARD UI ---

st.title("🚗 Intelligent EV Market Analysis Dashboard")
st.markdown("A strategic decision support system for global EV market entry.")


# --- Sidebar for User Inputs ---
st.sidebar.header("Select a Market")
# Get a unique list of countries for the dropdown
country_list = kpi_data['country'].unique()
selected_country = st.sidebar.selectbox("Country", country_list)


# --- Filter Data Based on Selection ---
country_kpi = kpi_data[kpi_data['country'] == selected_country]
country_forecast = forecast_data[forecast_data['country'] == selected_country]


# --- Main Page Content ---

st.header(f"Analysis for: {selected_country}")

# --- Display Key Metrics ---
st.subheader("Latest Key Metrics")

# Get the most recent year's data
latest_kpi = country_kpi.sort_values(by='year', ascending=False).iloc[0]

col1, col2, col3 = st.columns(3)
col1.metric("EV Sales", f"{latest_kpi['ev_sales']:,.0f} units", help="Total EV sales in the most recent year.")
col2.metric("GDP", f"${latest_kpi['gdp_usd']/1e9:,.2f} Billion", help="Gross Domestic Product (USD).")
col3.metric("Population", f"{latest_kpi['population_total']/1e6:,.2f} Million", help="Total population.")


# --- Charts and Visualizations ---

st.subheader("Historical Trends")

# Chart 1: Historical EV Sales
fig_sales = px.line(country_kpi, x='year', y='ev_sales', title='Historical EV Sales Trend', markers=True)
fig_sales.update_layout(xaxis_title='Year', yaxis_title='EV Sales (Units)')
st.plotly_chart(fig_sales, use_container_width=True)


st.subheader("Future Sales Forecast (5 Years)")

# Chart 2: Machine Learning Forecast
fig_forecast = px.line(country_forecast, x='forecast_date', y='predicted_sales', title='EV Sales Forecast', markers=True)
# Add confidence interval bands
fig_forecast.add_scatter(x=country_forecast['forecast_date'], y=country_forecast['predicted_sales_upper'], fill='tozeroy', fillcolor='rgba(0,100,80,0.2)', line_color='rgba(255,255,255,0)', name='Upper Bound')
fig_forecast.add_scatter(x=country_forecast['forecast_date'], y=country_forecast['predicted_sales_lower'], fill='tozeroy', fillcolor='rgba(0,100,80,0.2)', line_color='rgba(255,255,255,0)', name='Lower Bound')
fig_forecast.update_layout(xaxis_title='Year', yaxis_title='Predicted EV Sales', showlegend=False)
st.plotly_chart(fig_forecast, use_container_width=True)


# --- Display Raw Data Tables ---
with st.expander("Show Raw Data Tables"):
    st.subheader("KPI Data (Historical)")
    st.dataframe(country_kpi)
    
    st.subheader("Forecast Data (Predictions)")
    st.dataframe(country_forecast)