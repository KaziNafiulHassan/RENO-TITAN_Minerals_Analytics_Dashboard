"""
RENO-TITAN Module 1: Production Analysis
Page for analyzing and comparing mineral production data from USGS and BGS.
"""

import streamlit as st
import pandas as pd
import logging
from typing import Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import (
    get_production_data,
    get_top_producers,
    get_production_comparison,
    get_countries
)
from utils.visualizations import (
    plot_top_producers,
    plot_production_trend,
    plot_comparison_bars
)
from utils.calculations import calculate_discrepancy_percentage

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Production Analysis - RENO-TITAN",
    page_icon="📊",
    layout="wide"
)

logger = logging.getLogger(__name__)

# ============================================================================
# PAGE TITLE AND DESCRIPTION
# ============================================================================

st.title("📊 Production Analysis")
st.write("""
Compare mineral production trends across different data sources (USGS vs BGS).
Identify top producers, analyze trends over time, and detect discrepancies.
""")

# ============================================================================
# SIDEBAR FILTERS
# ============================================================================

with st.sidebar:
    st.header("Filters")
    
    commodity = st.selectbox(
        "Commodity",
        options=['titanium_minerals', 'zircon', 'rare_earth_elements'],
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    year_range = st.slider(
        "Year Range",
        min_value=1950,
        max_value=2023,
        value=(2010, 2023),
        step=1
    )
    
    show_comparison = st.checkbox(
        "Show USGS vs BGS Comparison",
        value=True
    )

# ============================================================================
# MAIN CONTENT - TAB 1: TOP PRODUCERS
# ============================================================================

tab1, tab2, tab3 = st.tabs(["Top Producers", "Trend Analysis", "Source Comparison"])

with tab1:
    st.subheader("Top 10 Producers by Year")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        selected_year = st.slider(
            "Select Year",
            min_value=year_range[0],
            max_value=year_range[1],
            value=year_range[1],
            key="top_producers_year"
        )
    
    with col1:
        # Get top producers
        df_top = get_production_data(
            commodity=commodity,
            year_min=selected_year,
            year_max=selected_year
        )
        
        if not df_top.empty:
            # Group by country and sum
            df_grouped = df_top.groupby(['country_iso3']).agg({
                'quantity': 'sum',
                'unit': 'first'
            }).reset_index().sort_values('quantity', ascending=False).head(10)
            
            df_grouped.columns = ['Country', 'Production', 'Unit']
            
            # Display chart
            fig = plot_top_producers(df_grouped, commodity, selected_year)
            st.plotly_chart(fig, use_container_width=True)
            
            # Display table
            st.subheader("Table View")
            df_display = df_grouped.copy()
            df_display['Production'] = df_display['Production'].apply(
                lambda x: f"{x:,.0f}"
            )
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # Download button
            csv = df_grouped.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"top_producers_{commodity}_{selected_year}.csv",
                mime="text/csv"
            )
        else:
            st.warning(f"No production data available for {commodity} in {selected_year}")

# ============================================================================
# TAB 2: TREND ANALYSIS
# ============================================================================

with tab2:
    st.subheader("Production Trends Over Time")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        # Country multi-select
        countries_df = get_countries()
        if not countries_df.empty:
            countries_list = countries_df['Country'].unique() if 'Country' in countries_df.columns else countries_df['iso3'].unique()
            selected_countries = st.multiselect(
                "Select Countries",
                options=sorted(countries_list),
                default=sorted(countries_list)[:5] if len(countries_list) > 5 else sorted(countries_list),
                max_selections=10
            )
        else:
            selected_countries = None
    
    with col1:
        # Get trend data
        df_trend = get_production_data(
            commodity=commodity,
            year_min=year_range[0],
            year_max=year_range[1]
        )
        
        if not df_trend.empty:
            # Filter by selected countries if provided
            if selected_countries:
                df_trend = df_trend[df_trend['country_iso3'].isin(selected_countries)]
            
            if not df_trend.empty:
                # Create trend chart
                fig = plot_production_trend(df_trend, commodity)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No data for selected countries")
        else:
            st.warning(f"No production data available for {commodity}")

# ============================================================================
# TAB 3: SOURCE COMPARISON (USGS vs BGS)
# ============================================================================

with tab3:
    if show_comparison:
        st.subheader("USGS vs BGS Comparison")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            # Select country for comparison
            countries_df = get_countries()
            if not countries_df.empty:
                country_list = sorted(countries_df['Country'].unique() if 'Country' in countries_df.columns else countries_df['iso3'].unique())
                selected_country = st.selectbox(
                    "Select Country",
                    options=country_list,
                    key="comparison_country"
                )
                # Try to extract ISO3 if we have a country name
                if 'Country' in countries_df.columns:
                    country_iso3 = countries_df[countries_df['Country'] == selected_country]['iso3'].values[0] if len(countries_df[countries_df['Country'] == selected_country]) > 0 else selected_country
                else:
                    country_iso3 = selected_country
            else:
                st.warning("Countries table not populated")
                country_iso3 = None
        
        with col1:
            if country_iso3:
                # Get comparison data
                df_comp = get_production_data(
                    commodity=commodity,
                    country_iso3=country_iso3,
                    year_min=year_range[0],
                    year_max=year_range[1]
                )
                
                if not df_comp.empty:
                    # Pivot to compare sources
                    df_pivot = df_comp.pivot_table(
                        index='year',
                        columns='data_source',
                        values='quantity',
                        aggfunc='sum'
                    ).reset_index()
                    
                    # Display comparison chart
                    fig = plot_comparison_bars(df_pivot, commodity)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show discrepancies
                    st.subheader("Discrepancy Analysis")
                    
                    df_pivot_copy = df_pivot.copy()
                    for col in ['USGS', 'BGS']:
                        if col not in df_pivot_copy.columns:
                            df_pivot_copy[col] = 0
                    
                    df_pivot_copy['Discrepancy %'] = df_pivot_copy.apply(
                        lambda row: calculate_discrepancy_percentage(
                            row.get('USGS', 0),
                            row.get('BGS', 0)
                        ),
                        axis=1
                    )
                    
                    # Highlight rows with >15% discrepancy
                    def highlight_discrepancy(val):
                        if val > 15:
                            return 'background-color: #ffcccc'
                        elif val > 10:
                            return 'background-color: #ffffcc'
                        else:
                            return ''
                    
                    display_cols = ['year', 'USGS', 'BGS', 'Discrepancy %']
                    df_display = df_pivot_copy[[col for col in display_cols if col in df_pivot_copy.columns]].copy()
                    
                    # Format numeric columns
                    for col in ['USGS', 'BGS']:
                        if col in df_display.columns:
                            df_display[col] = df_display[col].apply(lambda x: f"{x:,.0f}")
                    
                    df_display['Discrepancy %'] = df_pivot_copy['Discrepancy %'].apply(lambda x: f"{x:.1f}%")
                    
                    st.dataframe(
                        df_display,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Key insights
                    with st.expander("📊 Key Insights"):
                        avg_discrepancy = df_pivot_copy['Discrepancy %'].mean()
                        max_discrepancy = df_pivot_copy['Discrepancy %'].max()
                        high_disc_count = (df_pivot_copy['Discrepancy %'] > 15).sum()
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Average Discrepancy", f"{avg_discrepancy:.1f}%")
                        with col2:
                            st.metric("Maximum Discrepancy", f"{max_discrepancy:.1f}%")
                        with col3:
                            st.metric("High Disc. Years (>15%)", f"{high_disc_count}")
                        
                        if avg_discrepancy > 10:
                            st.warning(
                                f"⚠️ High discrepancy between USGS and BGS for {selected_country}. "
                                f"Average difference is {avg_discrepancy:.1f}%. "
                                f"Consider reviewing data quality."
                            )
                else:
                    st.info(f"No data available for {selected_country}")
    else:
        st.info("Enable 'Show USGS vs BGS Comparison' in sidebar to view comparison")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("Data sources: USGS Mineral Commodity Summaries, BGS World Mineral Statistics")
