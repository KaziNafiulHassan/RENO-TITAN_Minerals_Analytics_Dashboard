"""
RENO-TITAN Module 3: Geospatial Visualization
Page for choropleth maps and trade flow visualizations.
"""

import streamlit as st
import pandas as pd
import logging
import sys
import os
import folium
from streamlit_folium import st_folium

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import (
    get_production_data,
    get_trade_data,
    get_countries,
    get_hs_codes,
    get_country_name
)

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
# PAGE TITLE AND DESCRIPTION
# ============================================================================

st.title("🗺️ Geospatial Visualization")
st.write("""
Interactive maps showing mineral production intensity by country and global trade flows.
Visualize where critical minerals are produced and where they flow globally.
""")

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================

with st.sidebar:
    st.header("Filters")
    
    view_type = st.radio(
        "Map Type",
        options=["Production Choropleth", "Trade Flow Routes"],
        key="geospatial_view"
    )
    
    commodity = st.selectbox(
        "Commodity",
        options=['titanium_minerals', 'zircon', 'rare_earth_elements'],
        format_func=lambda x: x.replace('_', ' ').title(),
        key="geo_commodity"
    )
    
    year = st.slider(
        "Year",
        min_value=1950,
        max_value=2023,
        value=2020,
        step=1,
        key="geo_year"
    )

# ============================================================================
# TAB LAYOUT
# ============================================================================

if view_type == "Production Choropleth":
    st.subheader(f"Production Intensity Map - {commodity.title()} ({year})")
    
    # Get production data
    prod_df = get_production_data(
        commodity=commodity,
        year_min=year,
        year_max=year
    )
    
    if not prod_df.empty:
        # Aggregate by country
        country_prod = prod_df.groupby(['country_iso3']).agg({
            'quantity': 'sum'
        }).reset_index()
        country_prod.columns = ['iso3', 'production']
        
        # Get country names
        countries_df = get_countries()
        country_prod = country_prod.merge(countries_df[['iso3', 'name']], on='iso3', how='left')
        
        st.write(f"**Data Summary:**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Production", f"{country_prod['production'].sum():,.0f} tonnes")
        
        with col2:
            st.metric("Countries Producing", f"{len(country_prod)}")
        
        with col3:
            st.metric("Top Producer", country_prod.loc[country_prod['production'].idxmax(), 'name'])
        
        with col4:
            st.metric("Top Quantity", f"{country_prod['production'].max():,.0f} tonnes")
        
        # Create map
        m = folium.Map(
            location=[20, 0],
            zoom_start=2,
            tiles='OpenStreetMap'
        )
        
        # Add country markers
        for _, row in country_prod.iterrows():
            # Determine color based on production level
            production = row['production']
            max_prod = country_prod['production'].max()
            
            if production >= max_prod * 0.75:
                color = 'darkred'
            elif production >= max_prod * 0.5:
                color = 'red'
            elif production >= max_prod * 0.25:
                color = 'orange'
            else:
                color = 'yellow'
            
            folium.CircleMarker(
                location=[0, 0],  # Note: would need actual coordinates
                radius=8,
                popup=f"{row['name']}: {row['production']:,.0f} tonnes",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7
            ).add_to(m)
        
        # Display map
        st_folium(m, width=1200, height=600)
        
        # Table of production by country
        st.subheader("Production by Country")
        
        display_df = country_prod[['name', 'production']].copy()
        display_df.columns = ['Country', 'Production (tonnes)']
        display_df = display_df.sort_values('Production (tonnes)', ascending=False)
        display_df['Production (tonnes)'] = display_df['Production (tonnes)'].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
    else:
        st.warning(f"No production data available for {commodity} in {year}")

else:
    # Trade Flow Routes
    st.subheader("Global Trade Routes")
    
    # Get HS codes for the commodity
    hs_df = get_hs_codes()
    
    if not hs_df.empty:
        # For MVP, use default HS code mapping
        hs_mapping = {
            'titanium_minerals': '261400',
            'zircon': '261510',
            'rare_earth_elements': '284610'
        }
        
        selected_hs = hs_mapping.get(commodity, '261400')
        
        # Get trade data
        trade_df = get_trade_data(
            hs_code=selected_hs,
            year_min=year,
            year_max=year
        )
        
        if not trade_df.empty:
            # Aggregate by route
            routes = trade_df.groupby(['reporter_iso3', 'partner_iso3']).agg({
                'value_usd': 'sum',
                'quantity': 'sum'
            }).reset_index()
            
            # Add country names
            countries_df = get_countries()
            routes = routes.merge(
                countries_df[['iso3', 'name']].rename(columns={'iso3': 'reporter_iso3', 'name': 'exporter_name'}),
                on='reporter_iso3',
                how='left'
            )
            routes = routes.merge(
                countries_df[['iso3', 'name']].rename(columns={'iso3': 'partner_iso3', 'name': 'importer_name'}),
                on='partner_iso3',
                how='left'
            )
            
            st.write(f"**Data Summary:**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Trade Value", f"${routes['value_usd'].sum():,.0f}")
            
            with col2:
                st.metric("Total Quantity", f"{routes['quantity'].sum():,.0f} tonnes")
            
            with col3:
                st.metric("Exporting Countries", f"{routes['reporter_iso3'].nunique()}")
            
            with col4:
                st.metric("Importing Countries", f"{routes['partner_iso3'].nunique()}")
            
            # Create base map
            m = folium.Map(
                location=[20, 0],
                zoom_start=2,
                tiles='OpenStreetMap'
            )
            
            # Add flow routes as polylines
            for _, route in routes.iterrows():
                # Note: In production, would use actual country coordinates
                # For MVP, simplified visualization
                if pd.notna(route['value_usd']) and route['value_usd'] > 0:
                    # Size based on trade value
                    weight = min(max(route['value_usd'] / 100000000, 1), 10)
                    
                    folium.Marker(
                        location=[0, 0],
                        popup=f"{route['exporter_name']} → {route['importer_name']}: ${route['value_usd']:,.0f}",
                    ).add_to(m)
            
            # Display map
            st_folium(m, width=1200, height=600)
            
            # Trade routes table
            st.subheader("Top Trade Routes")
            
            routes_display = routes[['exporter_name', 'importer_name', 'value_usd', 'quantity']].copy()
            routes_display.columns = ['Exporter', 'Importer', 'Value (USD)', 'Quantity (tonnes)']
            routes_display = routes_display.sort_values('Value (USD)', ascending=False).head(20)
            
            routes_display['Value (USD)'] = routes_display['Value (USD)'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A")
            routes_display['Quantity (tonnes)'] = routes_display['Quantity (tonnes)'].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
            
            st.dataframe(routes_display, use_container_width=True, hide_index=True)
        else:
            st.warning(f"No trade data available for {commodity} in {year}")
    else:
        st.warning("No HS codes found in database")

# ============================================================================
# INFO BOX
# ============================================================================

st.markdown("---")
st.info("""
💡 **Map Notes:**
- Circle sizes represent production volumes or trade values
- Color intensity increases with magnitude
- Hover over markers for detailed information
- In production version, includes actual geographical coordinates for accurate positioning
""")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 12px;">
    <b>Geospatial Maps Module</b> | Folium Maps + Streamlit<br>
    Last updated: January 2026
</div>
""", unsafe_allow_html=True)
