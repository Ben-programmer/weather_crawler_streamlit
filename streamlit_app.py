"""
Weather Forecast Visualization - Streamlit Web Application

This application provides an interactive web interface for viewing weather
temperature forecasts from the CWA (Central Weather Administration) database.

Author: AIoT Course Project
Date: 2025-12-06
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import numpy as np
import subprocess
import sys

# Page configuration
st.set_page_config(
    page_title="CWA Weather Forecast",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database configuration
DB_NAME = "sqlitedata.db"

# Auto-fetch data if database doesn't exist (for Streamlit Cloud deployment)
def ensure_data_exists():
    """
    Check if database exists, if not, automatically run crawler to fetch data.
    This is essential for Streamlit Cloud where the filesystem is ephemeral.
    """
    if not os.path.exists(DB_NAME):
        st.warning("⏳ Database not found. Fetching latest weather data from CWA API...")
        
        try:
            # Import and run crawler functions directly
            import crawler
            
            with st.spinner("🌐 Connecting to CWA Open Data API..."):
                # Fetch data from API
                data = crawler.fetch_cwa_opendata()
                
                if data and 'records' in data:
                    # Initialize database
                    crawler.init_database()
                    
                    # Extract and save data
                    table_data = crawler.extract_temperature_table(data)
                    crawler.save_to_database(table_data)
                    
                    st.success("✅ Weather data fetched successfully!")
                    st.rerun()  # Reload the app with new data
                else:
                    st.error("❌ Failed to fetch data from CWA API. Please check your connection.")
                    st.stop()
                    
        except Exception as e:
            st.error(f"❌ Error fetching data: {e}")
            st.info("💡 **Troubleshooting:**\n"
                   "1. Check your internet connection\n"
                   "2. Verify CWA API is accessible\n"
                   "3. Check API authorization key")
            st.stop()

# Ensure data exists before proceeding
ensure_data_exists()

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_database_connection():
    """
    Create and return a database connection.
    Uses Streamlit caching to reuse connection.
    """
    if not os.path.exists(DB_NAME):
        return None
    return sqlite3.connect(DB_NAME, check_same_thread=False)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_weather_data():
    """
    Load weather forecast data from database.
    
    Returns:
        pandas.DataFrame: Weather forecast data or None if error
    """
    conn = get_database_connection()
    if conn is None:
        return None
    
    try:
        query = """
            SELECT 
                location,
                forecast_date,
                max_temp,
                min_temp,
                fetched_at
            FROM weather_forecast
            ORDER BY fetched_at DESC, location, forecast_date
        """
        df = pd.read_sql_query(query, conn)
        
        # Convert date columns
        df['forecast_date'] = pd.to_datetime(df['forecast_date'])
        df['fetched_at'] = pd.to_datetime(df['fetched_at'])
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


@st.cache_data(ttl=300)
def get_latest_fetch_time():
    """Get the most recent data fetch timestamp."""
    conn = get_database_connection()
    if conn is None:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(fetched_at) FROM weather_forecast")
        result = cursor.fetchone()[0]
        return pd.to_datetime(result) if result else None
    except Exception as e:
        st.error(f"Error getting fetch time: {e}")
        return None


def get_location_coordinates():
    """
    Get approximate coordinates for Taiwan regions.
    Returns dict with location names as keys and (lat, lon) as values.
    """
    return {
        '北部地區': (25.0330, 121.5654),      # Taipei area
        '中部地區': (24.1477, 120.6736),      # Taichung area
        '南部地區': (22.6273, 120.3014),      # Kaohsiung area
        '東北部地區': (24.7571, 121.7603),    # Yilan area
        '東部地區': (23.9871, 121.6015),      # Hualien area
        '東南部地區': (22.7972, 121.0713)     # Taitung area
    }


def create_taiwan_temperature_map(df, date_filter=None):
    """
    Create an interactive map visualization of Taiwan with temperature data.
    
    Args:
        df: DataFrame with temperature data
        date_filter: Optional specific date to display (uses today if None)
        
    Returns:
        plotly.graph_objects.Figure
    """
    if df is None or df.empty:
        return None
    
    # Get today's date if no filter specified
    if date_filter is None:
        date_filter = df['forecast_date'].min()
    
    # Filter data for the specified date
    df_today = df[df['forecast_date'] == date_filter].copy()
    
    if df_today.empty:
        return None
    
    # Add coordinates to dataframe
    coords = get_location_coordinates()
    df_today['lat'] = df_today['location'].map(lambda x: coords.get(x, (0, 0))[0])
    df_today['lon'] = df_today['location'].map(lambda x: coords.get(x, (0, 0))[1])
    
    # Calculate average temperature for sizing
    df_today['avg_temp'] = (df_today['max_temp'] + df_today['min_temp']) / 2
    
    # Create the map
    fig = go.Figure()
    
    # Add scatter points for each location
    fig.add_trace(go.Scattergeo(
        lon=df_today['lon'],
        lat=df_today['lat'],
        text=df_today['location'],
        mode='markers+text',
        marker=dict(
            size=df_today['avg_temp'] * 2,  # Size based on temperature
            color=df_today['avg_temp'],      # Color based on temperature
            colorscale='RdYlBu_r',          # Red (hot) to Blue (cold)
            showscale=True,
            colorbar=dict(
                title="Avg Temp<br>(°C)",
                thickness=15,
                len=0.7
            ),
            line=dict(width=1, color='white'),
            cmin=10,
            cmax=30
        ),
        textposition='top center',
        textfont=dict(size=10, color='black', family='Arial Black'),
        hovertemplate='<b>%{text}</b><br>' +
                     'Max: %{customdata[0]}°C<br>' +
                     'Min: %{customdata[1]}°C<br>' +
                     'Avg: %{customdata[2]:.1f}°C<br>' +
                     '<extra></extra>',
        customdata=df_today[['max_temp', 'min_temp', 'avg_temp']].values
    ))
    
    # Update map layout to focus on Taiwan
    fig.update_geos(
        center=dict(lat=23.5, lon=121.0),
        projection_scale=30,
        visible=True,
        resolution=50,
        showcountries=True,
        countrycolor="lightgray",
        showcoastlines=True,
        coastlinecolor="gray",
        showland=True,
        landcolor="lightgreen",
        showocean=True,
        oceancolor="lightblue",
        projection_type="mercator"
    )
    
    fig.update_layout(
        title=dict(
            text=f"🗺️ Taiwan Temperature Map - {date_filter.strftime('%Y-%m-%d')}",
            x=0.5,
            xanchor='center',
            font=dict(size=20, color='#1f77b4')
        ),
        height=500,
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    return fig


def get_locations(df):
    """Get unique locations from dataframe."""
    if df is None or df.empty:
        return []
    return sorted(df['location'].unique().tolist())


def filter_latest_forecast(df):
    """Filter to keep only the most recent forecast for each location and date."""
    if df is None or df.empty:
        return df
    
    # Get the most recent fetch time
    latest_fetch = df['fetched_at'].max()
    
    # Filter to only the latest fetch
    return df[df['fetched_at'] == latest_fetch].copy()


def calculate_statistics(df):
    """Calculate summary statistics for the dataframe."""
    if df is None or df.empty:
        return None
    
    stats = {
        'avg_max_temp': df['max_temp'].mean(),
        'avg_min_temp': df['min_temp'].mean(),
        'highest_max': df['max_temp'].max(),
        'lowest_min': df['min_temp'].min(),
        'temp_range': df['max_temp'].max() - df['min_temp'].min(),
        'num_forecasts': len(df),
        'num_days': df['forecast_date'].nunique()
    }
    return stats


def create_temperature_chart(df, title="Temperature Forecast"):
    """
    Create an interactive line chart for temperature data.
    
    Args:
        df: DataFrame with temperature data
        title: Chart title
        
    Returns:
        plotly.graph_objects.Figure
    """
    if df is None or df.empty:
        return None
    
    fig = go.Figure()
    
    # Get unique locations
    locations = df['location'].unique()
    
    for location in locations:
        location_data = df[df['location'] == location].sort_values('forecast_date')
        
        # Add max temperature line
        fig.add_trace(go.Scatter(
            x=location_data['forecast_date'],
            y=location_data['max_temp'],
            name=f'{location} - Max',
            mode='lines+markers',
            line=dict(width=2),
            marker=dict(size=8)
        ))
        
        # Add min temperature line
        fig.add_trace(go.Scatter(
            x=location_data['forecast_date'],
            y=location_data['min_temp'],
            name=f'{location} - Min',
            mode='lines+markers',
            line=dict(width=2, dash='dot'),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Temperature (°C)",
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    return fig


def main():
    """Main application function."""
    
    # Header
    st.markdown('<div class="main-header">🌤️ CWA Weather Forecast Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Taiwan Agricultural Weather Forecast Visualization</div>', unsafe_allow_html=True)
    
    # Check database existence
    if not os.path.exists(DB_NAME):
        st.error(f"❌ Database file '{DB_NAME}' not found!")
        st.info("📝 Please run `python crawler.py` first to fetch weather data from CWA API.")
        st.stop()
    
    # Load data
    with st.spinner("Loading weather data..."):
        df_all = load_weather_data()
    
    if df_all is None or df_all.empty:
        st.warning("⚠️ No weather data available in the database.")
        st.info("📝 Please run `python crawler.py` to fetch weather data from CWA API.")
        st.stop()
    
    # Filter to latest forecast
    df = filter_latest_forecast(df_all)
    
    # Get last update time
    last_update = get_latest_fetch_time()
    
    # Sidebar
    st.sidebar.header("🎯 Filter Options")
    
    # Location selector
    locations = get_locations(df)
    location_options = ["All Locations"] + locations
    selected_location = st.sidebar.selectbox(
        "Select Location",
        location_options,
        index=0
    )
    
    # Display last update time
    if last_update:
        st.sidebar.markdown("---")
        st.sidebar.info(f"📅 **Last Updated:**\n{last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check if data is stale (>24 hours)
        hours_old = (datetime.now() - last_update).total_seconds() / 3600
        if hours_old > 24:
            st.sidebar.warning(f"⚠️ Data is {hours_old:.1f} hours old. Consider updating!")
    
    # About section
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### ℹ️ About
    This dashboard displays 7-day weather forecasts for 6 regions in Taiwan.
    
    **Data Source:** Central Weather Administration (CWA) Open Data API
    
    **Regions:**
    - 北部地區 (North)
    - 中部地區 (Central)
    - 南部地區 (South)
    - 東北部地區 (Northeast)
    - 東部地區 (East)
    - 東南部地區 (Southeast)
    """)
    
    # Filter data by location
    if selected_location != "All Locations":
        df_filtered = df[df['location'] == selected_location].copy()
        chart_title = f"Temperature Forecast - {selected_location}"
    else:
        df_filtered = df.copy()
        chart_title = "Temperature Forecast - All Locations"
    
    # === TAIWAN TEMPERATURE MAP (TOP SECTION) ===
    st.markdown("---")
    
    # Date selector for map
    available_dates = sorted(df['forecast_date'].unique())
    
    col_map1, col_map2 = st.columns([3, 1])
    with col_map2:
        selected_date = st.selectbox(
            "📅 Select Date for Map",
            available_dates,
            format_func=lambda x: x.strftime('%Y-%m-%d (%A)')
        )
    
    # Create and display Taiwan temperature map
    with st.spinner("Generating Taiwan temperature map..."):
        map_fig = create_taiwan_temperature_map(df, selected_date)
        if map_fig:
            st.plotly_chart(map_fig, use_container_width=True)
        else:
            st.warning("⚠️ Unable to generate map visualization")
    
    st.markdown("---")
    
    # Calculate statistics
    stats = calculate_statistics(df_filtered)
    
    # Display metrics
    st.subheader("📊 Summary Statistics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Avg Max Temp", f"{stats['avg_max_temp']:.1f}°C")
    with col2:
        st.metric("Avg Min Temp", f"{stats['avg_min_temp']:.1f}°C")
    with col3:
        st.metric("Highest Max", f"{stats['highest_max']}°C")
    with col4:
        st.metric("Lowest Min", f"{stats['lowest_min']}°C")
    with col5:
        st.metric("Forecast Days", f"{stats['num_days']}")
    
    # Temperature chart
    st.subheader("📈 Temperature Trends")
    fig = create_temperature_chart(df_filtered, chart_title)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.subheader("📋 Detailed Forecast Data")
    
    # Prepare display dataframe
    display_df = df_filtered[['location', 'forecast_date', 'max_temp', 'min_temp']].copy()
    display_df['forecast_date'] = display_df['forecast_date'].dt.strftime('%Y-%m-%d')
    display_df.columns = ['Location', 'Date', 'Max Temp (°C)', 'Min Temp (°C)']
    
    # Display with sorting
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    # Download button
    csv = display_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name=f"weather_forecast_{selected_location.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv'
    )
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>🎓 AIoT Course Project | Data from CWA Open Data Platform</p>
            <p>Built with ❤️ using Streamlit</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
