"""
RENO-TITAN Module 3: Geospatial Visualization
Page for choropleth maps and production intensity visualizations.
"""

import streamlit as st
import pandas as pd
import logging
import sys
import os
import folium
from streamlit_folium import st_folium
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import (
    get_production_data,
    get_countries,
    get_country_name
)
from utils.country_coordinates import get_country_centroid

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Geospatial Maps - RENO-TITAN",
    page_icon="🗺️",
    layout="wide"
)

logger = logging.getLogger(__name__)

# ============================================================================
# COLOR PALETTES
# ============================================================================

COLOR_PALETTES = {
    'Reds': ['#ffffcc', '#ffeda0', '#fed976', '#feb24c', '#fd8d3c', '#f03b20', '#bd0026', '#800026'],
    'Greens': ['#edf8e9', '#c7e9c4', '#a1d99b', '#74c476', '#41ab5d', '#238b45', '#006d2c', '#00441b'],
    'Blues': ['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c'],
    'Purples': ['#fcfbfd', '#efedf5', '#dadaeb', '#bcbddc', '#9e9ac8', '#807dba', '#6a51a3', '#54278f'],
    'Oranges': ['#fff5eb', '#fee6ce', '#fdd0a2', '#fdae6b', '#fd8d3c', '#f16913', '#d94801', '#8c2d04'],
    'Viridis': ['#440154', '#482878', '#3e4989', '#31688e', '#26828e', '#35b779', '#6ece58', '#b5de2b'],
    'Cool': ['#0d47a1', '#1565c0', '#1976d2', '#1e88e5', '#2196f3', '#42a5f5', '#64b5f6', '#bbdefb'],
    'Warm': ['#fff8e1', '#ffe082', '#ffd54f', '#ffca28', '#fbc02d', '#f9a825', '#f57f17', '#ff6f00'],
}

# ============================================================================
# PAGE TITLE AND DESCRIPTION
# ============================================================================

st.title("🗺️ Production Choropleth Map")
st.write("""
Interactive choropleth map showing mineral production intensity by country.
Customize colors, visualization styles, and data normalization to explore patterns.
""")

# ============================================================================
# DATA SOURCE AVAILABILITY MAPPING
# ============================================================================

SOURCE_AVAILABILITY = {
    'titanium_minerals': ['USGS', 'BGS'],
    'zircon': ['BGS'],
    'rare_earth_elements': ['BGS']
}

# ============================================================================
# GLOBAL FILTERS (Sidebar)
# ============================================================================

st.sidebar.title("🔍 Global Filters")

commodity = st.sidebar.selectbox(
    "📦 Commodity",
    options=['titanium_minerals', 'zircon', 'rare_earth_elements'],
    format_func=lambda x: x.replace('_', ' ').title(),
    key="geo_commodity"
)

year = st.sidebar.slider(
    "📅 Year",
    min_value=1950,
    max_value=2023,
    value=2020,
    step=1,
    key="geo_year"
)

available_sources = SOURCE_AVAILABILITY.get(commodity, ['BGS'])
source_options = available_sources + ['All Sources']
data_source = st.sidebar.selectbox(
    "📊 Data Source",
    options=source_options,
    key="geo_data_source"
)

# ============================================================================
# VISUALIZATION OPTIONS
# ============================================================================

st.subheader("🎨 Visualization Options")

viz_options = st.columns(4)

with viz_options[0]:
    color_palette = st.selectbox(
        "Color Palette",
        options=list(COLOR_PALETTES.keys()),
        key="color_palette"
    )

with viz_options[1]:
    normalization = st.selectbox(
        "Data Normalization",
        options=['Absolute Production', 'Normalized (0-1)', 'Production Intensity'],
        key="normalization"
    )

with viz_options[2]:
    marker_style = st.selectbox(
        "Marker Style",
        options=['Circle Markers', 'Counter Style', 'Heatmap Intensity'],
        key="marker_style"
    )

with viz_options[3]:
    size_multiplier = st.slider(
        "Marker Size",
        min_value=0.5,
        max_value=3.0,
        value=1.0,
        step=0.1,
        key="size_multiplier"
    )

# ============================================================================
# PRODUCTION CHOROPLETH MAP
# ============================================================================

st.subheader(f"📊 {commodity.replace('_', ' ').title()} Production Map - {year}")

# Determine which source to filter by
selected_source = None if data_source == 'All Sources' else data_source

# Get production data with source filter
prod_df = get_production_data(
    commodity=commodity,
    year_min=year,
    year_max=year,
    data_source=selected_source
)

if not prod_df.empty:
    # Aggregate by country (preserving source info)
    country_prod = prod_df.groupby(['country_iso3']).agg({
        'quantity': 'sum',
        'data_source': lambda x: ', '.join(x.unique())  # Get unique sources for each country
    }).reset_index()
    country_prod.columns = ['iso3', 'production', 'sources']
    
    # Get country names
    countries_df = get_countries()
    country_prod = country_prod.merge(countries_df[['iso3', 'name']], on='iso3', how='left')
    
    # Apply normalization
    if normalization == 'Normalized (0-1)':
        min_prod = country_prod['production'].min()
        max_prod = country_prod['production'].max()
        country_prod['normalized_production'] = (country_prod['production'] - min_prod) / (max_prod - min_prod)
    elif normalization == 'Production Intensity':
        # Production intensity: production per country (log scale for better visualization)
        country_prod['normalized_production'] = np.log1p(country_prod['production']) / np.log1p(country_prod['production'].max())
    else:
        # Absolute production
        max_prod = country_prod['production'].max()
        country_prod['normalized_production'] = country_prod['production'] / max_prod
    
    # Create map
    m = folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles='OpenStreetMap'
    )
    
    # Get color palette
    palette = COLOR_PALETTES[color_palette]
    
    # Add country markers with visualization based on selected style
    for _, row in country_prod.iterrows():
        # Get country centroid coordinates
        lat, lon = get_country_centroid(row['iso3'])
        
        # Get color based on normalized production value
        color_index = int(row['normalized_production'] * (len(palette) - 1))
        color_index = min(max(color_index, 0), len(palette) - 1)
        marker_color = palette[color_index]
        
        if marker_style == 'Circle Markers':
            # Traditional circle markers with variable size
            radius = max(3, min(25, (row['normalized_production'] * 20) * size_multiplier))
            
            folium.CircleMarker(
                location=[lat, lon],
                radius=radius,
                popup=f"""
                    <b>{row['name']}</b><br>
                    Production: {row['production']:,.0f} tonnes<br>
                    Normalized: {row['normalized_production']:.2%}<br>
                    <i>Source: {row['sources']}</i>
                """,
                tooltip=row['name'],
                color=marker_color,
                fill=True,
                fillColor=marker_color,
                fillOpacity=0.8,
                weight=2
            ).add_to(m)
        
        elif marker_style == 'Counter Style':
            # Counter-style markers with text labels
            radius = max(8, min(20, (row['normalized_production'] * 15) * size_multiplier))
            
            # Create custom HTML for counter-style appearance
            folium.CircleMarker(
                location=[lat, lon],
                radius=radius,
                popup=f"""
                    <b>{row['name']}</b><br>
                    Production: {row['production']:,.0f} tonnes<br>
                    Normalized: {row['normalized_production']:.2%}<br>
                    <i>Source: {row['sources']}</i>
                """,
                tooltip=row['name'],
                color='#333',
                fill=True,
                fillColor=marker_color,
                fillOpacity=0.85,
                weight=2.5
            ).add_to(m)
        
        elif marker_style == 'Heatmap Intensity':
            # Heatmap-style with gradient intensity
            opacity = 0.4 + (row['normalized_production'] * 0.6)  # Opacity between 0.4 and 1.0
            radius = max(5, min(30, (row['normalized_production'] * 25) * size_multiplier))
            
            folium.CircleMarker(
                location=[lat, lon],
                radius=radius,
                popup=f"""
                    <b>{row['name']}</b><br>
                    Production: {row['production']:,.0f} tonnes<br>
                    Intensity: {row['normalized_production']:.2%}<br>
                    <i>Source: {row['sources']}</i>
                """,
                tooltip=row['name'],
                color=marker_color,
                fill=True,
                fillColor=marker_color,
                fillOpacity=opacity,
                weight=1
            ).add_to(m)
    
    # Display map
    st_folium(m, width=1200, height=650)
    
    # Additional visualization: Production distribution chart
    st.subheader("📊 Production Distribution by Country")
    
    tabs = st.tabs(["Top 20 Countries", "All Countries"])
    
    with tabs[0]:
        display_df = country_prod[['name', 'production', 'sources']].copy()
        display_df.columns = ['Country', 'Production (tonnes)', 'Data Source']
        display_df = display_df.sort_values('Production (tonnes)', ascending=False).head(20)
        display_df['Production (tonnes)'] = display_df['Production (tonnes)'].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    with tabs[1]:
        display_df = country_prod[['name', 'production', 'sources']].copy()
        display_df.columns = ['Country', 'Production (tonnes)', 'Data Source']
        display_df = display_df.sort_values('Production (tonnes)', ascending=False)
        display_df['Production (tonnes)'] = display_df['Production (tonnes)'].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    
else:
    st.warning(f"No production data available for {commodity.replace('_', ' ').title()} in {year}")

# ============================================================================
# INFO BOX
# ============================================================================

st.markdown("---")
st.info("""
💡 **Choropleth Map Features:**
- **Color Palettes:** Choose from 8 different color schemes (Reds, Greens, Blues, Purples, Oranges, Viridis, Cool, Warm)
- **Data Normalization:** View data as absolute values, normalized (0-1 scale), or production intensity (log scale)
- **Marker Styles:** 
  - 🔵 **Circle Markers** - Traditional bubble map with variable sizing
  - 🏷️ **Counter Style** - Pronounced markers with distinct outlines
  - 🔥 **Heatmap Intensity** - Gradient opacity showing production concentration
- **Marker Size:** Adjust marker sizes with the multiplier slider for custom visualization preferences
- **Data Source:** Select between USGS, BGS, or view all available sources combined
  - 🔬 **Titanium Minerals** → USGS & BGS
  - ⚪ **Zircon** → BGS only
  - 🌟 **Rare Earth Elements** → BGS only
- Hover over markers to see country names; click for detailed production data including data source
""")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 12px;">
    <b>Production Choropleth Map Module</b> | Folium + Streamlit<br>
    Last updated: February 2026<br>
    <i>Data sources: USGS (U.S. Geological Survey) & BGS (British Geological Survey)</i>
</div>
""", unsafe_allow_html=True)
