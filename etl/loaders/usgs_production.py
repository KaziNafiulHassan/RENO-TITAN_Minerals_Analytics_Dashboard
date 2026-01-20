"""
USGS Production Data Loader
Loads titanium minerals production data from USGS CSV file.
"""

import os
import logging
import pandas as pd
from etl.config import CSV_FILES, get_iso3_from_country_name

logger = logging.getLogger(__name__)

# ============================================================================
# FILE PATH
# ============================================================================

USGS_TITANIUM_FILE = CSV_FILES.get("titanium_usgs")

# ============================================================================
# USGS PRODUCTION LOADER
# ============================================================================

def load_usgs_production() -> pd.DataFrame:
    """
    Load and process USGS titanium production data.
    
    Returns:
        DataFrame ready for insertion into production_data table
    """
    if not os.path.exists(USGS_TITANIUM_FILE):
        logger.error(f"USGS Titanium file not found: {USGS_TITANIUM_FILE}")
        return pd.DataFrame()
    
    logger.info(f"Loading USGS Titanium data from {USGS_TITANIUM_FILE}")
    
    df = pd.read_csv(USGS_TITANIUM_FILE)
    
    # Rename columns to standard format
    df = df.rename(columns={
        'Country': 'country_name',
        'Year': 'year',
        'Subcommodity': 'subcommodity',
        'Production (in tonnes)': 'quantity',
        'Source': 'data_source'
    })
    
    # Add standard columns
    df['commodity'] = 'titanium_minerals'
    df['unit'] = 'tonnes'
    df['quality_flag'] = 'Official'
    df['notes'] = df['subcommodity']  # Store subcommodity type
    
    # Map country names to ISO3
    df['country_iso3'] = df['country_name'].apply(_map_country)
    
    # Filter valid records (remove unmapped countries and zero/negative quantities)
    df = df[df['country_iso3'].notna() & (df['quantity'] > 0)].copy()
    
    # Select and reorder columns
    result = df[[
        'commodity', 'country_iso3', 'year', 'quantity', 'unit',
        'data_source', 'quality_flag', 'notes'
    ]]
    
    logger.info(f"✅ Loaded {len(result)} USGS production records")
    return result

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _map_country(country_name: str) -> str:
    """
    Map country name to ISO3 code.
    Returns None if country not found.
    """
    try:
        return get_iso3_from_country_name(country_name)
    except ValueError:
        logger.warning(f"Country '{country_name}' not mapped to ISO3")
        return None

# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    df = load_usgs_production()
    print(f"\nLoaded {len(df)} USGS production records")
    print(f"Countries: {df['country_iso3'].nunique()}")
    print(f"Years: {df['year'].min()}-{df['year'].max()}")
