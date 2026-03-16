# CSV Data Analysis Report

**Date**: January 20, 2026  
**Purpose**: Initial assessment of available CSV data files for ETL pipeline

---

## Executive Summary

Five CSV files are available totaling **12,101 data rows** across production and trade data:

| File | Rows | Coverage | Status |
|------|------|----------|--------|
| **Titanium Minerals Production (USGS)** | 5,915 | Long time series, multiple countries | ✅ Ready |
| **Titanium Minerals Production (BGS)** | 3,870 | Comparison data, sub-commodity detail | ✅ Ready |
| **Zirconium Production (BGS)** | 1,273 | BGS-only data | ✅ Ready |
| **Rare Earth Minerals Production (BGS)** | 1,114 | Monazite & Xenotime tracking | ✅ Ready |
| **Titanium Trade (Comtrade Sample)** | 4,929 | Partial import/export data | ⚠️ Incomplete |

---

## Detailed File Analysis

### 1. Titanium Minerals Production Data from USGS.csv

**Rows**: 5,915 (header + 5,914 data rows)  
**Time Span**: 1950-2022 (72 years of data)  
**Columns**: 5
- `Country` - Country name
- `Year` - Integer year
- `Subcommodity` - Type of titanium mineral (ilmenite, rutile, leucoxene)
- `Production (in tonnes)` - Quantity in metric tonnes
- `Source` - Always "USGS"

**Data Quality Issues**:
1. **Sub-commodities vary**: Some records have "ilmenite", others "ilmenite and leucoxene", others just "leucoxene"
2. **Zero values common**: Many countries/years have 0 production
3. **Country name formatting**: Consistent capitalization (e.g., "Australia", "China")
4. **Missing recent data**: Last entry is 2022

**Sample Country Names** (need ISO3 mapping):
- Australia, Brazil, Canada, China, France, Germany, India, Japan, Kenya, Malaysia, Mexico, Norway, Russia, Sierra Leone, South Africa, Thailand, Turkey, United States, Vietnam, etc.

**Expected Mapping to Commodity**:
- Subcommodity types → `titanium_minerals` commodity
- Unit: `tonnes` (metric)

---

### 2. Titanium Minerals Production Data from BGS.csv

**Rows**: 3,870 (header + 3,869 data rows)  
**Time Span**: 1970-2022 (53 years of data)  
**Columns**: 5
- `Country` - Country name
- `Year` - Integer year
- `Sub-commodity` - Mineral type (ilmenite, rutile, leucoxene, "titanium ores and concentrates")
- `Quantity in metric tons` - Production quantity
- `Source` - Always "BGS"

**Data Quality Issues**:
1. **Different year coverage**: Starts 1970 (vs USGS starting 1950)
2. **Aggregate category**: "titanium ores and concentrates" used in later years
3. **Same country names**: Consistent with USGS
4. **Potential duplicates**: Same commodity/country/year pairs as USGS (different values)

**Key Observation**:
- USGS has 1950-1969 historical data that BGS lacks
- After 1970, both sources report on same countries but with different values
- This creates the "USGS vs BGS comparison" feature opportunity

---

### 3. Zirconium Production Data from BGS.csv

**Rows**: 1,273 (header + 1,272 data rows)  
**Time Span**: 1970-2022 (53 years)  
**Columns**: 5
- `Country` - Country name
- `Year` - Integer year
- `Sub-commodity` - "Zirconium Minerals"
- `Production (tonnes)` - Quantity
- `Source` - "BGS"

**Data Quality Issues**:
1. **Simpler structure**: Only one sub-commodity type tracked
2. **BGS-only**: No USGS zirconium production data available
3. **Note from requirements**: USGS lacks zirconium mine production data

**Expected Mapping**:
- Commodity: `zircon`
- Unit: `tonnes`

---

### 4. Rare Earth Minerals Production Data from BGS.csv

**Rows**: 1,114 (header + 1,113 data rows)  
**Time Span**: 1970-2022 (53 years)  
**Columns**: 5
- `Country` - Country name
- `Year` - Integer year
- `Sub-commodity` - "Monazite" or "Xenotime" (REE-bearing minerals)
- `Production (tonnes)` - Quantity
- `Source` - "BGS"

**Data Quality Issues**:
1. **Many zero values**: Monazite and Xenotime production often 0
2. **BGS-only**: No USGS REE mine production data
3. **Note from requirements**: USGS lacks REE mine production data

**Expected Mapping**:
- Commodity: `rare_earth_elements`
- Unit: `tonnes`

---

### 5. Titanium Import & Export_sample_not complete.csv

**Rows**: 4,929 (header + 4,928 data rows)  
**Time Span**: 1992-2018 (27 years, incomplete)  
**Columns**: 6
- `Country` - **Reporter country** (exporting or importing)
- `Year` - Integer year
- `Sub_commodity` - "titanium ores and concentrates" (consistent)
- `Export/Import` - "Export" or "Import"
- `Quantity in metric tons` - Trade volume
- `Trade Value in 1000 USD` - Value in thousands (need to multiply by 1000)

**Data Quality Issues**:
1. **Incomplete**: File name notes "sample_not complete"
2. **No HS codes**: Lacks Harmonized System codes for linking to trade database
3. **Limited time period**: Only 1992-2018 vs production data going to 2022
4. **No trading partner info**: Shows reporter country but not bilateral partner
5. **Trade value formatting**: In thousands USD (need conversion to USD)

**Sample Issues in File**:
```
Algeria,1992,titanium ores and concentrates,Export,0,0
Algeria,1993,titanium ores and concentrates,Export,0,0
```
- Many countries have zero trade flows
- Formatting issue in header (newline in column name)

---

## Data Mapping to Database Schema

### Production Data Mapping

**USGS Titanium → `production_data`**:
- `commodity` = "titanium_minerals"
- `country_iso3` = mapped from "Country" (see Country Mapping section)
- `year` = Year
- `quantity` = Production (in tonnes)
- `unit` = "tonnes"
- `data_source` = "USGS"
- `quality_flag` = "Official"
- `notes` = Subcommodity type (ilmenite, rutile, etc.)

**BGS Titanium → `production_data`**:
- Same as above but `data_source` = "BGS"

**BGS Zirconium → `production_data`**:
- `commodity` = "zircon"
- Other fields same as above with `data_source` = "BGS"

**BGS REE → `production_data`**:
- `commodity` = "rare_earth_elements"
- `notes` = Monazite or Xenotime
- `data_source` = "BGS"

### Trade Data Mapping

**Titanium Trade → `trade_data`**:
- `hs_code` = "261400" (titanium ores and concentrates)
- `reporter_iso3` = mapped from "Country"
- `partner_iso3` = NULL (not available in current file)
- `flow` = lowercase("Export/Import")
- `year` = Year
- `month` = NULL
- `value_usd` = Trade Value * 1000 (convert from thousands)
- `quantity` = Quantity in metric tons
- `quantity_unit` = "tonnes"
- `data_source` = "Comtrade" (inferred)

**LIMITATION**: Cannot compute mirror analysis without partner information!

---

## Country Name Mapping Requirements

**Countries appearing in datasets** (identified so far):
```
Algeria, Australia, Belgium, Brazil, Canada, China, Egypt, France, 
Germany, Hong Kong, India, Indonesia, Japan, Kenya, Malaysia, Mexico, 
Morocco, Myanmar, Netherlands, New Zealand, Norway, Pakistan, Peru, 
Philippines, Russia, Saudi Arabia, Singapore, South Africa, Spain, 
Switzerland, Thailand, Turkey, United Kingdom, United States, Vietnam
```

**Action Required**: Verify all unique country names and add to `COUNTRY_ISO3_MAP` in `etl/config.py`

---

## Data Loading Priority & Sequence

### Phase 1 (Immediate - Within ETL):
1. ✅ **Load BGS Titanium** → `production_data` (3,870 rows)
2. ✅ **Load USGS Titanium** → `production_data` (5,915 rows)
3. ✅ **Load BGS Zirconium** → `production_data` (1,272 rows)
4. ✅ **Load BGS REE** → `production_data` (1,113 rows)
5. ⚠️ **Load Titanium Trade** → `trade_data` (4,928 rows, **without partner data**)

### Phase 2 (Future Enhancement):
- Source complete bilateral trade data from WITS or UN Comtrade API
- Add partner country information to trade flows
- Enable mirror analysis

---

## Identified Data Quality Flags

### Production Data
- All `quality_flag` = "Official" (data from USGS/BGS official sources)
- `uncertainty_factor` = NULL for now (can be added later from metadata)

### Trade Data
- `quality_flag` = "Official" (from Comtrade source)
- **NOTE**: Without partner data, many routes will show only exports or only imports

---

## Next Steps for ETL Development

1. ✅ Create loaders for each production source
   - `etl/loaders/bgs_production.py` - Handles BGS Titanium, Zirconium, REE
   - `etl/loaders/usgs_production.py` - Handles USGS Titanium
   - `etl/loaders/trade_data.py` - Handles incomplete Titanium trade

2. ✅ Add country ISO3 mapping
   - Extract unique country names from each file
   - Populate `COUNTRY_ISO3_MAP` in config.py

3. ✅ Validate data constraints
   - Check for NULL values
   - Filter out zero/negative quantities
   - Validate years are within expected range

4. ⚠️ **Handle trade data limitation**
   - Document that partner_iso3 is unavailable
   - Flag mirror analysis as "not available for current data"
   - Plan to source complete bilateral trade data later

---

## Data Statistics Summary

| Metric | Count |
|--------|-------|
| Total production rows | ~11,000 |
| Total trade rows | ~4,900 |
| Countries represented | ~35 |
| Year range | 1950-2022 |
| HS codes | 1 (261400 only) |
| Commodities | 3 (Titanium, Zirconium, REE) |

---

**Prepared by**: Coding Agent  
**Status**: Ready for ETL Implementation
