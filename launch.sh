#!/bin/bash

# RENO-TITAN Quick Launch Script
# Usage: bash launch.sh

set -e  # Exit on error

echo "========================================================================"
echo "RENO-TITAN Intelligence Platform - Quick Launch"
echo "========================================================================"

# Get directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# ========================================================================
# Step 1: Verify Python
# ========================================================================

echo ""
echo "[1/4] Verifying Python installation..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $python_version found"

# ========================================================================
# Step 2: Check dependencies
# ========================================================================

echo ""
echo "[2/4] Checking dependencies..."
if python3 health_check.py; then
    echo "✅ All systems check passed"
else
    echo "⚠️  Some checks failed - installing dependencies..."
    pip install -r requirements.txt
fi

# ========================================================================
# Step 3: Verify database
# ========================================================================

echo ""
echo "[3/4] Checking database connection..."
python3 << 'PYTHON_SCRIPT'
try:
    from app.utils.database import test_connection, get_table_count
    if test_connection():
        print("✅ Database connected successfully")
        for table in ['countries', 'production_data']:
            count = get_table_count(table)
            if count > 0:
                print(f"   ✅ {table}: {count} records")
            else:
                print(f"   ⚠️  {table}: No data - run ETL first")
    else:
        print("⚠️  Database not connected - check .env file")
except Exception as e:
    print(f"❌ Error: {e}")
    print("   Please check .env file and Supabase connection")
PYTHON_SCRIPT

# ========================================================================
# Step 4: Launch Streamlit
# ========================================================================

echo ""
echo "[4/4] Launching Streamlit application..."
echo "========================================================================"
echo "Opening http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================================================"
echo ""

streamlit run app/app.py

# ========================================================================

exit 0
