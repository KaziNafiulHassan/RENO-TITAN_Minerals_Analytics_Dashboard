# Planning Document for RENO-TITAN Intelligence Platform

## Executive Summary
The RENO-TITAN Intelligence Platform is a data visualization and analytics application for analyzing the global supply chain of critical minerals: Titanium, Zirconium, and Rare Earth Elements (REE). Building on existing conceptual drafts, this plan outlines the transition to a full-stack implementation using FastAPI (backend), React (frontend), ECharts/D3 and Leaflet (visualizations), GitLab CI/CD, DVC on S3, and Docker deployment. The project aims to aggregate data from USGS, BGS, and UN Comtrade to enable production comparisons, trade mirror analysis, geospatial maps, and Sankey-based material flow modeling. Key enhancements include automated data ingestion, quality checks for inconsistencies, uncertainty quantification, and scalable deployment for research use.

## Requirements Analysis
### Functional Modules
- **Production Series Analysis**: Compare mining output by country over time, highlighting top 10 producers. Overlay data from USGS, BGS, and national stats.
- **Trade Series & Quality Control**: Track HS codes (e.g., 261400 for Titanium ores), perform mirror analysis (exporter vs. importer discrepancies), visualize top routes, and estimate unit values.
- **Geospatial Visualization**: Choropleth maps for production/trade intensity, flow maps for material movement.
- **Material Flow Analysis**: Sankey diagrams for mass balance (P + I = E + PU + ΔS + L), solving for Processing Use (PU) to estimate domestic capacity.
- **Vietnam Focus**: Case study for local mining data reconciliation, extensible to other countries like Bangladesh.

### Data Sources and Flows
- **Sources**: USGS (production/reserves), BGS (world stats), UN Comtrade/WITS/BACI (trade), USGS MIS (processing params).
- **Flows**: Ingest via APIs/CSVs → DVC pipeline (cleaning, normalization) → Load into relational DB → FastAPI processing (analytics, models) → React frontend (visualizations).
- **Quality & Uncertainty**: Add quality_flag (e.g., "Official", "Estimated", "Mirror-Derived") and uncertainty_factor fields. Implement mirror reconstruction for missing exports. Visualize uncertainty bands in charts.

### Non-Functional Requirements
- **Scalability**: Handle large trade datasets (e.g., UN Comtrade) with efficient queries and caching.
- **Security**: Secure S3 for DVC data; on-prem deployment for sensitive research data.
- **Usability**: Interactive web UI for scientists/planners; low-maintenance deployment.
- **Automation**: Weekly data fetch via GitLab CI; DVC versioning for reproducibility.

## Architecture Overview
### High-Level Components
- **Data Layer**: Relational DB (PostgreSQL) with schema tables (ref_commodities, data_production, etc.). DVC manages data pipelines and versioning on S3.
- **Backend Layer**: FastAPI for API endpoints (data queries, mass balance computations, model runs).
- **Frontend Layer**: React app with components for dashboards, charts, and maps.
- **Visualization Layer**: ECharts/D3 for Sankey/flow charts, Leaflet for choropleths.
- **DevOps Layer**: GitLab CI/CD for pipelines (build, test, deploy); Docker for containerization.

### Data Flows
1. External data → DVC ETL (scrape/clean/normalize) → DB.
2. User requests → React → FastAPI API → DB queries/models → Render in viz libs.
3. CI triggers weekly fetch; tests validate inconsistencies.

### Integration Points
- DVC with FastAPI for data access; GitLab CI with S3 for secure runner access.
- Uncertainty: Probabilistic fields in DB, Monte Carlo in backend, error bands in frontend.

## Tech Stack Justification
- **FastAPI**: Python-based for seamless integration with analytics (e.g., NumPy/SciPy for mass balance). Async support for large data; auto-generated docs.
- **React**: Component-based for modular UI (e.g., separate views for production/trade/maps). Ecosystem fits viz libs.
- **ECharts/D3 + Leaflet**: ECharts for quick choropleths/Sankeys; D3 for custom flows. Leaflet for geospatial accuracy.
- **GitLab CI/CD**: Native to repo; supports scheduled jobs (weekly fetch) and multi-stage pipelines.
- **DVC on S3**: Versioning for data reproducibility; cloud storage for scalability.
- **Docker**: Ensures consistent environments; enables easy deployment on institutional servers or cloud.

## Risk Assessment
- **Data Volume/Scalability**: Mitigate with DB indexing, caching, and batch processing in DVC.
- **Uncertainty Complexity**: Start with simple error bands; iterate based on user feedback.
- **Integration Overhead**: Use modular design; test pipelines early.
- **Data Quality Issues**: Automate checks; provide manual override for expert validation.
- **Deployment Security**: Prioritize on-prem; encrypt S3 access.
- **Domain Expertise**: Collaborate with geologists for HS codes/grades.

## Roadmap
### Phase 1: Foundation (1-2 months)
- Set up DB schema with uncertainty fields.
- Implement DVC pipeline for sample data ingestion.
- Build FastAPI skeleton with basic endpoints.

### Phase 2: Core Features (2-3 months)
- Develop React frontend with viz components.
- Integrate mass balance logic and mirror checks.
- Add GitLab CI for data fetch and tests.

### Phase 3: Enhancement & Deployment (1-2 months)
- Implement uncertainty visualizations.
- Containerize and deploy (e.g., institutional server).
- User testing and documentation.

### Phase 4: Extension (Ongoing)
- Add more countries/sources; optimize performance.</content>
<parameter name="filePath">/home/kazi-nafiul-hassan/Hochschule Magdeburg-Stendal/RENO_TITAN_Project/reno-titan-intelligence-platform/planning.md