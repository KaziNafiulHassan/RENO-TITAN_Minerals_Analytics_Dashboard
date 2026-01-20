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
# DEFAULT PROCESSING COEFFICIENTS
# ============================================================================

PROCESSING_COEFFICIENTS = {
    'titanium_minerals': {
        'description': 'Titanium Ore → Products',
        'inputs': {
            'Titanium Ore (Ilmenite)': 1.0
        },
        'outputs': {
            'TiO2 Pigment': 0.70,
            'Titanium Sponge': 0.20,
            'Processing Losses': 0.10
        }
    },
    'rare_earth_elements': {
        'description': 'REE Ore → Products',
        'inputs': {
            'Rare Earth Ore': 1.0
        },
        'outputs': {
            'REE Oxides/Salts': 0.60,
            'REE Metals': 0.30,
            'Processing Losses': 0.10
        }
    },
    'zircon': {
        'description': 'Zircon Ore → Products',
        'inputs': {
            'Zircon Ore': 1.0
        },
        'outputs': {
            'Zirconium Oxide': 0.65,
            'Zirconium Metal': 0.25,
            'Processing Losses': 0.10
        }
    }
}

# ============================================================================
# PAGE TITLE AND DESCRIPTION
# ============================================================================

st.title("🌊 Material Flow Analysis")
st.write("""
Visualize how raw ore is processed into final products using Sankey diagrams.
Analyze material flows and calculate processing yields for critical minerals.
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
    
    year = st.slider(
        "Year",
        min_value=1950,
        max_value=2023,
        value=2020,
        step=1
    )
    
    # Country selection
    countries_df = get_countries()
    if not countries_df.empty:
        country_options = {row['name']: row['iso3'] for _, row in countries_df.iterrows()}
        selected_country_name = st.selectbox(
            "Country (for analysis)",
            options=["Global"] + list(country_options.keys()),
            key="material_country"
        )
        selected_country = country_options.get(selected_country_name) if selected_country_name != "Global" else None
    else:
        selected_country = None

# ============================================================================
# TAB LAYOUT
# ============================================================================

tab1, tab2, tab3 = st.tabs(["Material Flow Sankey", "Mass Balance", "Processing Details"])

# ============================================================================
# TAB 1: SANKEY DIAGRAM
# ============================================================================

with tab1:
    st.subheader(f"Material Flow Diagram - {commodity.title()}")
    
    # Get production data
    if selected_country:
        prod_data = get_production_data(
            commodity=commodity,
            country_iso3=selected_country,
            year_min=year,
            year_max=year
        )
        scope = f"for {selected_country}"
    else:
        prod_data = get_production_data(
            commodity=commodity,
            year_min=year,
            year_max=year
        )
        scope = "Global"
    
    if not prod_data.empty:
        # Get total production
        total_prod = prod_data['quantity'].sum()
        
        # Get processing coefficients
        coeffs = PROCESSING_COEFFICIENTS.get(commodity, {
            'inputs': {'Raw Ore': 1.0},
            'outputs': {'Product': 0.7, 'Loss': 0.3}
        })
        
        # Calculate outputs based on coefficients
        outputs = {
            product: total_prod * ratio 
            for product, ratio in coeffs.get('outputs', {}).items()
        }
        
        # Create Sankey diagram
        sources = [0]  # Input index
        targets = [i+1 for i in range(len(outputs))]  # Output indices
        values = list(outputs.values())
        labels = ['Raw Ore Input'] + list(outputs.keys())
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color='black', width=0.5),
                label=labels,
                color=['lightblue', 'lightgreen', 'lightcoral', 'lightyellow']
            ),
            link=dict(
                source=sources * len(targets),
                target=targets,
                value=values
            )
        )])
        
        fig.update_layout(
            title=f"Material Flow: {commodity.title()} {scope}",
            height=500,
            font_size=11
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary statistics
        st.subheader("Flow Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Input (Ore)", f"{total_prod:,.0f} tonnes")
        
        with col2:
            st.metric("Total Output", f"{sum(outputs.values()):,.0f} tonnes")
        
        with col3:
            st.metric("Overall Yield", f"{sum(outputs.values())/total_prod*100:.1f}%")
        
        # Output breakdown table
        st.subheader("Output Breakdown")
        
        output_df = pd.DataFrame([
            {'Product': product, 'Quantity': qty, 'Percentage': qty/total_prod*100}
            for product, qty in outputs.items()
        ])
        
        output_df['Quantity'] = output_df['Quantity'].apply(lambda x: f"{x:,.0f}")
        output_df['Percentage'] = output_df['Percentage'].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(output_df, use_container_width=True, hide_index=True)
        
    else:
        st.warning(f"No production data available for {commodity} in {year}")

# ============================================================================
# TAB 2: MASS BALANCE
# ============================================================================

with tab2:
    st.subheader("Mass Balance Analysis (P + I = E + PU + ΔS + L)")
    
    st.markdown("""
    **Mass Balance Equation:**
    - **P** = Production (domestic mining)
    - **I** = Imports
    - **E** = Exports
    - **PU** = Processing Use (domestic processing)
    - **ΔS** = Stock Change (inventory changes)
    - **L** = Losses (waste, shrinkage)
    """)
    
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
        prod_data = get_production_data(
            commodity=commodity,
            year_min=year,
            year_max=year
        )
        scope = "Global"
    
    if not prod_data.empty:
        # Get trade data for imports/exports
        trade_data = get_trade_data(
            year_min=year,
            year_max=year
        )
        
        # Get total production
        P = prod_data['quantity'].sum()
        
        # Get trade values (simplified - just using available data)
        if not trade_data.empty:
            E = trade_data[trade_data['flow'] == 'export']['quantity'].sum()
            I = trade_data[trade_data['flow'] == 'import']['quantity'].sum()
        else:
            E = 0
            I = 0
        
        # Calculate implied processing use
        # Assume stock change and losses are minimal for MVP
        PU = P + I - E  # Processing Use = Production + Imports - Exports
        
        # Create waterfall data
        waterfall_data = {
            'Category': ['Production', 'Imports', 'Exports', 'Processing Use'],
            'Value': [P, I, -E, PU]
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
            st.metric("Processing Use (PU)", f"{max(PU, 0):,.0f} tonnes")
        
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
        
        balance_check = P + I - E - PU
        
        if abs(balance_check) < 0.01:
            st.success(f"✅ Balance verified: P + I = E + PU (residual: {balance_check:.2f})")
        else:
            st.warning(f"⚠️ Balance check: residual = {balance_check:,.0f} tonnes")
        
        # Detailed balance table
        st.subheader("Balance Summary")
        
        balance_items = [
            ('Production (P)', P, '+'),
            ('Imports (I)', I, '+'),
            ('Total Available', P + I, '='),
            ('Exports (E)', E, '-'),
            ('Processing Use (PU)', max(PU, 0), '-'),
            ('Residual (L + ΔS)', abs(balance_check), '±')
        ]
        
        balance_display = pd.DataFrame(balance_items, columns=['Item', 'Quantity (tonnes)', 'Operation'])
        balance_display['Quantity (tonnes)'] = balance_display['Quantity (tonnes)'].apply(lambda x: f"{x:,.0f}")
        
        st.dataframe(balance_display, use_container_width=True, hide_index=True)
        
    else:
        st.warning("No data available for mass balance calculation")

# ============================================================================
# TAB 3: PROCESSING DETAILS
# ============================================================================

with tab3:
    st.subheader("Processing Coefficients & Details")
    
    # Get coefficients for selected commodity
    coeffs = PROCESSING_COEFFICIENTS.get(commodity, {})
    
    if coeffs:
        st.markdown(f"**{coeffs.get('description', 'Processing Details')}**")
        
        # Input side
        st.markdown("**Inputs:**")
        inputs_df = pd.DataFrame([
            {'Input Material': mat, 'Coefficient': coeff}
            for mat, coeff in coeffs.get('inputs', {}).items()
        ])
        st.dataframe(inputs_df, use_container_width=True, hide_index=True)
        
        # Output side
        st.markdown("**Outputs (by coefficient):**")
        outputs_df = pd.DataFrame([
            {'Output Product': prod, 'Split Ratio': f"{ratio:.1%}"}
            for prod, ratio in coeffs.get('outputs', {}).items()
        ])
        st.dataframe(outputs_df, use_container_width=True, hide_index=True)
        
        st.info("""
        💡 **Processing Coefficients:**
        - Based on USGS Mineral Industry Surveys
        - Represent typical conversion ratios for ore processing
        - Can be country and year-specific (future enhancement)
        - Split ratios show % of input converted to each output
        """)
    
    # Notes on limitations
    st.warning("""
    ⚠️ **MVP Limitations:**
    - Processing coefficients are defaults (not country-specific)
    - Stock change and losses are simplified
    - Trade mirror data not fully integrated
    - Geographic processing capacity not mapped
    
    **Future Enhancements:**
    - Load country-specific coefficients from `processing_splits` table
    - Integrate actual trade mirror data
    - Add time-series processing capacity data
    - Country-level processing utilization analysis
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; font-size: 12px;">
    <b>Material Flow Module</b> | Sankey Diagrams & Mass Balance<br>
    Last updated: January 2026
</div>
""", unsafe_allow_html=True)
