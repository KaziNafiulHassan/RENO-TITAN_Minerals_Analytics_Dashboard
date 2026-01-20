"""
Quick Startup Test for RENO-TITAN MVP
Verifies all modules load without errors before launching Streamlit
"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

print("\n" + "="*80)
print("🔍 RENO-TITAN MVP STARTUP VERIFICATION")
print("="*80 + "\n")

# Test 1: Import main app
print("1️⃣  Testing app.py imports...")
try:
    # Verify app.py can be loaded (just check it exists and has no syntax errors)
    with open(os.path.join(os.path.dirname(__file__), 'app', 'app.py'), 'r') as f:
        compile(f.read(), 'app.py', 'exec')
    print("   ✅ app.py syntax is valid\n")
except Exception as e:
    print(f"   ❌ app.py failed to load: {e}\n")
    sys.exit(1)

# Test 2: Import database module
print("2️⃣  Testing database module...")
try:
    from app.utils.database import (
        test_connection,
        get_production_data,
        get_trade_data,
        get_countries,
        get_hs_codes,
        get_top_trade_routes,
        get_trade_statistics
    )
    print("   ✅ All database functions imported\n")
except ImportError as e:
    print(f"   ❌ Database module import failed: {e}\n")
    sys.exit(1)

# Test 3: Import visualizations module
print("3️⃣  Testing visualizations module...")
try:
    from app.utils.visualizations import (
        plot_top_producers,
        plot_production_trend,
        plot_comparison_bars,
        plot_top_routes,
        plot_unit_value_distribution,
        plot_material_flow_sankey,
        plot_mass_balance_waterfall
    )
    print("   ✅ All visualization functions imported\n")
except ImportError as e:
    print(f"   ❌ Visualizations module import failed: {e}\n")
    sys.exit(1)

# Test 4: Import calculations module
print("4️⃣  Testing calculations module...")
try:
    from app.utils.calculations import (
        calculate_unit_values,
        identify_outliers,
        calculate_mirror_discrepancies
    )
    print("   ✅ All calculation functions imported\n")
except ImportError as e:
    print(f"   ❌ Calculations module import failed: {e}\n")
    sys.exit(1)

# Test 5: Test database connection
print("5️⃣  Testing Supabase connection...")
try:
    if test_connection():
        print("   ✅ Supabase connection successful\n")
    else:
        print("   ⚠️  Supabase connection test failed (check .env file)\n")
except Exception as e:
    print(f"   ⚠️  Connection error: {e}\n")

# Test 6: Test data retrieval
print("6️⃣  Testing data retrieval...")
try:
    countries = get_countries()
    hs_codes = get_hs_codes()
    prod_data = get_production_data(year_min=2020, year_max=2020)
    trade_data = get_trade_data(year_min=2020, year_max=2020)
    
    print(f"   ✅ Countries: {len(countries)} records")
    print(f"   ✅ HS Codes: {len(hs_codes)} records")
    print(f"   ✅ Production Data: {len(prod_data)} records")
    print(f"   ✅ Trade Data: {len(trade_data)} records\n")
except Exception as e:
    print(f"   ⚠️  Data retrieval warning: {e}\n")

# Test 7: Verify page files exist
print("7️⃣  Verifying page files...")
pages_dir = os.path.join(os.path.dirname(__file__), 'app', 'pages')
required_pages = [
    '1_📊_Production_Analysis.py',
    '2_🔄_Trade_QC.py',
    '3_🗺️_Geospatial_Maps.py',
    '4_🌊_Material_Flow.py'
]

all_exist = True
for page in required_pages:
    path = os.path.join(pages_dir, page)
    if os.path.exists(path):
        print(f"   ✅ {page}")
    else:
        print(f"   ❌ {page} NOT FOUND")
        all_exist = False

if all_exist:
    print()
else:
    print()
    sys.exit(1)

# Summary
print("="*80)
print("✅ MVP STARTUP VERIFICATION COMPLETE")
print("="*80)
print("\n🚀 Ready to launch! Run: streamlit run app/app.py\n")
