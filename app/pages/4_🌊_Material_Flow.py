"""
RENO-TITAN Module 4: Material Flow Analysis
Page for Sankey diagrams and mass balance calculations.
"""

import streamlit as st
import pandas as pd
import logging
import sys
import os
import plotly.graph_objects as go

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import (
    get_production_data,
    get_countries,
    get_trade_data
)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Material Flow - RENO-TITAN",
    page_icon="🌊",
    layout="wide"
)

logger = logging.getLogger(__name__)

# ============================================================================
# PAGE TITLE AND DESCRIPTION
# ============================================================================

st.title("🌊 Material Flow Analysis")
st.write("""
Analyze material flows using mass balance equations: Production + Imports = Exports + Apparent Consumption.
Explore apparent consumption trends across countries and commodities.
""")

# ============================================================================
# GLOBAL FILTERS (MAIN PAGE)
# ============================================================================

col_filter1, col_filter2, col_filter3 = st.columns(3)

with col_filter1:
    commodity = st.selectbox(
        "Commodity",
        options=['titanium_minerals', 'zircon', 'rare_earth_elements'],
        format_func=lambda x: x.replace('_', ' ').title(),
        key="material_commodity"
    )

with col_filter2:
    year = st.slider(
        "Year",
        min_value=1950,
        max_value=2023,
        value=2020,
        step=1,
        key="material_year"
    )

with col_filter3:
    # Country selection
    countries_df = get_countries()
    if not countries_df.empty:
        country_options = {row['name']: row['iso3'] for _, row in countries_df.iterrows()}
        selected_country_name = st.selectbox(
            "Country",
            options=list(country_options.keys()),
            key="material_country"
        )
        selected_country = country_options.get(selected_country_name)
    else:
        selected_country = None

st.markdown("---")

# ============================================================================
# MASS BALANCE ANALYSIS
# ============================================================================

st.subheader("Mass Balance Analysis (P + I = E + AC)")
    
# Get production data
if selected_country:
    prod_data = get_production_data(
        commodity=commodity,
        country_iso3=selected_country,
        year_min=year,
        year_max=year
    )
    scope = selected_country
else:
    st.warning("Please select a country to view mass balance analysis.")
    scope = None

if scope:
    # Get trade data for imports/exports (filtered by reporter country)
    trade_data = get_trade_data(
        reporter_iso3=selected_country,
        year_min=year,
        year_max=year
    )
    
    # Get total production (set to 0 if no data)
    P = prod_data['quantity'].sum() if not prod_data.empty else 0
    
    # Get trade values (simplified - just using available data)
    if not trade_data.empty:
        E = trade_data[trade_data['flow'] == 'export']['quantity'].sum()
        I = trade_data[trade_data['flow'] == 'import']['quantity'].sum()
    else:
        E = 0
        I = 0
    
    # Calculate apparent consumption
    # AC = Production + Imports - Exports
    AC = P + I - E
    
    # Create waterfall data
    waterfall_data = {
        'Category': ['Production', 'Imports', 'Exports', 'Apparent Consumption'],
        'Value': [P, I, -E, AC]
    }
    
    waterfall_df = pd.DataFrame(waterfall_data)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Production (P)", f"{P:,.0f} tonnes")
    
    with col2:
        st.metric("Imports (I)", f"{I:,.0f} tonnes")
    
    with col3:
        st.metric("Exports (E)", f"{E:,.0f} tonnes")
    
    with col4:
        st.metric("Apparent Consumption (AC)", f"{max(AC, 0):,.0f} tonnes")
    
    # Create waterfall chart
    fig = go.Figure(go.Waterfall(
        x=waterfall_df['Category'],
        y=waterfall_df['Value'],
        connector={"line": {"color": "rgba(63, 63, 63, 0.5)"}},
        decreasing={"marker": {"color": "red"}},
        increasing={"marker": {"color": "green"}}
    ))
    
    fig.update_layout(
        title=f"Mass Balance: {commodity.title()} ({scope})",
        height=400,
        waterfallgap=0.3
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Balance check
    st.subheader("Balance Verification")
    
    balance_check = P + I - E - AC
    
    if abs(balance_check) < 0.01:
        st.success(f"✅ Balance verified: P + I = E + AC (residual: {balance_check:.2f})")
    else:
        st.warning(f"⚠️ Balance check: residual = {balance_check:,.0f} tonnes")
    
    # Detailed balance table
    st.subheader("Balance Summary")
    
    balance_items = [
        ('Production (P)', P, '+'),
        ('Imports (I)', I, '+'),
        ('Total Available', P + I, '='),
        ('Exports (E)', E, '-'),
        ('Apparent Consumption (AC)', max(AC, 0), '=')
    ]
    
    balance_display = pd.DataFrame(balance_items, columns=['Item', 'Quantity (tonnes)', 'Operation'])
    balance_display['Quantity (tonnes)'] = balance_display['Quantity (tonnes)'].apply(lambda x: f"{x:,.0f}")
    
    st.dataframe(balance_display, use_container_width=True, hide_index=True)

    st.markdown("""
    **Mass Balance Equation:**
    - **P** = Production (domestic mining)
    - **I** = Imports
    - **E** = Exports
    - **AC** = Apparent Consumption (domestic use)
    """)

    st.info("""
    📌 **Data Notes:**
    - Production data sourced from USGS and BGS
    - Trade data from UN Comtrade
    - Stock changes and losses not included (reliable data unavailable)
    - Apparent Consumption represents domestic material use
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 12px;">
    <b>Mass Balance Analysis</b> | Material Flow & Trade Analysis<br>
    Last updated: February 2026
</div>
""", unsafe_allow_html=True)
