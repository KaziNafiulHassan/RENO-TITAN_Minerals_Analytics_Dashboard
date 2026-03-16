#!/bin/bash
# RENO-TITAN Intelligence Platform - Launch Script
# Usage: bash run_app.sh

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "========================================================================"
echo "RENO-TITAN Intelligence Platform"
echo "========================================================================"

# [1] Check Python
echo ""
echo "[1/3] Python version:"
python3 --version

# [2] Check database connection and data
echo ""
echo "[2/3] Checking database connection..."
python3 - <<'EOF'
try:
    from app.utils.database import test_connection, get_table_count
    if test_connection():
        print("  Connected to Supabase")
        for table in ["countries", "production_data", "trade_data"]:
            count = get_table_count(table)
            status = f"{count} records" if count > 0 else "empty — run: python etl/run_ingestion.py"
            print(f"  {table}: {status}")
    else:
        print("  Warning: not connected — check .env credentials")
except Exception as e:
    print(f"  Warning: {e}")
EOF

# [3] Launch Streamlit via uv
echo ""
echo "[3/3] Launching Streamlit app..."
echo "  URL:  http://localhost:8501"
echo "  Stop: Ctrl+C"
echo "========================================================================"
echo ""

uv run streamlit run app/app.py --logger.level=info
