"""
Comprehensive Supabase Database Status Check
Inspects all tables and provides data quality report
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from utils.database import get_db_client, test_connection

def get_table_count(table_name: str) -> int:
    """Get row count from a table."""
    try:
        client = get_db_client()
        response = client.table(table_name).select("*", count="exact").limit(0).execute()
        return response.count if response.count is not None else 0
    except Exception as e:
        print(f"❌ Error counting {table_name}: {e}")
        return 0

def get_sample_data(table_name: str, limit: int = 5) -> pd.DataFrame:
    """Get sample data from a table."""
    try:
        client = get_db_client()
        response = client.table(table_name).select("*").limit(limit).execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception as e:
        print(f"❌ Error fetching from {table_name}: {e}")
        return pd.DataFrame()

def get_year_range(table_name: str, year_column: str = "year") -> tuple:
    """Get min and max year from a table."""
    try:
        client = get_db_client()
        
        # Get min year
        response_min = client.table(table_name).select(f"min:{year_column}").execute()
        min_year = response_min.data[0]['min'] if response_min.data else None
        
        # Get max year
        response_max = client.table(table_name).select(f"max:{year_column}").execute()
        max_year = response_max.data[0]['max'] if response_max.data else None
        
        return (min_year, max_year)
    except Exception as e:
        print(f"❌ Error getting year range for {table_name}: {e}")
        return (None, None)

def get_distinct_values(table_name: str, column_name: str) -> list:
    """Get distinct values from a table column."""
    try:
        client = get_db_client()
        response = client.table(table_name).select(column_name).execute()
        
        if not response.data:
            return []
        
        # Extract unique values
        values = set()
        for row in response.data:
            if column_name in row and row[column_name]:
                values.add(row[column_name])
        
        return sorted(list(values))
    except Exception as e:
        print(f"❌ Error getting distinct values: {e}")
        return []

def main():
    """Run comprehensive database status check."""
    
    print("\n" + "="*80)
    print("🔍 RENO-TITAN SUPABASE DATABASE STATUS CHECK")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    # Test connection
    print("📡 Connection Test:")
    if not test_connection():
        print("❌ Cannot connect to Supabase. Check your .env credentials.")
        return
    print("✅ Connected successfully\n")
    
    # Define tables to check
    tables = {
        'Reference Tables': ['countries', 'hs_codes'],
        'Data Tables': ['production_data', 'trade_data'],
        'Model Tables': ['processing_splits', 'mass_balance_results']
    }
    
    total_records = 0
    data_quality = {}
    
    for category, table_list in tables.items():
        print(f"\n{'='*80}")
        print(f"📊 {category}")
        print('='*80)
        
        for table_name in table_list:
            count = get_table_count(table_name)
            total_records += count
            
            status_emoji = "✅" if count > 0 else "⚠️ "
            print(f"\n{status_emoji} {table_name.upper()}")
            print(f"   Records: {count:,}")
            
            if count > 0:
                # Get year range if applicable
                if table_name in ['production_data', 'trade_data']:
                    min_year, max_year = get_year_range(table_name)
                    if min_year and max_year:
                        print(f"   Year Range: {min_year} - {max_year}")
                
                # Get metadata
                if table_name == 'production_data':
                    commodities = get_distinct_values(table_name, 'commodity')
                    sources = get_distinct_values(table_name, 'data_source')
                    quality_flags = get_distinct_values(table_name, 'quality_flag')
                    
                    print(f"   Commodities: {', '.join(commodities) if commodities else 'None'}")
                    print(f"   Data Sources: {', '.join(sources) if sources else 'None'}")
                    print(f"   Quality Flags: {', '.join(quality_flags) if quality_flags else 'None'}")
                    
                    # Count by commodity
                    client = get_db_client()
                    try:
                        for commodity in commodities:
                            commodity_count = get_table_count('production_data')
                            # This is a simple count, ideally should filter by commodity
                        print(f"   Sample Data:")
                        sample = get_sample_data(table_name, limit=3)
                        if not sample.empty:
                            print(sample.to_string(index=False).replace('\n', '\n   '))
                    except:
                        pass
                
                elif table_name == 'trade_data':
                    hs_codes = get_distinct_values(table_name, 'hs_code')
                    sources = get_distinct_values(table_name, 'data_source')
                    flows = get_distinct_values(table_name, 'flow')
                    
                    print(f"   HS Codes: {len(hs_codes)} unique ({', '.join(hs_codes[:5])}{'...' if len(hs_codes) > 5 else ''})")
                    print(f"   Data Sources: {', '.join(sources) if sources else 'None'}")
                    print(f"   Flows: {', '.join(flows) if flows else 'None'}")
                    
                    print(f"   Sample Data:")
                    sample = get_sample_data(table_name, limit=3)
                    if not sample.empty:
                        print(sample[['hs_code', 'reporter_iso3', 'partner_iso3', 'flow', 'year', 'value_usd']].to_string(index=False).replace('\n', '\n   '))
                
                elif table_name == 'countries':
                    print(f"   Sample Data:")
                    sample = get_sample_data(table_name, limit=5)
                    if not sample.empty:
                        cols_to_show = [col for col in sample.columns if col in ['iso3', 'name', 'region']]
                        print(sample[cols_to_show].to_string(index=False).replace('\n', '\n   '))
                
                elif table_name == 'hs_codes':
                    print(f"   Sample Data:")
                    sample = get_sample_data(table_name, limit=5)
                    if not sample.empty:
                        cols_to_show = [col for col in sample.columns if col in ['code', 'description', 'commodity_group']]
                        print(sample[cols_to_show].to_string(index=False).replace('\n', '\n   '))
    
    # Summary report
    print(f"\n{'='*80}")
    print("📈 SUMMARY REPORT")
    print('='*80)
    print(f"Total Records Across All Tables: {total_records:,}")
    
    print(f"\n📋 Data Coverage for MVP:")
    print("-" * 80)
    
    # Check critical components
    checks = {
        'Countries Reference': get_table_count('countries'),
        'HS Codes Reference': get_table_count('hs_codes'),
        'Production Data': get_table_count('production_data'),
        'Trade Data': get_table_count('trade_data'),
        'Processing Splits': get_table_count('processing_splits'),
        'Mass Balance Results': get_table_count('mass_balance_results'),
    }
    
    for check_name, count in checks.items():
        status = "✅" if count > 0 else "❌"
        print(f"{status} {check_name}: {count:,} records")
    
    # MVP Assessment
    print(f"\n{'='*80}")
    print("🚀 MVP READINESS ASSESSMENT")
    print('='*80)
    
    mvp_ready = True
    recommendations = []
    
    if checks['Countries Reference'] == 0:
        mvp_ready = False
        recommendations.append("❌ Need to seed countries reference table")
    elif checks['Countries Reference'] < 50:
        recommendations.append("⚠️  Low number of countries (minimum 50 recommended)")
    
    if checks['HS Codes Reference'] == 0:
        mvp_ready = False
        recommendations.append("❌ Need to seed HS codes reference table")
    elif checks['HS Codes Reference'] < 10:
        recommendations.append("⚠️  Low number of HS codes (minimum 10+ for titanium/zircon/REE)")
    
    if checks['Production Data'] == 0:
        mvp_ready = False
        recommendations.append("❌ No production data loaded")
    elif checks['Production Data'] < 100:
        recommendations.append("⚠️  Limited production data (minimum 100+ records recommended)")
    
    if checks['Trade Data'] == 0:
        recommendations.append("⚠️  No trade data loaded (module can work with production-only MVP)")
    elif checks['Trade Data'] < 200:
        recommendations.append("⚠️  Limited trade data (minimum 200+ records for meaningful analysis)")
    
    if checks['Processing Splits'] == 0:
        recommendations.append("⚠️  No processing splits loaded (can use defaults in code)")
    
    if mvp_ready and checks['Production Data'] >= 100 and checks['Countries Reference'] >= 10:
        print("\n✅ MVP IS READY TO BUILD!")
        print("\nYou have sufficient data to:")
        print("  ✓ Production Analysis Module (production data + countries)")
        print("  ✓ Basic Trade QC Module (if trade data > 50 records)")
        print("  ✓ Geospatial Maps (with countries data)")
        print("  ✓ Material Flow Sankey (with processing splits)")
    else:
        print("\n⚠️  MVP NEEDS MORE DATA")
    
    if recommendations:
        print("\n📋 Recommendations:")
        for rec in recommendations:
            print(f"   {rec}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
