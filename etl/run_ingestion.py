"""
RENO-TITAN ETL Orchestrator
Master script to initialize database schema and load all data.
Run this once to populate the Supabase database.
"""

import os
import sys
import logging
from typing import List, Dict
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.config import (
    SUPABASE_URL, SUPABASE_KEY, 
    COUNTRY_ISO3_MAP, HS_CODES_REFERENCE
)
from app.utils.database import (
    test_connection, insert_countries, insert_hs_codes,
    insert_production_data, insert_trade_data, table_exists,
    get_table_count, get_db_client
)
from etl.loaders.bgs_production import load_bgs_production
from etl.loaders.usgs_production import load_usgs_production
from etl.loaders.trade_data import load_trade_data

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# INITIALIZATION FUNCTIONS
# ============================================================================

def init_countries() -> bool:
    """Initialize countries reference table."""
    logger.info("\n" + "="*70)
    logger.info("STEP 1: Initializing Countries Reference Table")
    logger.info("="*70)
    
    # Prepare countries data
    countries_data = []
    for country_name, iso3 in sorted(COUNTRY_ISO3_MAP.items()):
        countries_data.append({
            'iso3': iso3,
            'name': country_name,
            'region': None  # Could be populated later
        })
    
    # Remove duplicates (keep last occurrence of each ISO3)
    unique_countries = {}
    for country in countries_data:
        unique_countries[country['iso3']] = country
    
    countries_data = list(unique_countries.values())
    logger.info(f"Preparing {len(countries_data)} unique countries")
    
    if insert_countries(countries_data):
        logger.info(f"✅ Countries initialized")
        return True
    else:
        logger.error("❌ Failed to initialize countries")
        return False

def init_hs_codes() -> bool:
    """Initialize HS codes reference table."""
    logger.info("\n" + "="*70)
    logger.info("STEP 2: Initializing HS Codes Reference Table")
    logger.info("="*70)
    
    hs_codes_data = []
    for code, details in HS_CODES_REFERENCE.items():
        hs_codes_data.append({
            'code': code,
            'description': details['description'],
            'commodity_group': details['commodity_group'],
            'material_type': details['material_type'],
            'notes': None
        })
    
    logger.info(f"Preparing {len(hs_codes_data)} HS codes")
    
    if insert_hs_codes(hs_codes_data):
        logger.info(f"✅ HS codes initialized")
        return True
    else:
        logger.error("❌ Failed to initialize HS codes")
        return False

def load_production_data() -> bool:
    """Load production data from all sources."""
    logger.info("\n" + "="*70)
    logger.info("STEP 3: Loading Production Data")
    logger.info("="*70)
    
    try:
        # Load BGS data
        logger.info("\n[3A] Loading BGS Production Data...")
        df_bgs = load_bgs_production()
        if df_bgs.empty:
            logger.warning("⚠️  No BGS production data loaded")
        
        # Load USGS data
        logger.info("\n[3B] Loading USGS Production Data...")
        df_usgs = load_usgs_production()
        if df_usgs.empty:
            logger.warning("⚠️  No USGS production data loaded")
        
        # Combine
        if not df_bgs.empty and not df_usgs.empty:
            df_production = pd.concat([df_bgs, df_usgs], ignore_index=True)
            logger.info(f"\n[3C] Combined {len(df_production)} production records")
        elif not df_bgs.empty:
            df_production = df_bgs
        elif not df_usgs.empty:
            df_production = df_usgs
        else:
            logger.error("❌ No production data loaded")
            return False
        
        # Insert into database
        logger.info("\n[3D] Inserting production data into database...")
        if insert_production_data(df_production):
            logger.info(f"✅ Production data loaded: {len(df_production)} records")
            return True
        else:
            logger.error("❌ Failed to insert production data")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error loading production data: {e}")
        return False

def load_trade_data_etl() -> bool:
    """Load trade data."""
    logger.info("\n" + "="*70)
    logger.info("STEP 4: Loading Trade Data")
    logger.info("="*70)
    
    try:
        logger.info("\n[4A] Loading trade data from CSV...")
        df_trade = load_trade_data()
        
        if df_trade.empty:
            logger.warning("⚠️  No trade data loaded")
            return False
        
        logger.info(f"\n[4B] Inserting {len(df_trade)} trade records into database...")
        if insert_trade_data(df_trade):
            logger.info(f"✅ Trade data loaded: {len(df_trade)} records")
            return True
        else:
            logger.error("❌ Failed to insert trade data")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error loading trade data: {e}")
        return False

def verify_data_load() -> bool:
    """Verify that data was loaded successfully."""
    logger.info("\n" + "="*70)
    logger.info("STEP 5: Verifying Data Load")
    logger.info("="*70)
    
    tables = {
        'countries': 'Countries',
        'hs_codes': 'HS Codes',
        'production_data': 'Production Data',
        'trade_data': 'Trade Data'
    }
    
    success = True
    for table, label in tables.items():
        if table_exists(table):
            count = get_table_count(table)
            logger.info(f"✅ {label:20} {count:>6} records")
        else:
            logger.error(f"❌ {label:20} TABLE NOT FOUND")
            success = False
    
    return success

# ============================================================================
# MAIN ORCHESTRATION
# ============================================================================

def main():
    """Main orchestration function."""
    
    logger.info("\n" + "="*70)
    logger.info("RENO-TITAN ETL PIPELINE")
    logger.info("="*70)
    logger.info(f"Supabase URL: {SUPABASE_URL}")
    
    # Step 0: Test connection
    logger.info("\nTesting Supabase connection...")
    if not test_connection():
        logger.error("❌ Cannot connect to Supabase. Check .env credentials.")
        return False
    
    logger.info("✅ Supabase connection successful")
    
    # Step 1: Initialize reference tables
    if not init_countries():
        logger.error("❌ Failed to initialize countries. Stopping.")
        return False
    
    if not init_hs_codes():
        logger.error("❌ Failed to initialize HS codes. Stopping.")
        return False
    
    # Step 2: Load data tables
    try:
        import pandas as pd  # Import here to avoid issues if pandas not available
    except ImportError:
        logger.error("❌ pandas required. Run: pip install pandas")
        return False
    
    if not load_production_data():
        logger.warning("⚠️  Failed to load production data. Continuing...")
    
    if not load_trade_data_etl():
        logger.warning("⚠️  Failed to load trade data. Continuing...")
    
    # Step 3: Verify
    if verify_data_load():
        logger.info("\n" + "="*70)
        logger.info("✅ ETL PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("="*70)
        logger.info("\nYou can now run the Streamlit app:")
        logger.info("  streamlit run app/app.py")
        return True
    else:
        logger.info("\n" + "="*70)
        logger.info("⚠️  ETL PIPELINE COMPLETED WITH WARNINGS")
        logger.info("="*70)
        return False

# ============================================================================

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
