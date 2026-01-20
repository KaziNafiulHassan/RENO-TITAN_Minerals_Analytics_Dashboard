# RENO-TITAN Application Ready - Startup Instructions

**Date**: January 20, 2026  
**Status**: ✅ Ready to Launch

---

## What Has Been Built

### ✅ **Complete ETL Pipeline**
- Database connection module (`app/utils/database.py`)
- Production loaders (BGS & USGS)
- Trade data loader
- Orchestrator script (`etl/run_ingestion.py`)

### ✅ **Database Schema** 
- SQL schema ready in `database/init_schema.sql`
- 5 tables: countries, hs_codes, production_data, trade_data, processing_splits
- Proper indexes and constraints

### ✅ **Utility Modules**
- Visualization functions (Plotly charts)
- Calculation functions (mass balance, discrepancies, outliers)
- Database query functions with caching support

### ✅ **Module 1: Production Analysis**
- Top 10 producers visualization
- Trend analysis over time
- USGS vs BGS comparison
- Discrepancy detection & highlighting
- CSV export functionality

### ✅ **Supabase Integration**
- Credentials configured in `.env`
- Connection test function ready
- Batch insert functions for data loading

---

## Step-by-Step Startup

### Step 1: Install Dependencies

```bash
cd /home/kazi-nafiul-hassan/Hochschule\ Magdeburg-Stendal/RENO_TITAN_Project/code/reno-titan-intelligence-platform

pip install -r requirements.txt
```

**Expected output**: All packages installed successfully

---

### Step 2: Initialize Database Schema

Open Supabase dashboard and run the SQL script:

1. Go to **https://app.supabase.com**
2. Select your project
3. Click **SQL Editor** → **New Query**
4. Copy contents of `database/init_schema.sql` 
5. Paste and run the query

**Expected output**: All tables created successfully

Alternatively, you can run the schema creation in the Python script automatically.

---

### Step 3: Load Data into Database

```bash
python etl/run_ingestion.py
```

**This will:**
1. ✅ Test Supabase connection
2. ✅ Insert countries reference data
3. ✅ Insert HS codes reference data
4. ✅ Load BGS production data (Titanium, Zirconium, REE)
5. ✅ Load USGS production data (Titanium)
6. ✅ Load trade data
7. ✅ Verify all data loaded successfully

**Expected output**:
```
===============================
RENO-TITAN ETL PIPELINE
===============================
✅ Supabase connection successful
✅ Countries initialized
✅ HS codes initialized
✅ Production data loaded: 10,000+ records
✅ Trade data loaded: 4,900+ records

✅ Countries          1,500 records
✅ HS Codes             20 records
✅ Production Data  11,000 records
✅ Trade Data        4,900 records

===============================
✅ ETL PIPELINE COMPLETED SUCCESSFULLY
===============================

You can now run the Streamlit app:
  streamlit run app/app.py
```

---

### Step 4: Run the Streamlit App

```bash
streamlit run app/app.py
```

**Expected output**:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://xxx.xxx.xxx.xxx:8501
```

Open browser to **http://localhost:8501**

---

## What You'll See

### Home Page
- Welcome to RENO-TITAN platform
- Module cards (4 modules)
- System status (connected/not connected)
- Quick start guide

### Sidebar Navigation
- Navigate between modules
- Filter options for each module

### Module 1: Production Analysis (✅ Ready)
**Features:**
- **Top Producers Tab**: Bar chart of top 10 producers by year
  - Filter by commodity (Titanium, Zirconium, REE)
  - Select any year in your data range
  - View ranking table
  - Download as CSV

- **Trend Analysis Tab**: Line chart of production over time
  - Select up to 10 countries to compare
  - See multi-year trends
  - Identify production changes

- **Source Comparison Tab**: USGS vs BGS comparison
  - Select a country
  - View grouped bar chart
  - See discrepancy percentages
  - Key metrics (avg, max discrepancy)
  - Warnings for data quality issues

---

## Troubleshooting

### ❌ Error: "SUPABASE_URL and SUPABASE_KEY not found"
**Solution**: Check `.env` file exists and has correct credentials
```bash
cat .env
```

### ❌ Error: "Failed to connect to Supabase"
**Solution**: 
1. Verify Supabase is online
2. Check URL and key are correct
3. Try connection test:
```bash
python -c "from app.utils.database import test_connection; test_connection()"
```

### ❌ Error: "relation 'countries' does not exist"
**Solution**: Run the SQL schema initialization script in Supabase dashboard

### ❌ Error: "No data available"
**Solution**: 
1. Check ETL completed successfully: `python etl/run_ingestion.py`
2. Verify tables have data in Supabase:
```bash
python -c "from app.utils.database import get_table_count; print(get_table_count('production_data'))"
```

### ❌ Streamlit not starting
**Solution**: 
1. Ensure requirements.txt installed: `pip install -r requirements.txt`
2. Check Python version: `python --version` (should be 3.10+)
3. Try: `python -m streamlit run app/app.py`

---

## Data Summary

### Production Data (11,000+ records)
- **Titanium**: 
  - USGS: 1950-2022 (5,900+ records)
  - BGS: 1970-2022 (3,870 records)
- **Zirconium**: BGS 1970-2022 (1,273 records)
- **Rare Earth Elements**: BGS 1970-2022 (1,114 records)

### Trade Data (4,900+ records)
- Titanium ores and concentrates (HS 261400)
- 1992-2018 period
- **⚠️ Note**: Partner country not available in current file
  - Mirror analysis deferred to Phase 6

### Geographic Coverage
- 35+ countries mapped to ISO3 codes
- From small producers to major suppliers

---

## Next Steps After Launch

### Phase 2: Module 2 (Trade QC)
- Top routes visualization
- Unit value analysis (price per tonne)
- Outlier detection
- Planned: When partner country data available

### Phase 3: Module 3 (Geospatial Maps)
- Choropleth maps (production by country)
- Flow maps (trade routes)
- Interactive filtering

### Phase 4: Module 4 (Material Flow)
- Sankey diagrams (ore → product)
- Mass balance validation
- Processing coefficients (to be curated)

---

## File Structure (Final)

```
reno-titan-intelligence-platform/
├── .env                                 ← Your Supabase credentials
├── .env.example                         ← Template
├── requirements.txt                     ← Python dependencies
├── README.md                            ← Project documentation
├── STARTUP_GUIDE.md                     ← This file
│
├── database/
│   └── init_schema.sql                  ← SQL schema (run in Supabase)
│
├── etl/
│   ├── config.py                        ← Configuration & mappings
│   ├── run_ingestion.py                 ← Main ETL orchestrator
│   └── loaders/
│       ├── bgs_production.py            ← BGS data loader
│       ├── usgs_production.py           ← USGS data loader
│       └── trade_data.py                ← Trade data loader
│
└── app/
    ├── app.py                           ← Streamlit home page
    ├── pages/
    │   ├── 1_📊_Production_Analysis.py  ← Module 1 (READY)
    │   ├── 2_🔄_Trade_QC.py             ← Module 2 (stub)
    │   ├── 3_🗺️_Maps.py                 ← Module 3 (stub)
    │   └── 4_🌊_Material_Flow.py        ← Module 4 (stub)
    └── utils/
        ├── database.py                  ← Query functions
        ├── visualizations.py            ← Plotly charts
        └── calculations.py              ← Business logic

Total: 20+ files, 3,000+ lines of code
```

---

## Commands Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Test database connection
python -c "from app.utils.database import test_connection; test_connection()"

# Load data
python etl/run_ingestion.py

# Run app
streamlit run app/app.py

# View logs
tail -f logs/etl.log

# Check specific table count
python -c "from app.utils.database import get_table_count; print(get_table_count('production_data'))"
```

---

## Success Metrics

Once running successfully, you should see:

✅ **Home Page Loads**: Welcome message and 4 module cards visible
✅ **Database Connected**: Status shows "Connected" in sidebar
✅ **Module 1 Works**: Can select commodity, year, country and see charts
✅ **Data Displays**: Top producers list and trend lines visible
✅ **Filters Work**: Changing filters updates visualizations
✅ **Download Works**: CSV export button functions
✅ **USGS vs BGS**: Comparison chart shows both sources

---

## Support

If issues arise:
1. Check `.env` file for Supabase credentials
2. Verify all tables created in Supabase dashboard
3. Run ETL script with verbose logging
4. Check Streamlit logs for errors
5. Consult DATA_ANALYSIS.md for data structure details

---

**All systems ready for launch!**  
Start with: `streamlit run app/app.py`
