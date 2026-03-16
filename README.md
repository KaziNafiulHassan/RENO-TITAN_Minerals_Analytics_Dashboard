# RENO-TITAN Intelligence Platform

Critical Minerals Supply Chain Analytics & Visualization.
A Streamlit-based analytics platform for analyzing the global supply chain of critical minerals — Titanium, Zirconium, and Rare Earth Elements (REE) — from mine production through trade to processing.

---

## Project Overview

Aggregates data from authoritative sources (USGS, BGS, UN Comtrade) to provide:

- **Production Analysis**: Compare mining output trends across USGS and BGS data sources
- **Trade Quality Control**: Detect discrepancies through bilateral trade mirror analysis
- **Geospatial Visualization**: Choropleth maps for production intensity and flow maps for trade routes
- **Material Flow Modeling**: Sankey diagrams showing ore-to-product transformations with mass balance validation

---

## Modules

| Module | Status | Key Features |
| -------- | -------- | -------------- |
| Production Analysis | Complete | USGS vs BGS comparison, top producers, trend analysis, CSV export |
| Trade QC | Complete | Route analysis, unit value anomalies, exporter vs partner comparison |
| Geospatial Maps | Complete | Production choropleths, trade flow maps, interactive Folium maps |
| Material Flow | Complete | Sankey diagrams, mass balance validation, processing splits |

---

## Tech Stack

| Component | Technology |
| ----------- | ------------ |
| Frontend | Streamlit |
| Backend Database | Supabase (PostgreSQL with PostGIS) |
| Language | Python 3.11+ |
| Visualizations | Plotly, Folium, Leaflet.js |
| Data Processing | Pandas, NumPy |
| Package Manager | uv |

---

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Supabase project with credentials
- Git

### Installation

```bash
git clone <repo-url>
cd reno-titan-intelligence-platform

# Install dependencies
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your SUPABASE_URL and SUPABASE_KEY

# Load data (first time only)
python etl/run_ingestion.py

# Launch the app
bash run_app.sh
# or: uv run streamlit run app/app.py
```

App opens at `http://localhost:8501`.

---

## Project Structure

```text
reno-titan-intelligence-platform/
├── app/
│   ├── app.py                          # Streamlit home page
│   ├── pages/
│   │   ├── 1_📊_Production_Analysis.py
│   │   ├── 2_🔄_Trade_QC.py
│   │   ├── 3_🗺️_Geospatial_Maps.py
│   │   └── 4_🌊_Material_Flow.py
│   └── utils/
│       ├── database.py                 # Supabase query functions
│       ├── visualizations.py           # Plotly / Folium charts
│       ├── calculations.py             # Mass balance, unit values
│       └── country_coordinates.py      # Coordinate lookup
├── etl/
│   ├── config.py                       # Configuration & country mapping
│   ├── run_ingestion.py                # ETL orchestrator
│   └── loaders/
│       ├── bgs_production.py
│       ├── usgs_production.py
│       └── trade_data.py
├── database/
│   └── init_schema.sql                 # Supabase schema (run once)
├── docs/                               # Supporting documentation
├── data/
│   └── raw/                            # Source CSV files
├── pyproject.toml                      # Project metadata and dependencies (uv)
├── requirements.txt                    # Deployment artifact for Streamlit Cloud
├── run_app.sh                          # Launch script
└── .env                                # Supabase credentials (not committed)
```

---

## Database Schema

### Core Tables

| Table | Purpose |
| ------- | --------- |
| `countries` | Country reference with ISO3 codes and PostGIS geometries |
| `hs_codes` | HS-6 code reference for trade tracking |
| `production_data` | Annual production from USGS and BGS |
| `trade_data` | Bilateral trade flows with value and quantity |
| `processing_splits` | Material flow coefficients (ore → intermediate → product) |

### Views

| View | Purpose |
| ------ | --------- |
| `mirror_discrepancies` | Bilateral comparison of export vs import reports |
| `top_routes` | Aggregated trade routes ranked by value |

See [docs/database_schema_final.md](docs/database_schema_final.md) for full specifications.

---

## Data Sources

| Dataset | Source | Records |
| --------- | -------- | --------- |
| Titanium production | USGS (1950–2022) | ~5,900 |
| Titanium / Zirconium / REE production | BGS (1970–2022) | ~6,200 |
| Trade flows (HS 261400) | UN Comtrade (1992–2018) | ~2,700 |

---

## Dependency Management

This project uses **uv** for local development and `requirements.txt` for deployment.

| Context | Command | File used |
| --------- | --------- | ----------- |
| Local development | `uv sync` | `pyproject.toml` + `uv.lock` |
| Add a package | `uv add <package>` | `pyproject.toml` |
| Streamlit Community Cloud | automatic | `requirements.txt` |
| Regenerate deployment file | `uv export --format requirements-txt --no-hashes -o requirements.txt` | — |

`requirements.txt` is a generated deployment artifact. Do not edit it manually — regenerate it from `pyproject.toml` before deploying.

---

## Troubleshooting

### `SUPABASE_URL and SUPABASE_KEY not found`

Check that `.env` exists and contains both variables.

### `Failed to connect to Supabase`

```bash
python -c "from app.utils.database import test_connection; test_connection()"
```

Verify credentials and that the Supabase project is active.

### `relation 'countries' does not exist`

Run the SQL schema in the Supabase SQL Editor: `database/init_schema.sql`

### `No data available`

Run the ETL pipeline: `python etl/run_ingestion.py`

### Streamlit not starting

```bash
python --version          # must be 3.11+
uv run streamlit --version
uv run streamlit run app/app.py
```

### Port already in use

```bash
uv run streamlit run app/app.py --server.port 8502
```

---

## Known Limitations (MVP)

1. **Trade data incomplete**: Only titanium ore (HS 261400) loaded; import flows missing for full mirror analysis
2. **Processing splits hardcoded**: `processing_splits` table not yet populated from database
3. **Geographic accuracy**: Maps use simplified country centroids
4. **Stock changes simplified**: Near-zero approximation for MVP mass balance

---

## Data Quality Standards

- Country names mapped to ISO3 codes (>95% coverage target)
- Quality flags: `Official`, `Estimated`, `Mirror-Derived`
- Uncertainty factors tracked for all calculations
- Zero/negative quantities filtered from unit value analysis
- Outliers identified at >3σ threshold

---

## Contributing

1. Create a feature branch from `main`
2. Follow conventions in [docs/description_of_the_application.md](docs/description_of_the_application.md)
3. Test locally: `bash run_app.sh`
4. Submit merge request with test results

---

## Documentation

- [docs/database_schema_final.md](docs/database_schema_final.md) — Database design
- [docs/mass_balance_equation_requirements.md](docs/mass_balance_equation_requirements.md) — Material flow equations
- [docs/DATA_ANALYSIS.md](docs/DATA_ANALYSIS.md) — Data structure and analysis notes
- [docs/CHANGELOG.md](docs/CHANGELOG.md) — Change history

---

**Last Updated**: March 2026 | **Status**: Active Development |
[GitLab Repository](https://gitlab.h2.de/ingenieuroekologie/reno-titan-intelligence-platform)
