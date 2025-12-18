# Implementation Document for RENO-TITAN Intelligence Platform

## Code Structure
```
reno-titan-intelligence-platform/
├── backend/                 # FastAPI app
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app instance
│   │   ├── models/          # Pydantic models
│   │   ├── routes/          # API endpoints (e.g., production.py, trade.py)
│   │   ├── services/        # Business logic (mass_balance.py, mirror_analysis.py)
│   │   └── utils/           # Helpers (data_processing.py)
│   ├── requirements.txt     # Python deps (fastapi, sqlalchemy, numpy, etc.)
│   └── Dockerfile           # Backend container
├── frontend/                # React app
│   ├── src/
│   │   ├── components/      # Viz components (SankeyChart.js, ChoroplethMap.js)
│   │   ├── pages/           # Views (ProductionView.js, TradeView.js)
│   │   ├── services/        # API calls
│   │   └── App.js
│   ├── package.json         # Node deps (react, echarts, leaflet, etc.)
│   └── Dockerfile           # Frontend container
├── data/                    # DVC pipeline
│   ├── scripts/             # ETL scripts (fetch_comtrade.py, clean_data.py)
│   ├── dvc.yaml             # DVC pipeline config
│   └── .dvc/                # DVC metadata
├── database/                # DB migrations
│   ├── schema.sql           # Initial schema
│   └── migrations/          # Alembic scripts
├── .gitlab-ci.yml           # CI/CD pipeline
├── docker-compose.yml       # Local dev setup
└── docs/                    # This and other docs
```

## API Specifications (FastAPI)
- **Base URL**: `/api/v1`
- **Endpoints**:
  - `GET /production/{country}/{year}`: Retrieve production data with uncertainty bands.
  - `GET /trade/mirror/{country}`: Compare exporter/importer data; reconstruct if missing.
  - `POST /mass-balance/{country}`: Compute PU using P + I = E + PU + ΔS + L; return Sankey data.
  - `GET /maps/choropleth/{commodity}`: GeoJSON for choropleth maps.
- **Response Format**: JSON with data arrays, uncertainty fields (e.g., `{"value": 1000, "uncertainty": 0.1}`).
- **Auth**: None for MVP; add JWT later if needed.

## Database Setup
- **Engine**: PostgreSQL.
- **Schema Extensions**:
  - Add `quality_flag` (ENUM: 'Official', 'Estimated', 'Mirror-Derived') to `data_production`, `data_trade_flows`.
  - Add `uncertainty_factor` (DECIMAL) to model tables for confidence intervals.
- **Migration**: Use Alembic for schema updates.
- **Connection**: SQLAlchemy in FastAPI; environment vars for creds.

## Data Pipeline Guide (DVC)
- **Setup**: `dvc init`; configure S3 remote (`dvc remote add -d myremote s3://bucket/path`).
- **Pipeline**:
  - `fetch_comtrade.py`: Scrape UN Comtrade API weekly; output raw CSVs.
  - `clean_data.py`: Normalize units, apply grade conversions, flag inconsistencies.
  - `load_db.py`: Insert into DB tables.
- **Quality Checks**: In `clean_data.py`, validate HS codes, check mirrors (e.g., if exporter value > 1.2 * importer sum, flag).
- **Versioning**: `dvc add data/`; commit to Git.

## Frontend Components (React)
- **Structure**: Use React Router for views.
- **Viz Integrations**:
  - ECharts: For production charts and Sankeys (e.g., `echarts.init(dom).setOption(options)`).
  - D3: For custom flow maps if ECharts insufficient.
  - Leaflet: `react-leaflet` for choropleths (e.g., `MapContainer` with `GeoJSON` layers).
- **Uncertainty**: Add shaded regions in ECharts (e.g., `areaStyle` for bands).

## Deployment Guide
- **Docker**: Build images for backend/frontend; use `docker-compose` for local dev (app + DB).
- **GitLab CI/CD**: See `.gitlab-ci.yml` below.
- **Options**:
  - **Institutional Server**: Deploy via SSH; use Docker Compose on Linux VM.
  - **Cloud**: Hugging Face Spaces for demos; Render for full app (free tier).
- **Scaling**: Use Kubernetes if needed for large queries.

## Testing Strategy
- **Unit Tests**: Pytest for FastAPI (e.g., mass balance solver); Jest for React components.
- **Integration Tests**: Test API endpoints with DB fixtures.
- **Data Quality Tests**: In CI, run scripts to check inconsistencies (e.g., mirror discrepancies >10%).
- **Coverage**: Aim for 80%+; use `pytest-cov`.

## User Manual
- **Getting Started**: Clone repo; run `docker-compose up` for local dev.
- **Using the App**: Select country/year; view production trends with uncertainty; analyze trade mirrors; explore Sankey flows.
- **Interpreting Outputs**: Bands show data gaps; flags indicate quality.
- **Troubleshooting**: Check logs for API errors; re-run DVC if data stale.</content>
<parameter name="filePath">/home/kazi-nafiul-hassan/Hochschule Magdeburg-Stendal/RENO_TITAN_Project/reno-titan-intelligence-platform/implementation.md