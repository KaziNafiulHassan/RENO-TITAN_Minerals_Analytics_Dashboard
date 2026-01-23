"""
RENO-TITAN Intelligence Platform - Main Streamlit Application
Entry point for the analytics dashboard
"""

import streamlit as st
import sys
import os

# Add parent directory (project root) to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.database import test_connection, get_table_count

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

# Navigation menu
selected_page = st.sidebar.radio(
    "Navigate to:",
    ["Home", "Production Analysis", "Trade QC", "Geospatial Maps", "Material Flow"],
    captions=["Main dashboard", "USGS vs BGS", "Mirror analysis", "Choropleths", "Sankey diagrams"]
)

# Route to selected page
if selected_page == "Home":
    pass  # Stay on home page
elif selected_page == "Production Analysis":
    st.switch_page("pages/1_📊_Production_Analysis.py")
elif selected_page == "Trade QC":
    st.switch_page("pages/2_🔄_Trade_QC.py")
elif selected_page == "Geospatial Maps":
    st.switch_page("pages/3_🗺️_Geospatial_Maps.py")
elif selected_page == "Material Flow":
    st.switch_page("pages/4_🌊_Material_Flow.py")

st.sidebar.markdown("---")

# ============================================================================
# HOME PAGE CONTENT
# ============================================================================

st.title("🌍 RENO-TITAN Intelligence Platform")
st.write("#### Global Supply Chain Analytics for Titanium, Zirconium & Rare Earth Elements")

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
        <small>USGS vs BGS comparison</small><br><br>
        <a href="/Production_Analysis" style="color: #1f77b4; text-decoration: none;">Go →</a>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="border: 2px solid #ff7f0e; padding: 15px; border-radius: 5px; text-align: center;">
        <h3>🔄</h3>
        <b>Trade QC</b><br>
        <small>Mirror analysis & routes</small><br><br>
        <a href="/Trade_QC" style="color: #ff7f0e; text-decoration: none;">Go →</a>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="border: 2px solid #2ca02c; padding: 15px; border-radius: 5px; text-align: center;">
        <h3>🗺️</h3>
        <b>Geospatial Maps</b><br>
        <small>Choropleths & flows</small><br><br>
        <a href="/Geospatial_Maps" style="color: #2ca02c; text-decoration: none;">Go →</a>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style="border: 2px solid #d62728; padding: 15px; border-radius: 5px; text-align: center;">
        <h3>🌊</h3>
        <b>Material Flow</b><br>
        <small>Sankey diagrams</small><br><br>
        <a href="/Material_Flow" style="color: #d62728; text-decoration: none;">Go →</a>
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

# Get actual database status
db_connected = test_connection()
countries_count = get_table_count("countries") if db_connected else 0
hs_codes_count = get_table_count("hs_codes") if db_connected else 0
production_count = get_table_count("production_data") if db_connected else 0
trade_count = get_table_count("trade_data") if db_connected else 0
total_records = production_count + trade_count

status_cols = st.columns(4)

db_status = "✅ Connected" if db_connected else "❌ Not Connected"
with status_cols[0]:
    st.metric("Database", db_status.split()[0], delta=db_status.split()[1] if len(db_status.split()) > 1 else "")

with status_cols[1]:
    st.metric("Data Records", f"{total_records:,}", delta=f"Production: {production_count}, Trade: {trade_count}")

with status_cols[2]:
    st.metric("Countries Mapped", f"{countries_count:,}", delta="Ready" if countries_count > 0 else "Loading")

with status_cols[3]:
    st.metric("HS Codes", f"{hs_codes_count:,}", delta="Reference loaded" if hs_codes_count > 0 else "Loading")

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
