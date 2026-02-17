"""
AIDRA - Real-Time Flood Intelligence System
A decision-support dashboard for emergency resource allocation during disasters
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.logger import setup_logger

from data.weather_api import fetch_weather_data, fetch_hourly_forecast
from core.risk_engine import compute_adss
from core.demand_estimator import estimate_demand
from core.priority_engine import compute_priority
from core.allocation_engine import allocate_resources

logger = setup_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="AIDRA - Flood Intelligence",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚨 AIDRA - Real-Time Flood Intelligence System")
st.markdown("**Decision support for emergency resource allocation**")

# ============================================================================
# SIDEBAR: Controls and Settings
# ============================================================================
st.sidebar.header("⚙️ System Controls")

with st.sidebar:
    # Data refresh control
    if st.button("🔄 Refresh Data", key="refresh_btn"):
        st.cache_data.clear()
        logger.info("Cache cleared by user")
        st.rerun()
    
    # Resource controls
    st.subheader("Available Resources")
    total_ambulances = st.slider("🚑 Total Ambulances", 5, 100, 20, step=5)
    total_rescue = st.slider("🚨 Total Rescue Teams", 5, 50, 10, step=5)
    
    # Data mode
    st.subheader("Data Mode")
    use_synthetic = st.checkbox("Use Synthetic Data", value=False,
                                help="Enable for testing without API key")

# ============================================================================
# DATA PIPELINE: Fetch and Process
# ============================================================================
@st.cache_data(ttl=300)
def load_and_process_data(use_synthetic: bool):
    """Load weather data and execute full analysis pipeline."""
    try:
        logger.info("Starting data pipeline...")
        
        # Fetch data
        df = fetch_weather_data(use_synthetic=use_synthetic)
        
        if df.empty or len(df) < 3:
            logger.error("Insufficient data retrieved")
            return None, "Error: Unable to retrieve sufficient data"
        
        # Process pipeline
        df = compute_adss(df)
        df = estimate_demand(df)
        df = compute_priority(df)
        df = allocate_resources(df, total_ambulances, total_rescue)
        
        logger.info(f"Pipeline complete: {len(df)} zones processed")
        return df, None
        
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return None, f"Error: {str(e)}"

# Load data
df, error_msg = load_and_process_data(use_synthetic)

if error_msg:
    st.error(error_msg)
    st.stop()

if df is None or df.empty:
    st.error("No data available for analysis")
    st.stop()

# ============================================================================
# KEY METRICS DASHBOARD
# ============================================================================
st.markdown("### 📊 System Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_danger = df["ADSS"].sum()
    st.metric("🚨 Total Danger Score", f"{total_danger:.1f}", 
              help="Sum of all zone severity scores")

with col2:
    total_injuries = df["Estimated_Injuries"].sum()
    st.metric("👥 Est. Injuries", int(total_injuries),
              help="Estimated total casualties across all zones")

with col3:
    ambulance_gap = df["Ambulance_Deficit"].sum()
    st.metric("🚑 Ambulance Deficit", int(ambulance_gap),
              help="Unmet ambulance demand across all zones")

with col4:
    rescue_gap = df["Rescue_Deficit"].sum()
    st.metric("🆘 Rescue Team Deficit", int(rescue_gap),
              help="Unmet rescue team demand across all zones")

# ============================================================================
# VISUALIZATIONS: Risk and Resource Allocation
# ============================================================================
st.markdown("### 📈 Risk Assessment & Allocation")

col1, col2 = st.columns(2)

with col1:
    # ADSS by Zone
    fig_adss = px.bar(
        df.sort_values("ADSS", ascending=False),
        x="Zone",
        y="ADSS",
        color="ADSS",
        color_continuous_scale="Reds",
        title="🔴 Disaster Severity Score by Zone",
        labels={"ADSS": "ADSS (0-1)"},
        height=400
    )
    fig_adss.update_yaxes(range=[0, 1])
    st.plotly_chart(fig_adss, use_container_width=True)

with col2:
    # Priority Score by Zone
    fig_priority = px.bar(
        df,
        x="Zone",
        y="Priority_Score",
        color="Priority_Score",
        color_continuous_scale="Oranges",
        title="🟠 Deployment Priority by Zone",
        labels={"Priority_Score": "Priority (0-1)"},
        height=400
    )
    fig_priority.update_yaxes(range=[0, 1])
    st.plotly_chart(fig_priority, use_container_width=True)

# ============================================================================
# DETAILED RESOURCE ALLOCATION TABLE
# ============================================================================
st.markdown("### 🚑 Resource Allocation Details")

display_cols = [
    "Zone",
    "Priority_Score",
    "Ambulance_Needed",
    "Allocated_Ambulances",
    "Ambulance_Deficit",
    "Rescue_Teams_Needed",
    "Allocated_Rescue_Teams",
    "Rescue_Deficit"
]

# Ensure columns exist before displaying
available_cols = [col for col in display_cols if col in df.columns]
allocation_df = df[available_cols].copy()

# Format numerical columns
for col in allocation_df.columns:
    if col not in ["Zone"]:
        if "Score" in col:
            allocation_df[col] = allocation_df[col].apply(lambda x: f"{x:.3f}")
        else:
            allocation_df[col] = allocation_df[col].astype(int)

st.dataframe(allocation_df, use_container_width=True, hide_index=True)

# ============================================================================
# TEMPERATURE TREND ANALYSIS (24-Hour Forecast)
# ============================================================================
st.markdown("### 🌡️ Temperature Trends (24-Hour Forecast)")

with st.spinner("Loading weather trends..."):
    # Fetch hourly forecast
    @st.cache_data(ttl=600)
    def load_hourly_data(use_synthetic: bool):
        return fetch_hourly_forecast(use_synthetic=use_synthetic)
    
    hourly_df = load_hourly_data(use_synthetic)
    
    if hourly_df is not None and not hourly_df.empty:
        # Temperature trend for all zones
        st.markdown("#### 📈 Temperature Evolution (All Locations)")
        
        fig_temp = go.Figure()
        
        for zone in hourly_df['Zone'].unique():
            zone_data = hourly_df[hourly_df['Zone'] == zone].sort_values('Hour')
            fig_temp.add_trace(go.Scatter(
                x=zone_data['Hour'],
                y=zone_data['Temperature'],
                mode='lines+markers',
                name=zone,
                hovertemplate='<b>%{fullData.name}</b><br>Hour: %{x}<br>Temp: %{y:.1f}°C<extra></extra>'
            ))
        
        fig_temp.update_layout(
            title="🌡️ Temperature Forecast (Next 24 Hours)",
            xaxis_title="Hour of Day",
            yaxis_title="Temperature (°C)",
            height=400,
            hovermode='x unified',
            template='plotly_white'
        )
        
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # Grid of individual location trends
        st.markdown("#### 📍 Temperature by Location")
        
        zones = hourly_df['Zone'].unique()
        cols = st.columns(3)
        
        for idx, zone in enumerate(zones):
            zone_data = hourly_df[hourly_df['Zone'] == zone].sort_values('Hour')
            col = cols[idx % 3]
            
            with col:
                fig_zone = go.Figure()
                
                fig_zone.add_trace(go.Scatter(
                    x=zone_data['Hour'],
                    y=zone_data['Temperature'],
                    fill='tozeroy',
                    mode='lines+markers',
                    name='Temperature',
                    line=dict(color='#FF6B6B'),
                    marker=dict(size=6)
                ))
                
                # Highlight rainfall
                fig_zone.add_trace(go.Bar(
                    x=zone_data['Hour'],
                    y=zone_data['Rainfall'],
                    name='Rainfall (mm)',
                    marker=dict(color='#4ECDC4', opacity=0.3),
                    yaxis='y2'
                ))
                
                fig_zone.update_layout(
                    title=f"📍 {zone}",
                    xaxis_title="Hour",
                    yaxis_title="Temperature (°C)",
                    yaxis2=dict(
                        title="Rainfall (mm)",
                        overlaying='y',
                        side='right'
                    ),
                    height=350,
                    showlegend=True,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig_zone, use_container_width=True)
        
        # Current vs Forecast comparison
        st.markdown("#### 🔮 Statistical Forecast Summary")
        
        forecast_stats = []
        for zone in hourly_df['Zone'].unique():
            zone_hourly = hourly_df[hourly_df['Zone'] == zone]
            
            forecast_stats.append({
                "Location": zone,
                "Now": f"{zone_hourly[zone_hourly['Hour'] == 0]['Temperature'].values[0]:.1f}°C" 
                       if len(zone_hourly[zone_hourly['Hour'] == 0]) > 0 else "N/A",
                "Min": f"{zone_hourly['Temperature'].min():.1f}°C",
                "Max": f"{zone_hourly['Temperature'].max():.1f}°C",
                "Avg": f"{zone_hourly['Temperature'].mean():.1f}°C",
                "Peak Rain Hour": f"Hour {zone_hourly.loc[zone_hourly['Rainfall'].idxmax(), 'Hour']:.0f}" 
                                 if zone_hourly['Rainfall'].max() > 0 else "None",
                "Total Rain (24h)": f"{zone_hourly['Rainfall'].sum():.1f}mm"
            })
        
        stats_df = pd.DataFrame(forecast_stats)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)


# ============================================================================
# RESOURCE COVERAGE CHART
# ============================================================================
st.markdown("### 📊 Resource Coverage Analysis")

col1, col2 = st.columns(2)

with col1:
    # Ambulance allocation vs demand
    ambulance_data = pd.DataFrame({
        "Zone": df["Zone"],
        "Needed": df["Ambulance_Needed"],
        "Allocated": df["Allocated_Ambulances"]
    })
    
    fig_amb = go.Figure(data=[
        go.Bar(name="Needed", x=ambulance_data["Zone"], y=ambulance_data["Needed"], 
               marker_color="lightcoral"),
        go.Bar(name="Allocated", x=ambulance_data["Zone"], y=ambulance_data["Allocated"],
               marker_color="darkgreen")
    ])
    fig_amb.update_layout(
        title="🚑 Ambulance Allocation vs Demand",
        barmode="group",
        height=400,
        xaxis_title="Zone",
        yaxis_title="Count"
    )
    st.plotly_chart(fig_amb, use_container_width=True)

with col2:
    # Rescue team allocation vs demand
    rescue_data = pd.DataFrame({
        "Zone": df["Zone"],
        "Needed": df["Rescue_Teams_Needed"],
        "Allocated": df["Allocated_Rescue_Teams"]
    })
    
    fig_rescue = go.Figure(data=[
        go.Bar(name="Needed", x=rescue_data["Zone"], y=rescue_data["Needed"],
               marker_color="lightcoral"),
        go.Bar(name="Allocated", x=rescue_data["Zone"], y=rescue_data["Allocated"],
               marker_color="darkgreen")
    ])
    fig_rescue.update_layout(
        title="🆘 Rescue Team Allocation vs Demand",
        barmode="group",
        height=400,
        xaxis_title="Zone",
        yaxis_title="Count"
    )
    st.plotly_chart(fig_rescue, use_container_width=True)

# ============================================================================
# SYSTEM INFO
# ============================================================================
with st.sidebar:
    st.markdown("---")
    st.subheader("ℹ️ System Info")
    st.metric("Zones Analyzed", len(df))
    
    ambulance_coverage = (df["Allocated_Ambulances"].sum() / df["Ambulance_Needed"].sum() * 100) \
        if df["Ambulance_Needed"].sum() > 0 else 0
    rescue_coverage = (df["Allocated_Rescue_Teams"].sum() / df["Rescue_Teams_Needed"].sum() * 100) \
        if df["Rescue_Teams_Needed"].sum() > 0 else 0
    
    st.metric("Ambulance Coverage", f"{ambulance_coverage:.1f}%")
    st.metric("Rescue Coverage", f"{rescue_coverage:.1f}%")
