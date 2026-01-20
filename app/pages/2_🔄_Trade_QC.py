"""
RENO-TITAN Module 2: Trade QC & Route Analysis
Page for analyzing trade flows, detecting inconsistencies, and examining routes.
"""

import streamlit as st
import pandas as pd
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import (
    get_trade_data,
    get_top_trade_routes,
    get_trade_statistics,
    get_hs_codes,
    get_countries,
    get_country_name
)
from utils.visualizations import plot_top_routes, plot_unit_value_distribution
from utils.calculations import calculate_unit_values, identify_outliers

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Trade QC - RENO-TITAN",
    page_icon="🔄",
    layout="wide"
)

logger = logging.getLogger(__name__)

# ============================================================================
# PAGE TITLE AND DESCRIPTION
# ============================================================================

st.title("🔄 Trade QC & Route Analysis")
st.write("""
Analyze bilateral trade flows, identify top exporters/importers, detect pricing anomalies,
and analyze trade routes for critical minerals.
""")

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================

with st.sidebar:
    st.header("Filters")
    
    # Get available HS codes
    hs_df = get_hs_codes()
    if not hs_df.empty:
        hs_options = {f"{row['code']} - {row['description'][:40]}...": row['code'] 
                     for _, row in hs_df.iterrows()}
        hs_code = st.selectbox(
            "HS Code",
            options=list(hs_options.keys()),
            format_func=lambda x: x
        )
        selected_hs_code = hs_options[hs_code]
    else:
        selected_hs_code = "261400"  # Default titanium ore
        st.warning("No HS codes found in database")
    
    year_range = st.slider(
        "Year Range",
        min_value=1992,
        max_value=2023,
        value=(2000, 2023),
        step=1
    )
    
    # Country filter
    countries_df = get_countries()
    if not countries_df.empty:
        country_options = {row['name']: row['iso3'] for _, row in countries_df.iterrows()}
        selected_country_name = st.selectbox(
            "Focus Country (Optional)",
            options=["All Countries"] + list(country_options.keys()),
            key="trade_country"
        )
        selected_country = country_options.get(selected_country_name) if selected_country_name != "All Countries" else None
    else:
        selected_country = None

# ============================================================================
# TAB LAYOUT
# ============================================================================

tab1, tab2, tab3 = st.tabs(["Trade Overview", "Top Routes", "Price Analysis"])

# ============================================================================
# TAB 1: TRADE OVERVIEW
# ============================================================================

with tab1:
    st.subheader("Trade Statistics Summary")
    
    # Get trade data
    trade_df = get_trade_data(
        hs_code=selected_hs_code,
        year_min=year_range[0],
        year_max=year_range[1]
    )
    
    if not trade_df.empty:
        # Calculate statistics
        stats = get_trade_statistics(
            hs_code=selected_hs_code,
            year_min=year_range[0],
            year_max=year_range[1]
        )
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Trade Value",
                f"${stats['total_value']:,.0f}",
                delta="USD"
            )
        
        with col2:
            st.metric(
                "Total Quantity",
                f"{stats['total_quantity']:,.0f}",
                delta="tonnes"
            )
        
        with col3:
            st.metric(
                "Exporting Countries",
                f"{stats['num_exporters']}",
                delta="unique"
            )
        
        with col4:
            st.metric(
                "Avg Unit Value",
                f"${stats['avg_unit_value']:,.0f}",
                delta="per tonne"
            )
        
        # Trade data table
        st.subheader("Trade Records")
        
        display_df = trade_df[['hs_code', 'reporter_iso3', 'partner_iso3', 'year', 'flow', 'value_usd', 'quantity']].copy()
        display_df.columns = ['HS Code', 'Exporter', 'Importer', 'Year', 'Flow', 'Value (USD)', 'Quantity (tonnes)']
        
        # Format columns
        display_df['Value (USD)'] = display_df['Value (USD)'].apply(lambda x: f"${x:,.0f}")
        display_df['Quantity (tonnes)'] = display_df['Quantity (tonnes)'].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Download button
        csv = trade_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Trade Data as CSV",
            data=csv,
            file_name=f"trade_data_{selected_hs_code}_{year_range[0]}-{year_range[1]}.csv",
            mime="text/csv"
        )
    else:
        st.warning(f"No trade data available for HS code {selected_hs_code} in {year_range[0]}-{year_range[1]}")

# ============================================================================
# TAB 2: TOP TRADE ROUTES
# ============================================================================

with tab2:
    st.subheader("Top Trade Routes by Value")
    
    routes_df = get_top_trade_routes(
        hs_code=selected_hs_code,
        year=year_range[1],
        limit=15
    )
    
    if not routes_df.empty:
        # Chart
        fig = plot_top_routes(routes_df[['route', 'total_value_usd']], limit=15)
        st.plotly_chart(fig, use_container_width=True)
        
        # Table with details
        st.subheader("Route Details")
        
        routes_display = routes_df[['route', 'reporter_iso3', 'partner_iso3', 'total_value_usd', 'total_quantity']].copy()
        routes_display.columns = ['Route', 'Exporter', 'Importer', 'Total Value (USD)', 'Total Quantity (tonnes)']
        
        routes_display['Total Value (USD)'] = routes_display['Total Value (USD)'].apply(lambda x: f"${x:,.0f}")
        routes_display['Total Quantity (tonnes)'] = routes_display['Total Quantity (tonnes)'].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(routes_display, use_container_width=True, hide_index=True)
    else:
        st.warning("No route data available for selected filters")

# ============================================================================
# TAB 3: PRICE & UNIT VALUE ANALYSIS
# ============================================================================

with tab3:
    st.subheader("Unit Value Analysis & Outlier Detection")
    
    trade_df = get_trade_data(
        hs_code=selected_hs_code,
        year_min=year_range[0],
        year_max=year_range[1]
    )
    
    if not trade_df.empty:
        # Calculate unit values
        uv_df = calculate_unit_values(trade_df.copy())
        
        if not uv_df.empty:
            # Identify outliers
            uv_df['is_outlier'] = identify_outliers(uv_df['unit_value'], threshold=2.5)
            
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Avg Unit Value",
                    f"${uv_df['unit_value'].mean():,.0f}",
                    delta="per tonne"
                )
            
            with col2:
                st.metric(
                    "Median Unit Value",
                    f"${uv_df['unit_value'].median():,.0f}",
                    delta="per tonne"
                )
            
            with col3:
                st.metric(
                    "Min Unit Value",
                    f"${uv_df['unit_value'].min():,.0f}",
                    delta="per tonne"
                )
            
            with col4:
                st.metric(
                    "Max Unit Value",
                    f"${uv_df['unit_value'].max():,.0f}",
                    delta="per tonne"
                )
            
            # Unit value distribution chart
            st.subheader("Unit Value Distribution")
            
            fig = plot_unit_value_distribution(uv_df[['reporter_iso3', 'unit_value']].copy())
            st.plotly_chart(fig, use_container_width=True)
            
            # Outliers detection
            outliers = uv_df[uv_df['is_outlier']].copy()
            
            if not outliers.empty:
                st.subheader("⚠️ Price Anomalies (Outliers)")
                
                outlier_display = outliers[['reporter_iso3', 'partner_iso3', 'year', 'unit_value', 'quantity']].copy()
                outlier_display.columns = ['Exporter', 'Importer', 'Year', 'Unit Value (USD/tonne)', 'Quantity (tonnes)']
                
                outlier_display['Unit Value (USD/tonne)'] = outlier_display['Unit Value (USD/tonne)'].apply(lambda x: f"${x:,.0f}")
                outlier_display['Quantity (tonnes)'] = outlier_display['Quantity (tonnes)'].apply(lambda x: f"{x:,.0f}")
                
                st.dataframe(outlier_display, use_container_width=True, hide_index=True)
                
                st.info(f"Found {len(outliers)} price anomalies ({len(outliers)/len(uv_df)*100:.1f}% of records)")
            else:
                st.success("✅ No significant price anomalies detected")
            
            # Unit value trends over time
            st.subheader("Unit Value Trends")
            
            trend_df = uv_df.groupby('year').agg({
                'unit_value': ['mean', 'median']
            }).reset_index()
            trend_df.columns = ['Year', 'Average', 'Median']
            
            import plotly.graph_objects as go
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=trend_df['Year'],
                y=trend_df['Average'],
                mode='lines+markers',
                name='Average Unit Value'
            ))
            
            fig.add_trace(go.Scatter(
                x=trend_df['Year'],
                y=trend_df['Median'],
                mode='lines+markers',
                name='Median Unit Value',
                line=dict(dash='dash')
            ))
            
            fig.update_layout(
                title="Unit Value Trends Over Time",
                xaxis_title="Year",
                yaxis_title="Unit Value (USD/tonne)",
                height=400,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Cannot calculate unit values - insufficient data")
    else:
        st.warning("No trade data available for selected filters")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 12px;">
    <b>Trade QC Module</b> | Data from UN Comtrade<br>
    Last updated: January 2026
</div>
""", unsafe_allow_html=True)
