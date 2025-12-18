# RENO-TITAN Intelligence Platform - AI Coding Guidelines

## Project Overview
This is a data visualization and analytics application for analyzing the global supply chain of critical minerals: Titanium, Zirconium, and Rare Earth Elements (REE). It aggregates data from sources like USGS, BGS, and UN Comtrade to visualize production trends, trade flows, and material balances.

Key features:
- Production series comparison across sources
- Trade mirror analysis to detect inconsistencies
- Geospatial visualizations (choropleths, flow maps)
- Material flow modeling with Sankey diagrams using mass balance equations

## Core Architecture
- **Data Ingestion**: Pull from external APIs/databases into structured tables
- **Database Schema**: Relational model with reference tables (commodities, HS codes) and data tables (production, trade flows, model params/results)
- **Visualization Layer**: Frontend components for charts/maps using ECharts/D3.js (Sankey/flow maps) and Leaflet.js (choropleths)
- **Analytics Engine**: Backend logic for mass balance calculations (Production + Imports = Exports + Processing Use + Stock Change + Losses)

## Tech Stack
- **Backend**: FastAPI for API endpoints and analytics
- **Frontend**: React for UI components
- **Visualization**: ECharts or D3.js for Sankey diagrams and flow maps; Leaflet.js for choropleth maps
- **Data Management**: DVC for versioning on S3
- **CI/CD**: GitLab CI for automated pipelines (e.g., weekly data fetch)
- **Deployment**: Docker containers; options include institutional servers or cloud (Hugging Face, Render)

## Key Files and References
- `description_of_the_application.md`: Functional requirements and module breakdown
- `database_schema_draft.md`: Table structures for commodities, HS codes, production/trade data, and model results
- `mass_balance_equation_requirements.md`: Detailed fields and logic for material flow calculations

## Domain-Specific Patterns
- **HS Codes**: Use specific Harmonized System codes for tracking (e.g., 261400 for Titanium ores, 282300 for oxides)
- **Units**: Prefer metric tons for weights, USD for values; normalize to equivalents (e.g., TiO2-equivalent) for comparisons
- **Mirror Analysis**: Always compare exporter-reported vs. importer-reported trade data to flag discrepancies
- **Mass Balance**: Implement equation P + I = E + PU + ΔS + L, solving for Processing Use (PU) as implied domestic capacity
- **Vietnam Focus**: Treat as primary case study; structure code to easily extend to other countries like Bangladesh

## Data Flows and Integration
- Ingest production data from USGS/BGS APIs or CSVs
- Trade data from UN Comtrade/WITS/BACI sources
- Processing params from USGS MIS for yield efficiencies and split ratios
- Output model results for Sankey diagrams showing ore-to-product conversions

## Development Conventions
- Use ISO country codes (e.g., 'VNM' for Vietnam) consistently
- Enum values for sources: 'USGS', 'BGS', 'NationalStats', 'WITS', 'Comtrade', 'BACI'
- Flow directions: 'Import', 'Export'
- Data quality: Include quality_flag ('Official', 'Estimated', 'Mirror-Derived') and uncertainty_factor in relevant tables
- Prioritize data quality checks: highlight top 10 producers, flag inconsistencies in notes fields

## Common Pitfalls
- Avoid assuming data consistency; always implement mirror checks
- Normalize grades before mass balance to account for ore quality variations
- Ensure Sankey diagrams balance (inputs = outputs) per mass conservation principles