# Part 1: Mass Balance Data Fields
The "Sankey Country Balance" equation is defined in the text as:

## Production + Imports = Exports + Processing Use + Assumed change of Stocks + Losses

To solve for Processing Use (the amount of feedstock actually processed domestically), we need the following specific data fields.

## 1. The "Supply" Side (Inputs)
### Domestic Mine Production ($P$)
- **Data Field:** production_volume_gross
- **Unit:** metric tons (gross weight)
- **Content:** Mine output for Titanium (ilmenite/rutile), Zirconium (zircon), or REE.
- **Source:** USGS Minerals Yearbook, USGS MCS, BGS World Mineral Statistics.

### Imports ($I$)
- **Data Field:** import_weight_gross
- **Unit:** metric tons.
- **Content:** Aggregated imports for relevant HS codes (e.g., 261400 for Ti ores).
- **Source:** UN Comtrade / WITS.

## 2. The "Demand" Side (Outputs)
### Export ($E$)
- **Data Field:** export_weight_gross
- **Unit:** metric tons.
- **Content:** Aggregated exports for relevant HS codes.
- **Source:** UN Comtrade / WITS.

### Stock change
- **Data Field:** stock_change_assumed
- **Unit:** metric tons.
- **Content:** Inventory build or draw. The text notes this is often an "assumed" variable or derived from "AStocks > 0".

### Losses ($L$)
- **Data Field:** processing_loss_factor
- **Unit:** Percentage (%) or scalar.
- **Content:** Material lost during transport or conversion.

## 3. The "Conversion" Fields (Normalization)
Since ores vary in grade, the text notes the need to convert to equivalents (e.g., "kt TiO2-equivalent").

### Export ($E$)
- **Data Field:** grade_conversion_factor
    - Example: %TiO2 in ilmenite vs. rutile
    - Purpose: To normalize P, I, and E into a standard unit before solving the equation.