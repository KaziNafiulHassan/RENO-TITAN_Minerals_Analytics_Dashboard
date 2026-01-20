# RENO-TITAN Database Schema (PostgreSQL + PostGIS)

This document defines the complete database schema for the RENO-TITAN Intelligence Platform. All tables reside in Supabase PostgreSQL with PostGIS extension for geospatial queries.

---

## 1. REFERENCE TABLES

### 1.1 `countries`
Stores country information with geospatial geometry for choropleth maps.

```sql
CREATE TABLE countries (
    iso3 VARCHAR(3) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    region VARCHAR(100),
    geometry GEOMETRY(MULTIPOLYGON, 4326),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_countries_name ON countries(name);
```

**Sample Data**:
```
iso3  | name          | region
------|---------------|----------
VNM   | Vietnam       | Asia
CHN   | China         | Asia
USA   | United States | North America
DEU   | Germany       | Europe
...
```

---

### 1.2 `hs_codes`
Reference table for HS-6 codes used in trade tracking.

```sql
CREATE TABLE hs_codes (
    code VARCHAR(6) PRIMARY KEY,
    description VARCHAR(500) NOT NULL,
    commodity_group VARCHAR(50),
    material_type VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_hs_codes_commodity ON hs_codes(commodity_group);
CREATE INDEX idx_hs_codes_material ON hs_codes(material_type);
```

**Sample Data**:
```
code   | description                  | commodity_group | material_type
-------|------------------------------|-----------------|-------------------
261400 | Titanium ores and concentr.  | Titanium        | Raw Material
282300 | Titanium oxides              | Titanium        | Intermediate
810810 | Zirconium in other forms     | Zirconium       | Intermediate
281410 | Rare earth oxides/salts      | REE             | Intermediate
...
```

**HS Codes to Seed**:
- **Titanium**: 261400 (ores), 282300 (oxides), 810810 (metal)
- **Zirconium**: 261510 (ores), 282560 (oxide), 810600 (metal)
- **REE**: 284610 (oxides/salts), 853021 (permanent magnets)

---

## 2. DATA TABLES

### 2.1 `production_data`
Annual production data from USGS, BGS, and other sources.

```sql
CREATE TABLE production_data (
    id SERIAL PRIMARY KEY,
    commodity VARCHAR(50) NOT NULL,  -- e.g., 'titanium_minerals', 'zircon', 'ree'
    country_iso3 VARCHAR(3) NOT NULL,
    year INT NOT NULL,
    quantity DECIMAL(15, 2) NOT NULL,
    unit VARCHAR(20) DEFAULT 'tonnes',  -- e.g., 'tonnes', 'kg', 'tonnes_tio2_equivalent'
    data_source VARCHAR(50) NOT NULL,  -- 'USGS', 'BGS', 'NationalStats'
    quality_flag VARCHAR(20) DEFAULT 'Official',  -- 'Official', 'Estimated', 'Mirror-Derived'
    uncertainty_factor DECIMAL(5, 2),  -- e.g., 0.15 for ±15%
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(commodity, country_iso3, year, data_source),
    FOREIGN KEY(country_iso3) REFERENCES countries(iso3)
);

CREATE INDEX idx_production_commodity ON production_data(commodity);
CREATE INDEX idx_production_country_year ON production_data(country_iso3, year);
CREATE INDEX idx_production_source ON production_data(data_source);
CREATE INDEX idx_production_year ON production_data(year);
```

**Data Types**:
- `commodity`: Must be one of: `titanium_minerals`, `zircon`, `rare_earth_elements`
- `unit`: Default `tonnes` (metric tons); alternative `tonnes_tio2_equivalent` for normalized comparisons
- `data_source`: Must be one of: `USGS`, `BGS`, `NationalStats`

**Sample Data**:
```
id | commodity           | country_iso3 | year | quantity   | unit    | data_source | quality_flag
---|---------------------|--------------|------|------------|---------|-------------|-----------
1  | titanium_minerals   | VNM          | 2022 | 1250000    | tonnes  | USGS        | Official
2  | titanium_minerals   | VNM          | 2022 | 1180000    | tonnes  | BGS         | Official
3  | zircon              | AUS          | 2021 | 425000     | tonnes  | BGS         | Official
...
```

---

### 2.2 `trade_data`
Bilateral trade flows from WITS, Comtrade, BACI.

```sql
CREATE TABLE trade_data (
    id SERIAL PRIMARY KEY,
    hs_code VARCHAR(6) NOT NULL,
    reporter_iso3 VARCHAR(3) NOT NULL,  -- Exporting country
    partner_iso3 VARCHAR(3) NOT NULL,   -- Importing country
    flow VARCHAR(10) NOT NULL,  -- 'export', 'import'
    year INT NOT NULL,
    month INT,  -- Optional: 1-12 for monthly data
    value_usd DECIMAL(15, 2),  -- Trade value in USD
    quantity DECIMAL(15, 2),  -- Quantity in units (see quantity_unit)
    quantity_unit VARCHAR(20) DEFAULT 'tonnes',
    data_source VARCHAR(50),  -- 'WITS', 'Comtrade', 'BACI'
    quality_flag VARCHAR(20) DEFAULT 'Official',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(hs_code, reporter_iso3, partner_iso3, flow, year, month, data_source),
    FOREIGN KEY(hs_code) REFERENCES hs_codes(code),
    FOREIGN KEY(reporter_iso3) REFERENCES countries(iso3),
    FOREIGN KEY(partner_iso3) REFERENCES countries(iso3)
);

CREATE INDEX idx_trade_hs_code ON trade_data(hs_code);
CREATE INDEX idx_trade_reporter ON trade_data(reporter_iso3);
CREATE INDEX idx_trade_partner ON trade_data(partner_iso3);
CREATE INDEX idx_trade_flow ON trade_data(flow);
CREATE INDEX idx_trade_year ON trade_data(year);
CREATE INDEX idx_trade_route ON trade_data(reporter_iso3, partner_iso3, year);
```

**Data Types**:
- `flow`: Must be one of: `export`, `import` (lowercase)
- `quantity_unit`: Default `tonnes`; alternatives: `kg`, `number_of_units`
- `data_source`: One of: `WITS`, `Comtrade`, `BACI`

**Sample Data**:
```
id | hs_code | reporter_iso3 | partner_iso3 | flow   | year | value_usd  | quantity  | data_source
---|---------|---------------|--------------|--------|------|------------|-----------|------------
1  | 261400  | VNM           | CHN          | export | 2022 | 5000000    | 45000     | Comtrade
2  | 261400  | CHN           | VNM          | import | 2022 | 4800000    | 45000     | Comtrade
3  | 282300  | CHN           | DEU          | export | 2022 | 15000000   | 35000     | WITS
...
```

---

### 2.3 `processing_splits`
Coefficients for ore-to-product transformations (manually curated from USGS MIS).

```sql
CREATE TABLE processing_splits (
    id SERIAL PRIMARY KEY,
    commodity VARCHAR(50) NOT NULL,  -- e.g., 'titanium_minerals'
    country_iso3 VARCHAR(3),  -- NULL = global default
    year INT,  -- NULL = applies to all years unless overridden
    input_material VARCHAR(100) NOT NULL,  -- e.g., 'Titanium Ore'
    output_material VARCHAR(100) NOT NULL,  -- e.g., 'TiO2 Pigment'
    split_ratio DECIMAL(5, 4) NOT NULL,  -- e.g., 0.7000 for 70%
    efficiency DECIMAL(5, 4),  -- e.g., 0.85 for 85% process efficiency
    source VARCHAR(100),  -- e.g., 'USGS_MIS_2022', 'Literature'
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY(country_iso3) REFERENCES countries(iso3)
);

CREATE INDEX idx_processing_commodity ON processing_splits(commodity);
CREATE INDEX idx_processing_country_year ON processing_splits(country_iso3, year);
```

**Sample Data** (Titanium Ore → Products):
```
id | commodity       | country_iso3 | year | input_material  | output_material      | split_ratio
---|-----------------|--------------|------|-----------------|----------------------|-------------
1  | titanium        | NULL         | NULL | Titanium Ore    | TiO2 Pigment         | 0.7000
2  | titanium        | NULL         | NULL | Titanium Ore    | Ti Sponge            | 0.2500
3  | titanium        | NULL         | NULL | Titanium Ore    | Processing Losses    | 0.0500
4  | titanium        | VNM          | 2022 | Titanium Ore    | TiO2 Pigment (Local) | 0.6500
```

---

## 3. VIEWS (FOR ANALYTICS)

### 3.1 `mirror_discrepancies`
Compares exporter-reported vs importer-reported figures.

```sql
CREATE VIEW mirror_discrepancies AS
SELECT
    ex.hs_code,
    ex.year,
    ex.reporter_iso3 AS exporter,
    ex.partner_iso3 AS importer,
    ex.value_usd AS export_value,
    im.value_usd AS import_value,
    CASE
        WHEN ex.value_usd IS NOT NULL THEN
            ROUND(ABS(ex.value_usd - COALESCE(im.value_usd, 0)) / ex.value_usd * 100, 2)
        ELSE NULL
    END AS discrepancy_percent,
    CASE
        WHEN ROUND(ABS(ex.value_usd - COALESCE(im.value_usd, 0)) / ex.value_usd * 100, 2) > 10
        THEN 'HIGH'
        WHEN ROUND(ABS(ex.value_usd - COALESCE(im.value_usd, 0)) / ex.value_usd * 100, 2) > 5
        THEN 'MEDIUM'
        ELSE 'LOW'
    END AS discrepancy_severity
FROM
    trade_data ex
LEFT JOIN trade_data im ON
    ex.hs_code = im.hs_code
    AND ex.reporter_iso3 = im.partner_iso3
    AND ex.partner_iso3 = im.reporter_iso3
    AND ex.year = im.year
    AND ex.flow = 'export'
    AND im.flow = 'import'
WHERE
    ex.flow = 'export'
ORDER BY
    discrepancy_percent DESC;
```

---

### 3.2 `top_routes`
Aggregated bilateral trade routes ranked by value.

```sql
CREATE VIEW top_routes AS
SELECT
    hs_code,
    reporter_iso3,
    partner_iso3,
    year,
    SUM(value_usd) AS total_value_usd,
    SUM(quantity) AS total_quantity,
    COUNT(*) AS num_records,
    ROUND(AVG(value_usd / NULLIF(quantity, 0)), 2) AS avg_unit_value
FROM
    trade_data
WHERE
    flow = 'export'
GROUP BY
    hs_code, reporter_iso3, partner_iso3, year
ORDER BY
    year DESC, total_value_usd DESC;
```

---

## 4. DATA IMPORT SPECIFICATIONS

### 4.1 Country ISO3 Mapping
Comprehensive mapping of country names from CSVs to ISO3 codes.

**Required Coverage** (from existing CSV files):
- Vietnam → VNM
- China → CHN
- United States → USA
- Australia → AUS
- Germany → DEU
- Japan → JPN
- India → IND
- [More countries as discovered in CSVs]

---

### 4.2 HS Code Standardization
- Zero-pad to 6 digits: `2614` → `261400`
- Store as VARCHAR(6) not INT (to preserve leading zeros)
- Validate against official HS code list

---

### 4.3 Data Quality Flags

| Flag | Definition | Usage |
|------|-----------|-------|
| `Official` | Reported by official statistical authority | Primary data source |
| `Estimated` | Interpolated/estimated from partial data | Mark with uncertainty_factor |
| `Mirror-Derived` | Calculated from partner country imports | Used to fill gaps |

---

## 5. PERFORMANCE OPTIMIZATION

### Indexes (Created Above)
- Production: (commodity, country_iso3, year), (year), (data_source)
- Trade: (hs_code, reporter_iso3, partner_iso3, year, flow)
- Processing: (commodity, country_iso3, year)

### Query Optimization Tips
1. Filter by year early to reduce table scans
2. Use production view for mirror analysis (pre-joined)
3. Limit trade_data queries to specific HS codes
4. Cache country geometries for choropleth rendering

---

## 6. INITIAL DATA POPULATION

### Step 1: Load Countries
Insert all countries with ISO3 codes and names. Geometry to be added after natural earth GeoJSON import.

### Step 2: Seed HS Codes
Insert 15-20 primary HS codes for Titanium, Zirconium, REE (see Section 1.2).

### Step 3: ETL Pipeline
Run loaders sequentially:
1. `etl/loaders/bgs_production.py` → `production_data`
2. `etl/loaders/usgs_production.py` → `production_data`
3. `etl/loaders/trade_data.py` → `trade_data`

### Step 4: Manually Curate Processing Splits
Populate `processing_splits` with coefficients from USGS Mineral Industry Surveys (post-Phase 1).

---

## 7. SUPABASE-SPECIFIC SETTINGS

### Authentication
- Public read access for non-sensitive tables (optional)
- API key required for data writes

### RLS (Row-Level Security)
- Initially disabled for development
- Enable for production with user-level policies

### Backups
- Enable automated daily backups
- Retention: 7 days minimum

---

## Appendix: SQL Setup Script

Create `database/init_schema.sql` for one-time setup:

```sql
-- Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create all tables (see sections above)
-- Insert reference data for countries and HS codes
-- Create views
-- Create indexes

-- Run: psql -h [SUPABASE_HOST] -U [USER] -d [DB] -f database/init_schema.sql
```

---

**Last Updated**: January 2026  
**Status**: Ready for implementation with ETL loaders
