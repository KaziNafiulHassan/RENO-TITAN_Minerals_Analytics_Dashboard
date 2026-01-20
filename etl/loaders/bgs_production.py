"""
BGS Production Data Loader
Loads titanium, zirconium, and rare earth minerals production data from BGS CSV files.
"""

import os
import logging
import pandas as pd
from typing import Tuple
from etl.config import (
    CSV_FILES, 
    COUNTRY_ISO3_MAP, 
    get_iso3_from_country_name
)

logger = logging.getLogger(__name__)

# ============================================================================
# FILE PATHS
# ============================================================================

BGS_TITANIUM_FILE = CSV_FILES.get("titanium_bgs")
BGS_ZIRCONIUM_FILE = CSV_FILES.get("zirconium_bgs")
BGS_REE_FILE = CSV_FILES.get("ree_bgs")

# ============================================================================
# BGS PRODUCTION LOADER
# ============================================================================

def load_bgs_production() -> pd.DataFrame:
    """
    Load and process all BGS production data (Titanium, Zirconium, REE).
    
    Returns:
        DataFrame ready for insertion into production_data table
    """
    logger.info("Starting BGS production data load...")
    
    dfs = []
    
    # Load Titanium
    if os.path.exists(BGS_TITANIUM_FILE):
        logger.info(f"Loading BGS Titanium data from {BGS_TITANIUM_FILE}")
        df_ti = _load_bgs_titanium()
        dfs.append(df_ti)
        logger.info(f"  ✅ Loaded {len(df_ti)} Titanium records")
    else:
        logger.warning(f"BGS Titanium file not found: {BGS_TITANIUM_FILE}")
    
    # Load Zirconium
    if os.path.exists(BGS_ZIRCONIUM_FILE):
        logger.info(f"Loading BGS Zirconium data from {BGS_ZIRCONIUM_FILE}")
        df_zr = _load_bgs_zirconium()
        dfs.append(df_zr)
        logger.info(f"  ✅ Loaded {len(df_zr)} Zirconium records")
    else:
        logger.warning(f"BGS Zirconium file not found: {BGS_ZIRCONIUM_FILE}")
    
    # Load REE
    if os.path.exists(BGS_REE_FILE):
        logger.info(f"Loading BGS REE data from {BGS_REE_FILE}")
        df_ree = _load_bgs_ree()
        dfs.append(df_ree)
        logger.info(f"  ✅ Loaded {len(df_ree)} REE records")
    else:
        logger.warning(f"BGS REE file not found: {BGS_REE_FILE}")
    
    # Combine all BGS data
    if dfs:
        result = pd.concat(dfs, ignore_index=True)
        logger.info(f"✅ Total BGS records: {len(result)}")
        return result
    else:
        logger.error("No BGS files loaded")
        return pd.DataFrame()

# ============================================================================
# BGS TITANIUM
# ============================================================================

def _load_bgs_titanium() -> pd.DataFrame:
    """Load BGS Titanium Minerals Production data."""
    df = pd.read_csv(BGS_TITANIUM_FILE)
    
    # Rename columns to standard format
    df = df.rename(columns={
        'Country': 'country_name',
        'Year': 'year',
        'Sub-commodity': 'subcommodity',
        'Quantity in metric tons': 'quantity',
        'Source': 'data_source'
    })
    
    # Add standard columns
    df['commodity'] = 'titanium_minerals'
    df['unit'] = 'tonnes'
    df['quality_flag'] = 'Official'
    df['notes'] = df['subcommodity']  # Store subcommodity type in notes
    
    # Map country names to ISO3
    df['country_iso3'] = df['country_name'].apply(_map_country)
    
    # Filter valid records
    df = df[df['country_iso3'].notna() & (df['quantity'] > 0)].copy()
    
    # Select and reorder columns
    return df[[
        'commodity', 'country_iso3', 'year', 'quantity', 'unit',
        'data_source', 'quality_flag', 'notes'
    ]]

# ============================================================================
# BGS ZIRCONIUM
# ============================================================================

def _load_bgs_zirconium() -> pd.DataFrame:
    """Load BGS Zirconium Production data."""
    df = pd.read_csv(BGS_ZIRCONIUM_FILE)
    
    # Rename columns
    df = df.rename(columns={
        'Country': 'country_name',
        'Year': 'year',
        'Sub-commodity': 'subcommodity',
        'Production (tonnes)': 'quantity',
        'Source': 'data_source'
    })
    
    # Add standard columns
    df['commodity'] = 'zircon'
    df['unit'] = 'tonnes'
    df['quality_flag'] = 'Official'
    df['notes'] = df['subcommodity']
    
    # Map country names to ISO3
    df['country_iso3'] = df['country_name'].apply(_map_country)
    
    # Filter valid records
    df = df[df['country_iso3'].notna() & (df['quantity'] > 0)].copy()
    
    # Select and reorder columns
    return df[[
        'commodity', 'country_iso3', 'year', 'quantity', 'unit',
        'data_source', 'quality_flag', 'notes'
    ]]

# ============================================================================
# BGS RARE EARTH ELEMENTS
# ============================================================================

def _load_bgs_ree() -> pd.DataFrame:
    """Load BGS Rare Earth Minerals Production data."""
    df = pd.read_csv(BGS_REE_FILE)
    
    # Rename columns
    df = df.rename(columns={
        'Country': 'country_name',
        'Year': 'year',
        'Sub-commodity': 'subcommodity',
        'Production (tonnes)': 'quantity',
        'Source': 'data_source'
    })
    
    # Add standard columns
    df['commodity'] = 'rare_earth_elements'
    df['unit'] = 'tonnes'
    df['quality_flag'] = 'Official'
    df['notes'] = df['subcommodity']  # Monazite or Xenotime
    
    # Map country names to ISO3
    df['country_iso3'] = df['country_name'].apply(_map_country)
    
    # Filter valid records (note: many may be 0)
    df = df[df['country_iso3'].notna() & (df['quantity'] > 0)].copy()
    
    # Select and reorder columns
    return df[[
        'commodity', 'country_iso3', 'year', 'quantity', 'unit',
        'data_source', 'quality_flag', 'notes'
    ]]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _map_country(country_name: str) -> str:
    """
    Map country name to ISO3 code.
    Returns empty string if country not found.
    """
    try:
        return get_iso3_from_country_name(country_name)
    except ValueError:
        logger.warning(f"Country '{country_name}' not mapped to ISO3")
        return None

# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    df = load_bgs_production()
    print(f"\nLoaded {len(df)} BGS production records")
    print(f"Commodities: {df['commodity'].unique()}")
    print(f"Countries: {df['country_iso3'].nunique()}")
    print(f"Years: {df['year'].min()}-{df['year'].max()}")
