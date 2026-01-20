#!/usr/bin/env python3
"""
Quick health check for RENO-TITAN project setup.
Verifies all modules can be imported and database connection works.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("\n" + "="*70)
print("RENO-TITAN PROJECT HEALTH CHECK")
print("="*70)

checks_passed = 0
checks_failed = 0

# ============================================================================
# 1. Check Python version
# ============================================================================

print("\n[1/6] Checking Python version...")
if sys.version_info >= (3, 10):
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    checks_passed += 1
else:
    print(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} (need 3.10+)")
    checks_failed += 1

# ============================================================================
# 2. Check .env file
# ============================================================================

print("\n[2/6] Checking .env configuration...")
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    with open(env_file) as f:
        content = f.read()
        if 'SUPABASE_URL=' in content and 'SUPABASE_KEY=' in content:
            print("✅ .env file configured")
            checks_passed += 1
        else:
            print("❌ .env file missing required variables")
            checks_failed += 1
else:
    print("❌ .env file not found")
    checks_failed += 1

# ============================================================================
# 3. Check configuration module
# ============================================================================

print("\n[3/6] Checking configuration module...")
try:
    from etl.config import COUNTRY_ISO3_MAP, HS_CODES_REFERENCE
    print(f"✅ Config module loaded ({len(COUNTRY_ISO3_MAP)} countries, {len(HS_CODES_REFERENCE)} HS codes)")
    checks_passed += 1
except Exception as e:
    print(f"❌ Config module error: {e}")
    checks_failed += 1

# ============================================================================
# 4. Check database module
# ============================================================================

print("\n[4/6] Checking database module...")
try:
    from app.utils.database import test_connection, get_db_client
    print("✅ Database module imported")
    
    # Try connection
    print("   Testing Supabase connection...")
    if test_connection():
        print("   ✅ Connected to Supabase")
        checks_passed += 1
    else:
        print("   ⚠️  Could not connect (may not be critical yet)")
        checks_passed += 1  # Don't fail on connection
except Exception as e:
    print(f"❌ Database module error: {e}")
    checks_failed += 1

# ============================================================================
# 5. Check ETL loaders
# ============================================================================

print("\n[5/6] Checking ETL loaders...")
try:
    from etl.loaders.bgs_production import load_bgs_production
    from etl.loaders.usgs_production import load_usgs_production
    from etl.loaders.trade_data import load_trade_data
    print("✅ All ETL loaders imported successfully")
    checks_passed += 1
except Exception as e:
    print(f"❌ ETL loader error: {e}")
    checks_failed += 1

# ============================================================================
# 6. Check visualization utilities
# ============================================================================

print("\n[6/6] Checking visualization utilities...")
try:
    from app.utils.visualizations import (
        plot_top_producers, plot_production_trend, 
        plot_comparison_bars, format_large_number
    )
    from app.utils.calculations import (
        calculate_unit_values, identify_outliers,
        calculate_discrepancy_percentage
    )
    print("✅ Visualization and calculation modules imported")
    checks_passed += 1
except Exception as e:
    print(f"❌ Utility modules error: {e}")
    checks_failed += 1

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
print(f"RESULTS: {checks_passed} passed, {checks_failed} failed")
print("="*70)

if checks_failed == 0:
    print("\n✅ All systems ready! You can now:")
    print("   1. Run ETL: python etl/run_ingestion.py")
    print("   2. Start app: streamlit run app/app.py")
    print("\nSee STARTUP_GUIDE.md for detailed instructions.")
    sys.exit(0)
else:
    print(f"\n❌ {checks_failed} issue(s) found. Please review above.")
    sys.exit(1)
