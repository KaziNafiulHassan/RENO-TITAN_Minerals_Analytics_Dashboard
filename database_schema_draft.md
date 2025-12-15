# Database Schema Draft
This schema is designed to house the multi-source data (USGS vs. BGS) and the trade flows (HS-6) identified in the document.

## Table 1: `ref_commodities`
Defines the material hierarchy (Ore \to Product).

* `id` (PK)
* `name` (e.g., Titanium, Zirconium, REE)
* `type` (Enum: Raw Material, Intermediate, Final Product)

## Table 2: `ref_codes_hs`
Stores the specific HS codes monitored by the app.

* `code` (PK) (e.g., '261400', '282300')
* `commodity_id` (FK)
* `description` (e.g., "Titanium ores and concentrates")
* `category` (e.g., Mineral/Concentrate, Product)

## Table 3: `data_production`
Stores comparative production series from different authorities.

* `id` (PK)
* `country_iso` (e.g., VNM, CHN)
* `year` (Int)
* `commodity_id` (FK)
* `source_authority` (Enum: 'USGS', 'BGS', 'NationalStats')
* `value_tons` (Decimal)
* 
`notes` (Text) (e.g., "inconsistencies in reported data" )

## Table 4: `data_trade_flows`
Stores bilateral trade data for "Mirror View" and "Top Routes" analysis.

* `id` (PK)
* `year` (Int)
* `reporter_iso` (Country reporting)
* `partner_iso` (Partner country)
* `flow_direction` (Enum: Import, Export)
* `hs_code` (FK)
* `trade_value_usd` (Decimal)
* `net_weight_kg` (Decimal)
* `quantity_unit` (String)
* `source_db` (Enum: 'WITS', 'Comtrade', 'BACI')

## Table 5: `model_processing_params`
Stores the assumptions needed for the Mass Balance calculation.

* `id` (PK)
* `country_iso` (FK)
* `commodity_id` (FK)
* `yield_efficiency` (Decimal) (Output/Input ratio)
* `assumed_loss_rate` (Decimal)
* `pigment_split_ratio` (Decimal) (Portion of ore going to Pigment) 
* `metal_split_ratio` (Decimal) (Portion of ore going to Metal) 



####Table 6: `model_results_material_flow`Stores the calculated outputs for the Sankey diagrams.

* `id` (PK)
* `country_iso` (FK)
* `year` (Int)
* `calculated_processing_use` (Decimal) (The result of P+I-E)
* `calculated_stock_change` (Decimal)
* 
`implied_processing_capacity` (Decimal) 
