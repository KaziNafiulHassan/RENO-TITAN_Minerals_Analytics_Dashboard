"""
RENO-TITAN Intelligence Platform - Main Streamlit Application
Entry point for the analytics dashboard
"""

import streamlit as st

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="RENO-TITAN Intelligence Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

st.sidebar.title("🌍 RENO-TITAN")
st.sidebar.write("Critical Minerals Supply Chain Analytics")
st.sidebar.markdown("---")

# ============================================================================
# HOME PAGE CONTENT
# ============================================================================

st.title("🌍 RENO-TITAN Intelligence Platform")
st.subtitle("Global Supply Chain Analytics for Titanium, Zirconium & Rare Earth Elements")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Welcome to RENO-TITAN
    
    This platform provides comprehensive analysis of the global supply chain for critical minerals:
    - **Titanium** (Ti)
    - **Zirconium** (Zr)
    - **Rare Earth Elements** (REE)
    
    Analyze production trends, detect trade inconsistencies, and model material flows.
    """)

with col2:
    st.markdown("""
    ### Key Features
    
    📊 **Production Analysis** - Compare USGS vs BGS data
    
    🔄 **Trade QC** - Mirror analysis & discrepancy detection
    
    🗺️ **Geospatial Maps** - Choropleths & flow maps
    
    🌊 **Material Flow** - Sankey diagrams & mass balance
    """)

st.markdown("---")

# ============================================================================
# MODULE CARDS
# ============================================================================

st.header("📑 Modules")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="border: 2px solid #1f77b4; padding: 15px; border-radius: 5px; text-align: center;">
        <h3>📊</h3>
        <b>Production Analysis</b><br>
        <small>USGS vs BGS comparison</small>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="border: 2px solid #ff7f0e; padding: 15px; border-radius: 5px; text-align: center;">
        <h3>🔄</h3>
        <b>Trade QC</b><br>
        <small>Mirror analysis & routes</small>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="border: 2px solid #2ca02c; padding: 15px; border-radius: 5px; text-align: center;">
        <h3>🗺️</h3>
        <b>Geospatial Maps</b><br>
        <small>Choropleths & flows</small>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style="border: 2px solid #d62728; padding: 15px; border-radius: 5px; text-align: center;">
        <h3>🌊</h3>
        <b>Material Flow</b><br>
        <small>Sankey diagrams</small>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# QUICK START GUIDE
# ============================================================================

with st.expander("📖 Quick Start Guide"):
    st.markdown("""
    ### Getting Started
    
    1. **Setup** - Configure your Supabase credentials in `.env`
    2. **Load Data** - Run the ETL pipeline to populate the database
    3. **Explore** - Use the sidebar to navigate to different modules
    4. **Analyze** - Filter by commodity, year, country, and trade routes
    
    ### Data Quality
    
    All data is marked with quality flags:
    - **Official** - From official statistical authority
    - **Estimated** - Interpolated from partial data
    - **Mirror-Derived** - Calculated from partner country imports
    
    ### Learn More
    
    See [reno_titan_guide.txt](../reno_titan_guide.txt) for detailed documentation.
    """)

# ============================================================================
# STATUS INDICATORS
# ============================================================================

st.markdown("---")
st.header("📊 System Status")

status_cols = st.columns(4)

with status_cols[0]:
    st.metric("Database", "Not Connected", delta="Setup required")

with status_cols[1]:
    st.metric("Data Records", "0", delta="Awaiting ETL")

with status_cols[2]:
    st.metric("Countries Mapped", "0", delta="Awaiting data load")

with status_cols[3]:
    st.metric("HS Codes", "0", delta="Reference only")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 12px;">
        <b>RENO-TITAN Intelligence Platform</b> | 
        Phase 1 - Foundation<br>
        Last updated: January 2026
    </div>
    """,
    unsafe_allow_html=True,
)
