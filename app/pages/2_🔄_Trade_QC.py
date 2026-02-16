"""
RENO-TITAN Module 2: Trade QC Analysis
Page for analyzing trade flows and comparing imports vs exports by country.
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
    get_trade_statistics,
    get_hs_codes,
    get_countries,
    get_country_name
)

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

st.title("🔄 Trade QC Analysis")
st.write("""
Analyze bilateral trade flows between countries, compare imports vs exports,
and identify trade patterns for critical minerals.
""")

# ============================================================================
# GLOBAL FILTERS
# ============================================================================

st.subheader("Filters")

filter_col1, filter_col2, filter_col3 = st.columns(3)

# Get available HS codes
hs_df = get_hs_codes()
with filter_col1:
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

with filter_col2:
    year_range = st.slider(
        "Year Range",
        min_value=1992,
        max_value=2023,
        value=(2000, 2023),
        step=1
    )

# Country filter
countries_df = get_countries()
with filter_col3:
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

st.markdown("---")

# ============================================================================
# TAB LAYOUT
# ============================================================================

tab1, tab2 = st.tabs(["Trade Overview", "Imports vs Exports"])

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
# TAB 2: IMPORTS VS EXPORTS BY COUNTRY
# ============================================================================

with tab2:
    st.subheader("Annual Imports vs Exports by Country")
    
    trade_df = get_trade_data(
        hs_code=selected_hs_code,
        year_min=year_range[0],
        year_max=year_range[1]
    )
    
    if not trade_df.empty:
        # Debug: Show data structure
        with st.expander("📊 Data Debug Info"):
            st.write(f"Total records: {len(trade_df)}")
            st.write(f"Columns: {list(trade_df.columns)}")
            if 'flow' in trade_df.columns:
                st.write(f"Flow values: {trade_df['flow'].unique()}")
                st.write(f"Flow value counts:\n{trade_df['flow'].value_counts()}")
            else:
                st.warning("⚠️ 'flow' column not found in trade data!")
            st.write(f"Sample data:\n{trade_df.head()}")
        
        # Properly filter imports and exports by flow column
        if 'flow' in trade_df.columns:
            # Filter by flow type
            export_df = trade_df[trade_df['flow'].str.lower() == 'export']
            import_df = trade_df[trade_df['flow'].str.lower() == 'import']
            
            st.info(f"Export records: {len(export_df)} | Import records: {len(import_df)}")
        else:
            # Fallback if flow column missing: use reporter/partner assumption
            export_df = trade_df
            import_df = trade_df
            st.warning("Using reporter/partner assumption for exports/imports")
        
        # Get unique countries
        all_countries = pd.concat([
            trade_df['reporter_iso3'],
            trade_df['partner_iso3']
        ]).unique()
        
        # Remove NaN values and sort
        all_countries = [c for c in all_countries if pd.notna(c)]
        
        # Country selector for detailed view
        country_display_options = ["All Countries (Top 10)"] + sorted(all_countries)
        selected_country_display = st.selectbox(
            "Select Country for Detailed View",
            options=country_display_options,
            key="imports_exports_country"
        )
        
        if selected_country_display == "All Countries (Top 10)":
            # Calculate exports by country (reporter who exported)
            if 'flow' in export_df.columns:
                exports_by_country = export_df.groupby(['reporter_iso3', 'year'])['value_usd'].sum().reset_index()
            else:
                exports_by_country = export_df.groupby(['reporter_iso3', 'year'])['value_usd'].sum().reset_index()
            exports_by_country.columns = ['country_iso3', 'year', 'export_value']
            
            # Calculate imports by country (reporter who imported)
            if 'flow' in import_df.columns:
                imports_by_country = import_df.groupby(['reporter_iso3', 'year'])['value_usd'].sum().reset_index()
            else:
                # Fallback: use partner_iso3
                imports_by_country = import_df.groupby(['partner_iso3', 'year'])['value_usd'].sum().reset_index()
            imports_by_country.columns = ['country_iso3', 'year', 'import_value']
            
            # Merge exports and imports
            country_trade = exports_by_country.merge(imports_by_country, on=['country_iso3', 'year'], how='outer').fillna(0)
            
            # Get top 10 exporters
            top_exporters = exports_by_country.groupby('country_iso3')['export_value'].sum().nlargest(10).index.tolist()
            
            # Filter to top 10 exporters
            country_trade_top = country_trade[country_trade['country_iso3'].isin(top_exporters)].copy()
            
            # Create side-by-side columns
            col_exp, col_imp = st.columns(2)
            
            with col_exp:
                st.write("**Total Annual Exports by Country (Top 10)**")
                
                exp_pivot = country_trade_top.pivot_table(
                    index='country_iso3',
                    columns='year',
                    values='export_value',
                    aggfunc='sum'
                )
                
                import plotly.graph_objects as go
                fig_exp = go.Figure()
                
                for country in exp_pivot.index:
                    fig_exp.add_trace(go.Scatter(
                        x=exp_pivot.columns,
                        y=exp_pivot.loc[country],
                        mode='lines+markers',
                        name=country
                    ))
                
                fig_exp.update_layout(
                    title="Export Trends (Top 10 Exporters)",
                    xaxis_title="Year",
                    yaxis_title="Export Value (USD)",
                    height=450,
                    hovermode='x unified'
                )
                st.plotly_chart(fig_exp, use_container_width=True)
            
            with col_imp:
                st.write("**Total Annual Imports by Country (Top 10)**")
                
                imp_pivot = country_trade_top.pivot_table(
                    index='country_iso3',
                    columns='year',
                    values='import_value',
                    aggfunc='sum'
                )
                
                fig_imp = go.Figure()
                
                for country in imp_pivot.index:
                    fig_imp.add_trace(go.Scatter(
                        x=imp_pivot.columns,
                        y=imp_pivot.loc[country],
                        mode='lines+markers',
                        name=country
                    ))
                
                fig_imp.update_layout(
                    title="Import Trends (Top 10 Exporters)",
                    xaxis_title="Year",
                    yaxis_title="Import Value (USD)",
                    height=450,
                    hovermode='x unified'
                )
                st.plotly_chart(fig_imp, use_container_width=True)
        
        else:
            # Single country detailed view
            country_iso = selected_country_display
            
            # Get exports for this country (where they are the reporter and flow='export')
            if 'flow' in export_df.columns:
                country_exports = export_df[export_df['reporter_iso3'] == country_iso].groupby('year')['value_usd'].sum().reset_index()
            else:
                country_exports = export_df[export_df['reporter_iso3'] == country_iso].groupby('year')['value_usd'].sum().reset_index()
            country_exports.columns = ['year', 'value']
            country_exports['type'] = 'Exports'
            
            # Get imports for this country (where they are the reporter and flow='import')
            if 'flow' in import_df.columns:
                country_imports = import_df[import_df['reporter_iso3'] == country_iso].groupby('year')['value_usd'].sum().reset_index()
            else:
                # Fallback: where they are the partner_iso3
                country_imports = import_df[import_df['partner_iso3'] == country_iso].groupby('year')['value_usd'].sum().reset_index()
            country_imports.columns = ['year', 'value']
            country_imports['type'] = 'Imports'
            
            # Combine
            country_flow_df = pd.concat([country_exports, country_imports], ignore_index=True)
            
            if not country_flow_df.empty:
                # Side-by-side columns
                col_chart, col_table = st.columns([2, 1])
                
                with col_chart:
                    st.write(f"**Imports vs Exports for {country_iso}**")
                    
                    import plotly.graph_objects as go
                    fig = go.Figure()
                    
                    exports_data = country_flow_df[country_flow_df['type'] == 'Exports'].sort_values('year')
                    imports_data = country_flow_df[country_flow_df['type'] == 'Imports'].sort_values('year')
                    
                    fig.add_trace(go.Bar(
                        x=exports_data['year'],
                        y=exports_data['value'],
                        name='Exports',
                        marker=dict(color='#2E7D32')
                    ))
                    
                    fig.add_trace(go.Bar(
                        x=imports_data['year'],
                        y=imports_data['value'],
                        name='Imports',
                        marker=dict(color='#1565C0')
                    ))
                    
                    fig.update_layout(
                        title=f"Annual Imports vs Exports - {country_iso}",
                        xaxis_title="Year",
                        yaxis_title="Trade Value (USD)",
                        barmode='group',
                        height=450,
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_table:
                    st.write("**Summary**")
                    
                    total_exports = exports_data['value'].sum() if not exports_data.empty else 0
                    total_imports = imports_data['value'].sum() if not imports_data.empty else 0
                    balance = total_exports - total_imports
                    
                    summary_data = {
                        'Metric': ['Total Exports', 'Total Imports', 'Trade Balance'],
                        'Value (USD)': [
                            f"${total_exports:,.0f}",
                            f"${total_imports:,.0f}",
                            f"${balance:,.0f}"
                        ]
                    }
                    summary_df = pd.DataFrame(summary_data)
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)
            else:
                st.warning(f"No trade data available for {country_iso} in the selected period")

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
