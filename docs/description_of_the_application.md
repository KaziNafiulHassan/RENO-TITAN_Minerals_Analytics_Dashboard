# Executive Summary
The document outlines the functional requirements for a data visualization and analytics application designed to assist **scientists and planners**. The app’s primary goal is to analyze the global supply chain—from mine production to trade and processing—of three specific critical mineral groups: **Titanium, Zirconium, and Rare Earth Elements (REE)**.

The application aims to aggregate data from major statistical bodies (USGS, BGS, UN Comtrade) to visualize production trends, identify trade inconsistencies, and model material flows.

# Core Functional Modules
The application is divided into four main functional areas:

## 1. Production Series Analysis
**Goal:** Compare mining output over time by country.
 
**Data Sources:** The app must overlay data from different authorities to show discrepancies, specifically **USGS** (United States Geological Survey), **BGS** (British Geological Survey), and optional national statistics.
 
**Key Feature:** It should automatically highlight the "10 biggest producers" for a selected time frame.


## 2. Trade Series & Quality Control
**HS Code Tracking:** The app monitors specific Harmonized System (HS-6) codes for ores and downstream products (e.g., HS 261400 for Titanium ores, HS 282300 for Titanium oxides).
 
**Mirror Data Analysis:** A critical feature is the "Mirror View," which compares **Exporter-Reported** figures against **Partner-Reported Imports**.

* *Why this matters:* It identifies data inconsistencies. For example, if Vietnam reports exporting $1M to China, but China reports importing 0.8M tons, the app flags this discrepancy.
 
**Route Analysis:** Visualization of "Top Routes" by value (e.g., China \to Germany).

**Unit Values:** Estimation of prices for ores and concentrates based on trade values.

## 3. Geospatial Visualization (Maps)
**Choropleths:** Maps indicating production intensity and trade intensity by country.

**Flow Maps:** Origin \to Destination flow maps to visualize the movement of materials globally.

## 4. Material Flow Analysis (Sankey Diagrams)
This is the most advanced analytical feature, likely used for "industrial ecology" studies. It uses **Sankey diagrams** to model how raw ores are converted into final products.

* **Mass Balance Equation:** The app must calculate processing splits using the following logic:
 
**Processing Splits:** Breakdowns of how ores are used (e.g., Titanium ore splitting into \text{TiO}_2 pigment vs. Ti metal).

**Visualization:** "Country Balance" views to quantify domestic processing capacity.

---

## Target Commodities & Data Architecture
The application focuses on a specific set of materials and relies on open-source intelligence.

## Key Materials & Codes
The document explicitly lists the following HS codes for tracking:

* **Titanium:** Ores (261400), Oxides (282300), Unwrought/Scrap (810810, 810890).
* **Zirconium:** Ores (261510), Oxides (282560), Unwrought (810910).
* **Rare Earths (REE):** Compounds (284610, 284690), Metals (280530).

## Data Sources identified
| Data Type | Source | Purpose |
| --- | --- | --- |
| **Production** | USGS (Mineral Commodity Summaries), BGS, National Stats | Annual mine production & reserves.
| **Trade** | WITS (UN Comtrade), CEPII BACI, Eurostat | Bilateral trade flows and "cleaned" mirror data.
| **Processing** | USGS MIS (Mineral Industry Surveys) | Context on pigment/sponge capacity to calibrate mass balance models.

## Special Focus: Vietnam Data Hub
The document includes a specific module for Vietnam, which serves as a case study or "template" that could later be applied to other countries like Bangladesh. This involves compiling specific local mining data and reconciling it with the global trade models.

---

## Summary of User Experience
The user (a scientist or planner) would log in to:
- Check Production trends to see who is mining the most Zircon or Titanium.
- Switch to Trade view to see where that ore is going and if the trade data is reliable (Mirror check).
- Use the Material Flow tool to estimate how much of that ore is actually being processed into metal or chemicals within a specific country versus being exported raw.

---

## Special Focus: Vietnam Data Hub
The document includes a specific module for **Vietnam**, which serves as a case study or "template" that could later be applied to other countries like Bangladesh. This involves compiling specific local mining data and reconciling it with the global trade models.