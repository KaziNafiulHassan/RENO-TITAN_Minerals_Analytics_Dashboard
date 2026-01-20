"""
RENO-TITAN ETL Configuration
Centralized settings, credentials, and mappings for data ingestion.
"""

import os
from typing import Dict, Set
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# SUPABASE CONFIGURATION
# ============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY must be set in .env file"
    )

# ============================================================================
# DATABASE TABLE NAMES
# ============================================================================

TABLES = {
    "countries": "countries",
    "hs_codes": "hs_codes",
    "production_data": "production_data",
    "trade_data": "trade_data",
    "processing_splits": "processing_splits",
}

# ============================================================================
# COUNTRY ISO3 MAPPING
# Maps country names from CSV files to ISO3 codes
# Extend this mapping as new countries are discovered in data files
# ============================================================================

COUNTRY_ISO3_MAP: Dict[str, str] = {
    # Asia-Pacific
    "Vietnam": "VNM",
    "China": "CHN",
    "Australia": "AUS",
    "India": "IND",
    "Japan": "JPN",
    "South Korea": "KOR",
    "Korea": "KOR",
    "Thailand": "THA",
    "Malaysia": "MYS",
    "Indonesia": "IDN",
    "Philippines": "PHL",
    "Myanmar": "MMR",
    "Laos": "LAO",
    "Cambodia": "KHM",
    "Singapore": "SGP",
    "Hong Kong": "HKG",
    
    # Europe
    "Germany": "DEU",
    "France": "FRA",
    "United Kingdom": "GBR",
    "Russia": "RUS",
    "Italy": "ITA",
    "Spain": "ESP",
    "Netherlands": "NLD",
    "Belgium": "BEL",
    "Poland": "POL",
    "Sweden": "SWE",
    "Norway": "NOR",
    "Finland": "FIN",
    "Denmark": "DNK",
    "Austria": "AUT",
    "Czechia": "CZE",
    "Czech Republic": "CZE",
    "Hungary": "HUN",
    "Romania": "ROU",
    "Portugal": "PRT",
    "Greece": "GRC",
    "Ukraine": "UKR",
    "Turkey": "TUR",
    
    # Americas
    "United States": "USA",
    "Canada": "CAN",
    "Mexico": "MEX",
    "Brazil": "BRA",
    "Argentina": "ARG",
    "Chile": "CHL",
    "Peru": "PER",
    "Colombia": "COL",
    
    # Africa
    "South Africa": "ZAF",
    "Egypt": "EGY",
    "Nigeria": "NGA",
    "Kenya": "KEN",
    "Ethiopia": "ETH",
    "Morocco": "MAR",
    "Algeria": "DZA",
    "Angola": "AGO",
    "Tanzania": "TZA",
    "Uganda": "UGA",
    
    # Middle East
    "Saudi Arabia": "SAU",
    "Iran": "IRN",
    "Israel": "ISR",
    "United Arab Emirates": "ARE",
    "Iraq": "IRQ",
    "Kuwait": "KWT",
}

# ============================================================================
# DATA SOURCE ENUMERATIONS
# ============================================================================

DATA_SOURCES = {
    "production": {"USGS", "BGS", "NationalStats"},
    "trade": {"WITS", "Comtrade", "BACI"},
}

QUALITY_FLAGS = {"Official", "Estimated", "Mirror-Derived"}

FLOW_DIRECTIONS = {"export", "import"}

COMMODITIES = {
    "titanium_minerals",
    "zircon",
    "rare_earth_elements",
}

QUANTITY_UNITS = {
    "tonnes",
    "kg",
    "tonnes_tio2_equivalent",
    "tonnes_zro2_equivalent",
    "number_of_units",
}

# ============================================================================
# HS CODE REFERENCE DATA
# Primary HS-6 codes for monitoring
# ============================================================================

HS_CODES_REFERENCE = {
    # Titanium
    "261400": {
        "description": "Titanium ores and concentrates",
        "commodity_group": "Titanium",
        "material_type": "Raw Material",
    },
    "282300": {
        "description": "Titanium oxides",
        "commodity_group": "Titanium",
        "material_type": "Intermediate",
    },
    "810810": {
        "description": "Titanium in other forms (excl. powder)",
        "commodity_group": "Titanium",
        "material_type": "Product",
    },
    
    # Zirconium
    "261510": {
        "description": "Zirconium ores and concentrates",
        "commodity_group": "Zirconium",
        "material_type": "Raw Material",
    },
    "282560": {
        "description": "Zirconium oxides and hydroxides",
        "commodity_group": "Zirconium",
        "material_type": "Intermediate",
    },
    "810600": {
        "description": "Zirconium and articles thereof",
        "commodity_group": "Zirconium",
        "material_type": "Product",
    },
    
    # Rare Earth Elements
    "284610": {
        "description": "Rare earth oxides and hydroxides, salts thereof",
        "commodity_group": "REE",
        "material_type": "Intermediate",
    },
    "853021": {
        "description": "Permanent magnets of sintered metal oxides",
        "commodity_group": "REE",
        "material_type": "Product",
    },
}

# ============================================================================
# DATA FILE PATHS
# ============================================================================

DATA_RAW_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
DATA_PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

CSV_FILES = {
    "titanium_usgs": os.path.join(DATA_RAW_DIR, "Titanium Minerals Production Data from USGS.csv"),
    "titanium_bgs": os.path.join(DATA_RAW_DIR, "Titanium Minerals Production Data from BGS.csv"),
    "zirconium_bgs": os.path.join(DATA_RAW_DIR, "Zirconium Production Data from BGS.csv"),
    "ree_bgs": os.path.join(DATA_RAW_DIR, "Rare Earth Minerals Production Data from BGS.csv"),
    "titanium_trade": os.path.join(DATA_RAW_DIR, "Titanium Import & Export_sample_not complete.csv"),
}

# ============================================================================
# VALIDATION THRESHOLDS
# ============================================================================

# Production data quality thresholds
MIN_VALID_PRODUCTION = 1  # tonnes
MAX_ALLOWED_OUTLIER_ZSCORE = 3  # Standard deviations

# Trade data thresholds
MIRROR_DISCREPANCY_THRESHOLD = 0.10  # 10% allowed difference
UNIT_VALUE_OUTLIER_ZSCORE = 3  # For detecting anomalous prices

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_iso3_from_country_name(country_name: str) -> str:
    """
    Retrieve ISO3 code from country name with fuzzy matching support.
    
    Args:
        country_name: Name of country as it appears in data
        
    Returns:
        ISO3 code (e.g., 'VNM')
        
    Raises:
        ValueError: If country not found in mapping
    """
    if country_name in COUNTRY_ISO3_MAP:
        return COUNTRY_ISO3_MAP[country_name]
    
    # Try case-insensitive matching
    for key, value in COUNTRY_ISO3_MAP.items():
        if key.lower() == country_name.lower():
            return value
    
    raise ValueError(f"Country '{country_name}' not found in ISO3 mapping. Add to COUNTRY_ISO3_MAP.")

def validate_commodity(commodity: str) -> bool:
    """Check if commodity is in allowed list."""
    return commodity in COMMODITIES

def validate_data_source(source: str, data_type: str) -> bool:
    """Check if data source is valid for given data type."""
    return source in DATA_SOURCES.get(data_type, set())

def validate_quality_flag(flag: str) -> bool:
    """Check if quality flag is valid."""
    return flag in QUALITY_FLAGS

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# ============================================================================

if __name__ == "__main__":
    # Quick verification
    print("Configuration loaded successfully.")
    print(f"Supabase URL: {SUPABASE_URL[:30]}...")
    print(f"Countries mapped: {len(COUNTRY_ISO3_MAP)}")
    print(f"HS Codes seeded: {len(HS_CODES_REFERENCE)}")
    print(f"Raw data files found: {len([f for f in CSV_FILES.values() if os.path.exists(f)])}/{len(CSV_FILES)}")
