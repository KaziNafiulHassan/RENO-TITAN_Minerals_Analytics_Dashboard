-- RENO-TITAN Database Schema Initialization
-- PostgreSQL with PostGIS extension
-- Run this script in Supabase SQL editor

-- ============================================================================
-- 1. REFERENCE TABLE: Countries
-- ============================================================================

CREATE TABLE IF NOT EXISTS countries (
    iso3 VARCHAR(3) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    region VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_countries_name ON countries(name);

-- ============================================================================
-- 2. REFERENCE TABLE: HS Codes
-- ============================================================================

CREATE TABLE IF NOT EXISTS hs_codes (
    code VARCHAR(6) PRIMARY KEY,
    description VARCHAR(500) NOT NULL,
    commodity_group VARCHAR(50),
    material_type VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_hs_codes_commodity ON hs_codes(commodity_group);
CREATE INDEX IF NOT EXISTS idx_hs_codes_material ON hs_codes(material_type);

-- ============================================================================
-- 3. DATA TABLE: Production Data
-- ============================================================================

CREATE TABLE IF NOT EXISTS production_data (
    id SERIAL PRIMARY KEY,
    commodity VARCHAR(50) NOT NULL,
    country_iso3 VARCHAR(3) NOT NULL,
    year INT NOT NULL,
    quantity DECIMAL(15, 2) NOT NULL,
    unit VARCHAR(20) DEFAULT 'tonnes',
    data_source VARCHAR(50) NOT NULL,
    quality_flag VARCHAR(20) DEFAULT 'Official',
    uncertainty_factor DECIMAL(5, 2),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(commodity, country_iso3, year, data_source),
    FOREIGN KEY(country_iso3) REFERENCES countries(iso3)
);

CREATE INDEX IF NOT EXISTS idx_production_commodity ON production_data(commodity);
CREATE INDEX IF NOT EXISTS idx_production_country_year ON production_data(country_iso3, year);
CREATE INDEX IF NOT EXISTS idx_production_source ON production_data(data_source);
CREATE INDEX IF NOT EXISTS idx_production_year ON production_data(year);

-- ============================================================================
-- 4. DATA TABLE: Trade Data
-- ============================================================================

CREATE TABLE IF NOT EXISTS trade_data (
    id SERIAL PRIMARY KEY,
    hs_code VARCHAR(6) NOT NULL,
    reporter_iso3 VARCHAR(3) NOT NULL,
    partner_iso3 VARCHAR(3),
    flow VARCHAR(10) NOT NULL,
    year INT NOT NULL,
    month INT,
    value_usd DECIMAL(15, 2),
    quantity DECIMAL(15, 2),
    quantity_unit VARCHAR(20) DEFAULT 'tonnes',
    data_source VARCHAR(50),
    quality_flag VARCHAR(20) DEFAULT 'Official',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY(hs_code) REFERENCES hs_codes(code),
    FOREIGN KEY(reporter_iso3) REFERENCES countries(iso3),
    FOREIGN KEY(partner_iso3) REFERENCES countries(iso3)
);

CREATE INDEX IF NOT EXISTS idx_trade_hs_code ON trade_data(hs_code);
CREATE INDEX IF NOT EXISTS idx_trade_reporter ON trade_data(reporter_iso3);
CREATE INDEX IF NOT EXISTS idx_trade_partner ON trade_data(partner_iso3);
CREATE INDEX IF NOT EXISTS idx_trade_flow ON trade_data(flow);
CREATE INDEX IF NOT EXISTS idx_trade_year ON trade_data(year);
CREATE INDEX IF NOT EXISTS idx_trade_route ON trade_data(reporter_iso3, partner_iso3, year);

-- ============================================================================
-- 5. DATA TABLE: Processing Splits
-- ============================================================================

CREATE TABLE IF NOT EXISTS processing_splits (
    id SERIAL PRIMARY KEY,
    commodity VARCHAR(50) NOT NULL,
    country_iso3 VARCHAR(3),
    year INT,
    input_material VARCHAR(100) NOT NULL,
    output_material VARCHAR(100) NOT NULL,
    split_ratio DECIMAL(5, 4) NOT NULL,
    efficiency DECIMAL(5, 4),
    source VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY(country_iso3) REFERENCES countries(iso3)
);

CREATE INDEX IF NOT EXISTS idx_processing_commodity ON processing_splits(commodity);
CREATE INDEX IF NOT EXISTS idx_processing_country_year ON processing_splits(country_iso3, year);

-- ============================================================================
-- Enable Row Level Security (optional)
-- ============================================================================

-- Uncomment to enable RLS for production:
-- ALTER TABLE countries ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE hs_codes ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE production_data ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE trade_data ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE processing_splits ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- End of Schema
-- ============================================================================
