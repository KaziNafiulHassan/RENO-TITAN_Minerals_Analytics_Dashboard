"""
Diagnostic script to check HS codes and trade data in the database.
Helps identify why some HS codes return no data.
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from utils.database import get_db_client

load_dotenv()

def diagnose_database():
    """Diagnose database contents for HS codes and trade data."""
    
    print("=" * 80)
    print("RENO-TITAN DATABASE DIAGNOSTIC REPORT")
    print("=" * 80)
    
    try:
        client = get_db_client()
        
        # 1. Check HS Codes in database
        print("\n1. HS CODES IN DATABASE")
        print("-" * 80)
        
        hs_response = client.table("hs_codes").select("code, description, commodity_group, material_type").execute()
        hs_df = pd.DataFrame(hs_response.data) if hs_response.data else pd.DataFrame()
        
        if not hs_df.empty:
            print(f"\n✅ Found {len(hs_df)} HS codes in database:")
            print(hs_df.to_string(index=False))
        else:
            print("\n❌ No HS codes found in database!")
        
        # 2. Check trade data records statistics
        print("\n\n2. TRADE DATA STATISTICS")
        print("-" * 80)
        
        trade_response = client.table("trade_data").select("*").execute()
        trade_df = pd.DataFrame(trade_response.data) if trade_response.data else pd.DataFrame()
        
        if not trade_df.empty:
            print(f"\n✅ Total trade records: {len(trade_df)}")
            print(f"\nColumns in trade_data table: {list(trade_df.columns)}")
            
            # Unique HS codes in data
            if 'hs_code' in trade_df.columns:
                unique_hs = trade_df['hs_code'].unique()
                print(f"\n📊 Unique HS codes in trade data: {len(unique_hs)}")
                print(f"   HS codes: {sorted(unique_hs)}")
                
                # Records per HS code
                print("\n📈 Record count per HS code:")
                hs_counts = trade_df['hs_code'].value_counts().sort_index()
                for hs_code, count in hs_counts.items():
                    print(f"   {hs_code}: {count:,} records")
                
                # Year range
                if 'year' in trade_df.columns:
                    print(f"\n📅 Year range in data: {trade_df['year'].min()} - {trade_df['year'].max()}")
                
                # Records by flow
                if 'flow' in trade_df.columns:
                    print(f"\n🔄 Records by flow:")
                    flow_counts = trade_df['flow'].value_counts()
                    for flow, count in flow_counts.items():
                        print(f"   {flow}: {count:,} records")
                
                # Comparison of HS codes in hs_codes table vs trade_data table
                print("\n\n3. HS CODE COVERAGE ANALYSIS")
                print("-" * 80)
                
                if not hs_df.empty:
                    hs_codes_in_table = set(hs_df['code'].astype(str))
                    hs_codes_in_data = set(unique_hs.astype(str))
                    
                    print(f"\n✅ HS codes defined in hs_codes table: {len(hs_codes_in_table)}")
                    print(f"✅ HS codes with data in trade_data table: {len(hs_codes_in_data)}")
                    
                    # Codes with definition but no data
                    missing_data = hs_codes_in_table - hs_codes_in_data
                    if missing_data:
                        print(f"\n⚠️  HS codes defined but with NO trade data ({len(missing_data)}):")
                        for code in sorted(missing_data):
                            hs_desc = hs_df[hs_df['code'] == code]['description'].values
                            print(f"   {code}: {hs_desc[0] if hs_desc else 'N/A'}")
                    
                    # Codes with data but no definition
                    extra_data = hs_codes_in_data - hs_codes_in_table
                    if extra_data:
                        print(f"\n⚠️  HS codes in trade data but NOT in hs_codes table ({len(extra_data)}):")
                        for code in sorted(extra_data):
                            print(f"   {code}")
                
                # Sample data
                print("\n\n4. SAMPLE TRADE DATA")
                print("-" * 80)
                print("\nFirst 5 records from trade_data:")
                sample_df = trade_df.head(5).copy()
                for col in sample_df.columns:
                    if sample_df[col].dtype == 'float64':
                        sample_df[col] = sample_df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "")
                print(sample_df.to_string(index=False))
        
        else:
            print("\n❌ No trade data found in database!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_database()
