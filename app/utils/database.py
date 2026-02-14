"""
Database Connection & Query Module for RENO-TITAN
Handles all Supabase interactions and provides cached query functions.
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
from functools import lru_cache
import pandas as pd
from dotenv import load_dotenv

try:
    from supabase import create_client, Client
except ImportError:
    raise ImportError("supabase library required. Run: pip install supabase")

# ============================================================================
# CONFIGURATION & LOGGING
# ============================================================================

load_dotenv()

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY not found in .env file. "
        "Please set these credentials and try again."
    )

# ============================================================================
# SINGLETON CLIENT
# ============================================================================

_client: Optional[Client] = None

def get_db_client() -> Client:
    """Get or create the Supabase client (singleton pattern)."""
    global _client
    if _client is None:
        try:
            _client = create_client(SUPABASE_URL, SUPABASE_KEY)
            logger.info("✅ Connected to Supabase successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Supabase: {e}")
            raise
    return _client

# ============================================================================
# CONNECTION TEST
# ============================================================================

def test_connection() -> bool:
    """Test connection to Supabase and return status."""
    try:
        client = get_db_client()
        # Simple query to verify connection - just fetch one row
        response = client.table("countries").select("*").limit(1).execute()
        logger.info("✅ Database connection test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False

# ============================================================================
# DATA INSERTION FUNCTIONS
# ============================================================================

def insert_countries(data: List[Dict]) -> bool:
    """Insert country reference data."""
    try:
        client = get_db_client()
        # Check if table already has data
        response = client.table("countries").select("*").limit(1).execute()
        
        if response.data and len(response.data) > 0:
            logger.info(f"Countries table already populated. Skipping.")
            return True
        
        # Insert countries
        for country_dict in data:
            client.table("countries").insert(country_dict).execute()
        
        logger.info(f"✅ Inserted {len(data)} countries")
        return True
    except Exception as e:
        logger.error(f"❌ Error inserting countries: {e}")
        return False

def insert_hs_codes(data: List[Dict]) -> bool:
    """Insert HS code reference data."""
    try:
        client = get_db_client()
        
        # First check if table already has data
        response = client.table("hs_codes").select("*").limit(1).execute()
        if response.data and len(response.data) > 0:
            logger.info(f"HS codes table already populated. Skipping.")
            return True
        
        for hs_dict in data:
            client.table("hs_codes").insert(hs_dict).execute()
        
        logger.info(f"✅ Inserted {len(data)} HS codes")
        return True
    except Exception as e:
        logger.error(f"❌ Error inserting HS codes: {e}")
        return False

def insert_production_data(df: pd.DataFrame) -> bool:
    """Insert production data from DataFrame."""
    try:
        client = get_db_client()
        
        # Convert DataFrame to list of dicts
        records = df.to_dict('records')
        
        # Replace NaN with None for JSON serialization
        for record in records:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
        
        # Insert in batches of 100 to avoid timeout
        batch_size = 100
        inserted_count = 0
        failed_count = 0
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            try:
                client.table("production_data").insert(batch).execute()
                inserted_count += len(batch)
            except Exception as batch_error:
                logger.warning(f"⚠️  Batch {i//batch_size} failed: {type(batch_error).__name__}: {str(batch_error)[:100]}")
                # Try inserting one by one
                for record in batch:
                    try:
                        client.table("production_data").insert([record]).execute()
                        inserted_count += 1
                    except Exception as single_error:
                        logger.debug(f"Failed to insert record: {single_error}")
                        failed_count += 1
        
        logger.info(f"✅ Inserted {inserted_count}/{len(records)} production records")
        if failed_count > 0:
            logger.warning(f"⚠️  Failed to insert {failed_count} records")
        return inserted_count > 0
    except Exception as e:
        logger.error(f"❌ Error inserting production data: {type(e).__name__}: {e}")
        return False

def insert_trade_data(df: pd.DataFrame) -> bool:
    """Insert trade data from DataFrame."""
    try:
        client = get_db_client()
        
        records = df.to_dict('records')
        
        # Replace NaN with None for JSON serialization
        for record in records:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
        
        # Insert in batches of 100
        batch_size = 100
        inserted_count = 0
        failed_count = 0
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            try:
                client.table("trade_data").insert(batch).execute()
                inserted_count += len(batch)
            except Exception as batch_error:
                logger.warning(f"⚠️  Batch {i//batch_size} failed: {type(batch_error).__name__}: {str(batch_error)[:100]}")
                # Try inserting one by one
                for record in batch:
                    try:
                        client.table("trade_data").insert([record]).execute()
                        inserted_count += 1
                    except Exception as single_error:
                        logger.debug(f"Failed to insert record: {single_error}")
                        failed_count += 1
        
        logger.info(f"✅ Inserted {inserted_count}/{len(records)} trade records")
        if failed_count > 0:
            logger.warning(f"⚠️  Failed to insert {failed_count} records")
        return inserted_count > 0
    except Exception as e:
        logger.error(f"❌ Error inserting trade data: {type(e).__name__}: {e}")
        return False

# ============================================================================
# QUERY FUNCTIONS
# ============================================================================

def get_production_data(
    commodity: Optional[str] = None,
    country_iso3: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    data_source: Optional[str] = None,
) -> pd.DataFrame:
    """
    Query production data with optional filters.
    
    Args:
        commodity: Filter by commodity (e.g., 'titanium_minerals')
        country_iso3: Filter by country ISO3 code (3-letter ISO code)
        year_min: Minimum year (1900-2100)
        year_max: Maximum year (1900-2100)
        data_source: Filter by source (USGS, BGS, etc.)
    
    Returns:
        DataFrame with production data
    """
    try:
        # Input validation
        if country_iso3 and (not isinstance(country_iso3, str) or len(country_iso3) != 3):
            logger.warning(f"Invalid country code: {country_iso3}")
            return pd.DataFrame()
        
        if year_min and (not isinstance(year_min, int) or year_min < 1900 or year_min > 2100):
            logger.warning(f"Invalid year_min: {year_min}")
            return pd.DataFrame()
        
        if year_max and (not isinstance(year_max, int) or year_max < 1900 or year_max > 2100):
            logger.warning(f"Invalid year_max: {year_max}")
            return pd.DataFrame()
        
        client = get_db_client()
        query = client.table("production_data").select("*")
        
        if commodity:
            query = query.eq("commodity", commodity)
        if country_iso3:
            query = query.eq("country_iso3", country_iso3)
        if year_min:
            query = query.gte("year", year_min)
        if year_max:
            query = query.lte("year", year_max)
        if data_source:
            query = query.eq("data_source", data_source)
        
        response = query.execute()
        df = pd.DataFrame(response.data)
        logger.info(f"✅ Retrieved {len(df)} production records")
        return df
    except Exception as e:
        logger.error(f"❌ Error querying production data: {type(e).__name__}: {e}")
        return pd.DataFrame()

def get_top_producers(commodity: str, year: int, limit: int = 10) -> pd.DataFrame:
    """
    Get top N producers for a specific commodity and year.
    
    Args:
        commodity: Commodity name
        year: Year to query
        limit: Number of top producers (default: 10, max: 100)
    
    Returns:
        DataFrame with top producers
    """
    try:
        # Input validation
        if not isinstance(commodity, str) or not commodity:
            logger.warning(f"Invalid commodity: {commodity}")
            return pd.DataFrame()
        
        if not isinstance(year, int) or year < 1900 or year > 2100:
            logger.warning(f"Invalid year: {year}")
            return pd.DataFrame()
        
        if not isinstance(limit, int) or limit < 1 or limit > 100:
            logger.warning(f"Invalid limit: {limit}, using default 10")
            limit = 10
        
        df = get_production_data(commodity=commodity, year_min=year, year_max=year)
        
        if df.empty:
            logger.info(f"No production data for {commodity} in {year}")
            return df
        
        # Group by country and sum quantity
        top = df.groupby('country_iso3').agg({
            'quantity': 'sum',
            'unit': 'first'
        }).reset_index()
        
        top = top.sort_values('quantity', ascending=False).head(limit)
        top.columns = ['Country', 'Production', 'Unit']
        
        return top
    except Exception as e:
        logger.error(f"❌ Error getting top producers: {type(e).__name__}: {e}")
        return pd.DataFrame()

def get_production_comparison(commodity: str, country_iso3: str) -> pd.DataFrame:
    """
    Get USGS vs BGS production comparison for a country.
    
    Args:
        commodity: Commodity name
        country_iso3: Country ISO3 code
    
    Returns:
        DataFrame with comparison data
    """
    try:
        df = get_production_data(commodity=commodity, country_iso3=country_iso3)
        
        if df.empty:
            return df
        
        # Pivot to compare sources
        comparison = df.pivot_table(
            index='year',
            columns='data_source',
            values='quantity',
            aggfunc='sum'
        ).reset_index()
        
        return comparison
    except Exception as e:
        logger.error(f"❌ Error getting production comparison: {e}")
        return pd.DataFrame()

def get_trade_data(
    hs_code: Optional[str] = None,
    reporter_iso3: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
) -> pd.DataFrame:
    """
    Query trade data with optional filters.
    
    Args:
        hs_code: Filter by HS code
        reporter_iso3: Filter by reporter country
        year_min: Minimum year
        year_max: Maximum year
    
    Returns:
        DataFrame with trade data
    """
    try:
        client = get_db_client()
        query = client.table("trade_data").select("*")
        
        if hs_code:
            query = query.eq("hs_code", hs_code)
        if reporter_iso3:
            query = query.eq("reporter_iso3", reporter_iso3)
        if year_min:
            query = query.gte("year", year_min)
        if year_max:
            query = query.lte("year", year_max)
        
        response = query.execute()
        df = pd.DataFrame(response.data)
        logger.info(f"✅ Retrieved {len(df)} trade records")
        return df
    except Exception as e:
        logger.error(f"❌ Error querying trade data: {e}")
        return pd.DataFrame()

@lru_cache(maxsize=1)
def _get_countries_cached() -> Tuple:
    """Internal cached countries query."""
    try:
        client = get_db_client()
        response = client.table("countries").select("iso3, name").execute()
        return tuple(response.data) if response.data else ()
    except Exception as e:
        logger.error(f"❌ Error getting countries: {type(e).__name__}: {e}")
        return ()

def get_countries() -> pd.DataFrame:
    """Get all countries (cached)."""
    try:
        cached_data = _get_countries_cached()
        df = pd.DataFrame(cached_data)
        return df
    except Exception as e:
        logger.error(f"❌ Error processing countries: {type(e).__name__}: {e}")
        return pd.DataFrame()

def get_country_name(iso3: str) -> Optional[str]:
    """Get country name from ISO3 code."""
    try:
        # Input validation
        if not isinstance(iso3, str) or len(iso3) != 3:
            logger.warning(f"Invalid ISO3 code: {iso3}")
            return None
        
        client = get_db_client()
        response = client.table("countries").select("name").eq("iso3", iso3.upper()).execute()
        if response.data:
            return response.data[0]['name']
        return None
    except Exception as e:
        logger.error(f"❌ Error getting country name: {type(e).__name__}: {e}")
        return None

@lru_cache(maxsize=1)
def _get_hs_codes_cached() -> Tuple:
    """Internal cached HS codes query."""
    try:
        client = get_db_client()
        response = client.table("hs_codes").select("code, description, commodity_group, material_type").execute()
        return tuple(response.data) if response.data else ()
    except Exception as e:
        logger.error(f"❌ Error getting HS codes: {type(e).__name__}: {e}")
        return ()

def get_hs_codes() -> pd.DataFrame:
    """Get all HS codes and descriptions (cached)."""
    try:
        cached_data = _get_hs_codes_cached()
        df = pd.DataFrame(cached_data)
        return df
    except Exception as e:
        logger.error(f"❌ Error processing HS codes: {type(e).__name__}: {e}")
        return pd.DataFrame()

def get_top_trade_routes(
    hs_code: Optional[str] = None,
    year: Optional[int] = None,
    limit: int = 15
) -> pd.DataFrame:
    """
    Get top trade routes by value.
    
    Args:
        hs_code: Filter by HS code (6-digit code)
        year: Filter by year (1900-2100)
        limit: Number of routes to return (default: 15, max: 100)
    
    Returns:
        DataFrame with route analysis
    """
    # Input validation
    if limit < 1 or limit > 100:
        logger.warning(f"Invalid limit: {limit}, using default 15")
        limit = 15
    
    if hs_code and (not isinstance(hs_code, str) or len(hs_code) != 6 or not hs_code.isdigit()):
        logger.warning(f"Invalid HS code: {hs_code}")
        return pd.DataFrame()
    
    try:
        df = get_trade_data(hs_code=hs_code, year_min=year, year_max=year)
        
        if df.empty:
            return df
        
        # Create route column and aggregate
        routes = df.groupby(['reporter_iso3', 'partner_iso3']).agg({
            'value_usd': 'sum',
            'quantity': 'sum'
        }).reset_index()
        
        routes['route'] = routes.apply(
            lambda row: f"{row['reporter_iso3']} → {row['partner_iso3']}" if pd.notna(row['partner_iso3']) else f"{row['reporter_iso3']} → Unknown",
            axis=1
        )
        
        routes = routes.sort_values('value_usd', ascending=False).head(limit)
        routes.columns = ['reporter_iso3', 'partner_iso3', 'total_value_usd', 'total_quantity', 'route']
        
        return routes
    except Exception as e:
        logger.error(f"❌ Error getting top trade routes: {type(e).__name__}: {e}")
        return pd.DataFrame()

def get_trade_statistics(
    hs_code: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None
) -> Dict:
    """
    Get summary statistics for trade data.
    
    Args:
        hs_code: Filter by HS code
        year_min: Minimum year
        year_max: Maximum year
    
    Returns:
        Dictionary with statistics
    """
    try:
        df = get_trade_data(hs_code=hs_code, year_min=year_min, year_max=year_max)
        
        if df.empty:
            return {
                'total_value': 0,
                'total_quantity': 0,
                'num_exporters': 0,
                'num_routes': 0,
                'avg_unit_value': 0
            }
        
        stats = {
            'total_value': df['value_usd'].sum(),
            'total_quantity': df['quantity'].sum(),
            'num_exporters': df['reporter_iso3'].nunique(),
            'num_routes': len(df),
            'avg_unit_value': (df['value_usd'].sum() / df['quantity'].sum()) if df['quantity'].sum() > 0 else 0
        }
        
        return stats
    except Exception as e:
        logger.error(f"❌ Error getting trade statistics: {type(e).__name__}: {e}")
        return {}

def get_country_trade_profile(iso3: str) -> Dict:
    """
    Get trade profile for a specific country.
    
    Args:
        iso3: Country ISO3 code
    
    Returns:
        Dictionary with export/import statistics
    """
    try:
        # Get exports from this country
        exports = get_trade_data(reporter_iso3=iso3)
        
        export_stats = {
            'total_export_value': exports['value_usd'].sum() if not exports.empty else 0,
            'export_routes': len(exports) if not exports.empty else 0,
            'top_export_destinations': exports.groupby('partner_iso3')['value_usd'].sum().head(5).to_dict() if not exports.empty else {}
        }
        
        return export_stats
    except Exception as e:
        logger.error(f"❌ Error getting country trade profile: {type(e).__name__}: {e}")
        return {}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def table_exists(table_name: str) -> bool:
    """Check if a table exists in the database."""
    try:
        if not isinstance(table_name, str) or not table_name:
            return False
        
        client = get_db_client()
        response = client.table(table_name).select("*").limit(1).execute()
        return True
    except Exception as e:
        logger.debug(f"Table '{table_name}' may not exist: {type(e).__name__}")
        return False

def get_table_count(table_name: str) -> int:
    """Get row count for a table."""
    try:
        if not isinstance(table_name, str) or not table_name:
            logger.warning(f"Invalid table name: {table_name}")
            return 0
        
        client = get_db_client()
        # Use count='exact' to get the actual row count
        response = client.table(table_name).select("*", count='exact').limit(0).execute()
        # response.count gives the total row count when limit(0) is used
        return response.count if hasattr(response, 'count') and response.count else 0
    except Exception as e:
        logger.error(f"❌ Error getting table count for '{table_name}': {type(e).__name__}: {e}")
        return 0

# ============================================================================

if __name__ == "__main__":
    print("Testing database connection...")
    if test_connection():
        print("✅ Supabase connection successful!")
        
        # Print table statistics
        tables = ["countries", "hs_codes", "production_data", "trade_data"]
        for table in tables:
            if table_exists(table):
                count = get_table_count(table)
                print(f"  {table}: {count} records")
            else:
                print(f"  {table}: NOT FOUND (needs to be created)")
    else:
        print("❌ Connection failed")
