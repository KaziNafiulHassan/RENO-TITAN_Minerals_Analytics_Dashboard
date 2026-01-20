"""
Trade Data Loader
Loads titanium import/export data from Comtrade CSV file.
"""

import os
import logging
import pandas as pd
from etl.config import CSV_FILES, get_iso3_from_country_name

logger = logging.getLogger(__name__)

# ============================================================================
# FILE PATH
# ============================================================================

TITANIUM_TRADE_FILE = CSV_FILES.get("titanium_trade")

# ============================================================================
# TRADE DATA LOADER
# ============================================================================

def load_trade_data() -> pd.DataFrame:
    """
    Load and process titanium trade data.
    
    Note: Current file lacks partner country information.
    This loader will handle the available data structure.
    
    Returns:
        DataFrame ready for insertion into trade_data table
    """
    if not os.path.exists(TITANIUM_TRADE_FILE):
        logger.error(f"Trade data file not found: {TITANIUM_TRADE_FILE}")
        return pd.DataFrame()
    
    logger.info(f"Loading trade data from {TITANIUM_TRADE_FILE}")
    
    df = pd.read_csv(TITANIUM_TRADE_FILE)
    
    # Print columns for debugging
    logger.info(f"Columns found: {list(df.columns)}")
    
    # Rename columns - note there may be weird spacing
    df.columns = df.columns.str.strip()  # Remove leading/trailing whitespace
    
    # Map column names (accounting for potential formatting issues)
    column_mapping = {}
    for col in df.columns:
        col_lower = col.lower()
        if 'country' in col_lower:
            column_mapping[col] = 'country_name'
        elif 'year' in col_lower:
            column_mapping[col] = 'year'
        elif 'commodity' in col_lower:
            column_mapping[col] = 'commodity_name'
        elif 'export' in col_lower or 'import' in col_lower:
            column_mapping[col] = 'flow'
        elif 'quantity' in col_lower and 'metric' in col_lower:
            column_mapping[col] = 'quantity'
        elif 'quantity' in col_lower or 'ton' in col_lower:
            column_mapping[col] = 'quantity'
        elif 'value' in col_lower and 'usd' in col_lower:
            column_mapping[col] = 'value_usd'
        elif 'trade' in col_lower and 'value' in col_lower:
            column_mapping[col] = 'value_usd'
    
    df = df.rename(columns=column_mapping)
    
    # Standardize flow direction (Export/Import to lowercase)
    if 'flow' in df.columns:
        df['flow'] = df['flow'].str.lower().str.strip()
    
    # Handle value column - may be in thousands
    if 'value_usd' in df.columns:
        # If values look like they're in thousands (< 1 million for avg trade)
        # multiply by 1000
        df['value_usd'] = pd.to_numeric(df['value_usd'], errors='coerce')
        
        # Check if values seem to be in thousands
        mean_value = df['value_usd'].mean()
        if mean_value < 1000000:  # If average < 1M, likely in thousands
            df['value_usd'] = df['value_usd'] * 1000
    
    # Add standard columns
    df['hs_code'] = '261400'  # Titanium ores and concentrates
    df['quantity_unit'] = 'tonnes'
    df['data_source'] = 'Comtrade'
    df['quality_flag'] = 'Official'
    
    # Map country names to ISO3
    df['reporter_iso3'] = df['country_name'].apply(_map_country)
    
    # Partner ISO3 is not available in current file
    df['partner_iso3'] = None
    
    # Filter valid records
    df = df[df['reporter_iso3'].notna()].copy()
    
    # Select and reorder columns for trade_data table
    result = df[[
        'hs_code', 'reporter_iso3', 'partner_iso3', 'flow', 'year',
        'value_usd', 'quantity', 'quantity_unit', 'data_source', 'quality_flag'
    ]]
    
    logger.info(f"✅ Loaded {len(result)} trade records")
    logger.warning("⚠️  NOTE: partner_iso3 is NULL - bilateral analysis not available with current data")
    
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
    df = load_trade_data()
    print(f"\nLoaded {len(df)} trade records")
    if not df.empty:
        print(f"Countries: {df['reporter_iso3'].nunique()}")
        print(f"Years: {df['year'].min()}-{df['year'].max()}")
        print(f"Flows: {df['flow'].unique()}")
