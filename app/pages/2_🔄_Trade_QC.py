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
    get_country_name,
    get_iso3_to_name_mapping
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

filter_col1, filter_col2 = st.columns(2)

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
    
    # Get ISO3 to country name mapping
    iso3_to_name = get_iso3_to_name_mapping()
    
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
        
        # ====================================================================
        # EXPORT PARTNERS ANALYSIS
        # ====================================================================
        
        st.subheader("Top 10 Exporting Countries")
        
        # Filter exports
        export_df_filtered = trade_df[trade_df['flow'].str.lower() == 'export'].copy()
        
        # Aggregate by reporter (the country exporting - sum across all years in range)
        exports_by_partner = export_df_filtered.groupby('reporter_iso3').agg({
            'quantity': 'sum',
            'value_usd': 'sum'
        }).reset_index()
        
        # Filter out zero quantities
        exports_by_partner = exports_by_partner[exports_by_partner['quantity'] > 0].copy()
        
        # Sort by quantity (descending) and get top 10
        exports_by_partner = exports_by_partner.sort_values('quantity', ascending=False).head(10).reset_index(drop=True)
        
        # Add rank column
        exports_by_partner.insert(0, 'Rank', range(1, len(exports_by_partner) + 1))
        
        # Map ISO3 to country names
        exports_by_partner['Partner'] = exports_by_partner['reporter_iso3'].map(
            lambda x: iso3_to_name.get(x, x)
        )
        
        # Format display columns
        exports_display = exports_by_partner[['Rank', 'Partner', 'quantity', 'value_usd']].copy()
        exports_display.columns = ['Rank', 'Country', 'Total Quantity (tonnes)', 'Total Value (USD)']
        exports_display['Total Quantity (tonnes)'] = exports_display['Total Quantity (tonnes)'].apply(
            lambda x: f"{x:,.0f}"
        )
        exports_display['Total Value (USD)'] = exports_display['Total Value (USD)'].apply(
            lambda x: f"${x:,.0f}" if x > 0 else "$0"
        )
        
        # Display with sorting
        st.dataframe(exports_display, use_container_width=True, hide_index=True)
        
        # Pie chart for exports
        export_chart_col1, export_chart_col2 = st.columns([1, 1])
        
        with export_chart_col1:
            st.write("**Export Distribution by Quantity**")
            
            # Prepare data for pie chart (top 10 + Other)
            export_pie_data = exports_by_partner[['Partner', 'quantity']].copy()
            export_pie_data.columns = ['Country', 'Quantity']
            
            # Calculate "Other" if there are more than top 10
            if len(export_df_filtered) > len(export_pie_data):
                other_qty = export_df_filtered[~export_df_filtered['reporter_iso3'].isin(
                    exports_by_partner['reporter_iso3']
                )]['quantity'].sum()
                
                if other_qty > 0:
                    other_row = pd.DataFrame({'Country': ['Other'], 'Quantity': [other_qty]})
                    export_pie_data = pd.concat([export_pie_data, other_row], ignore_index=True)
            
            import plotly.express as px
            fig_export_pie = px.pie(
                export_pie_data,
                values='Quantity',
                names='Country',
                title=f"Export Quantity by Country ({year_range[0]}-{year_range[1]})"
            )
            fig_export_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_export_pie, use_container_width=True)
        
        with export_chart_col2:
            st.write("**Export Distribution by Value**")
            
            # Value-based pie chart
            export_pie_value = exports_by_partner[['Partner', 'value_usd']].copy()
            export_pie_value.columns = ['Country', 'Value']
            
            # Calculate other value
            if len(export_df_filtered) > len(export_pie_value):
                other_value = export_df_filtered[~export_df_filtered['reporter_iso3'].isin(
                    exports_by_partner['reporter_iso3']
                )]['value_usd'].sum()
                
                if other_value > 0:
                    other_row = pd.DataFrame({'Country': ['Other'], 'Value': [other_value]})
                    export_pie_value = pd.concat([export_pie_value, other_row], ignore_index=True)
            
            fig_export_pie_val = px.pie(
                export_pie_value,
                values='Value',
                names='Country',
                title=f"Export Value by Country ({year_range[0]}-{year_range[1]})"
            )
            fig_export_pie_val.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_export_pie_val, use_container_width=True)
        
        # ====================================================================
        # IMPORT PARTNERS ANALYSIS
        # ====================================================================
        
        st.subheader("Top 10 Importing Countries")
        
        # Filter imports
        import_df_filtered = trade_df[trade_df['flow'].str.lower() == 'import'].copy()
        
        # Aggregate by reporter (the country importing)
        imports_by_partner = import_df_filtered.groupby('reporter_iso3').agg({
            'quantity': 'sum',
            'value_usd': 'sum'
        }).reset_index()
        
        # Filter out zero quantities
        imports_by_partner = imports_by_partner[imports_by_partner['quantity'] > 0].copy()
        
        # Sort by quantity (descending) and get top 10
        imports_by_partner = imports_by_partner.sort_values('quantity', ascending=False).head(10).reset_index(drop=True)
        
        # Add rank column
        imports_by_partner.insert(0, 'Rank', range(1, len(imports_by_partner) + 1))
        
        # Map ISO3 to country names
        imports_by_partner['Partner'] = imports_by_partner['reporter_iso3'].map(
            lambda x: iso3_to_name.get(x, x)
        )
        
        # Format display columns
        imports_display = imports_by_partner[['Rank', 'Partner', 'quantity', 'value_usd']].copy()
        imports_display.columns = ['Rank', 'Country', 'Total Quantity (tonnes)', 'Total Value (USD)']
        imports_display['Total Quantity (tonnes)'] = imports_display['Total Quantity (tonnes)'].apply(
            lambda x: f"{x:,.0f}"
        )
        imports_display['Total Value (USD)'] = imports_display['Total Value (USD)'].apply(
            lambda x: f"${x:,.0f}" if x > 0 else "$0"
        )
        
        # Display with sorting
        st.dataframe(imports_display, use_container_width=True, hide_index=True)
        
        # Pie chart for imports
        import_chart_col1, import_chart_col2 = st.columns([1, 1])
        
        with import_chart_col1:
            st.write("**Import Distribution by Quantity**")
            
            # Prepare data for pie chart (top 10 + Other)
            import_pie_data = imports_by_partner[['Partner', 'quantity']].copy()
            import_pie_data.columns = ['Country', 'Quantity']
            
            # Calculate "Other" if there are more than top 10
            if len(import_df_filtered) > len(import_pie_data):
                other_qty = import_df_filtered[~import_df_filtered['reporter_iso3'].isin(
                    imports_by_partner['reporter_iso3']
                )]['quantity'].sum()
                
                if other_qty > 0:
                    other_row = pd.DataFrame({'Country': ['Other'], 'Quantity': [other_qty]})
                    import_pie_data = pd.concat([import_pie_data, other_row], ignore_index=True)
            
            fig_import_pie = px.pie(
                import_pie_data,
                values='Quantity',
                names='Country',
                title=f"Import Quantity by Country ({year_range[0]}-{year_range[1]})"
            )
            fig_import_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_import_pie, use_container_width=True)
        
        with import_chart_col2:
            st.write("**Import Distribution by Value**")
            
            # Value-based pie chart
            import_pie_value = imports_by_partner[['Partner', 'value_usd']].copy()
            import_pie_value.columns = ['Country', 'Value']
            
            # Calculate other value
            if len(import_df_filtered) > len(import_pie_value):
                other_value = import_df_filtered[~import_df_filtered['reporter_iso3'].isin(
                    imports_by_partner['reporter_iso3']
                )]['value_usd'].sum()
                
                if other_value > 0:
                    other_row = pd.DataFrame({'Country': ['Other'], 'Value': [other_value]})
                    import_pie_value = pd.concat([import_pie_value, other_row], ignore_index=True)
            
            fig_import_pie_val = px.pie(
                import_pie_value,
                values='Value',
                names='Country',
                title=f"Import Value by Country ({year_range[0]}-{year_range[1]})"
            )
            fig_import_pie_val.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_import_pie_val, use_container_width=True)
        
        # ====================================================================
        # DOWNLOAD FULL DATA
        # ====================================================================
        
        st.markdown("---")
        st.subheader("Download Full Trade Data")
        
        csv = trade_df.to_csv(index=False)
        st.download_button(
            label="📥 Download All Trade Records as CSV",
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
    
    # Get ISO3 to country name mapping
    iso3_to_name = get_iso3_to_name_mapping()
    
    trade_df = get_trade_data(
        hs_code=selected_hs_code,
        year_min=year_range[0],
        year_max=year_range[1]
    )
    
    if not trade_df.empty:
        # Properly filter imports and exports by flow column
        if 'flow' in trade_df.columns:
            # Filter by flow type
            export_df = trade_df[trade_df['flow'].str.lower() == 'export']
            import_df = trade_df[trade_df['flow'].str.lower() == 'import']
            
            # Display data quality summary
            col_quality1, col_quality2, col_quality3 = st.columns(3)
            with col_quality1:
                st.metric("Total Trade Records", f"{len(trade_df):,}")
            with col_quality2:
                st.metric("Export Records", f"{len(export_df):,}")
            with col_quality3:
                st.metric("Import Records", f"{len(import_df):,}")
        else:
            # Fallback if flow column missing: use reporter/partner assumption
            export_df = trade_df
            import_df = trade_df
            st.warning("⚠️ Unable to distinguish between imports and exports in current data")
        
        # Get unique countries
        all_countries = pd.concat([
            trade_df['reporter_iso3'],
            trade_df['partner_iso3']
        ]).unique()
        
        # Remove NaN values and sort
        all_countries = [c for c in all_countries if pd.notna(c)]
        
        # Create mapping for display (ISO3 -> Country Name)
        country_display_mapping = {iso3: iso3_to_name.get(iso3, iso3) for iso3 in all_countries}
        
        # Country selector for detailed view
        country_options_list = sorted(all_countries, key=lambda x: country_display_mapping.get(x, x))
        country_display_options = ["All Countries (Top 10)"] + country_options_list
        
        selected_country_display = st.selectbox(
            "Select Country for Detailed View",
            options=country_display_options,
            format_func=lambda x: country_display_mapping.get(x, x) if x != "All Countries (Top 10)" else x,
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
                
                # Map ISO3 codes to country names for display
                exp_pivot.index = exp_pivot.index.map(lambda x: iso3_to_name.get(x, x))
                
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
                
                # Map ISO3 codes to country names for display
                imp_pivot.index = imp_pivot.index.map(lambda x: iso3_to_name.get(x, x))
                
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
            country_name = iso3_to_name.get(country_iso, country_iso)
            
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
                    st.write(f"**Imports vs Exports for {country_name}**")
                    
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
                        title=f"Annual Imports vs Exports - {country_name}",
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
                st.warning(f"No trade data available for {country_name} in the selected period")

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
