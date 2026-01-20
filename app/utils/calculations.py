"""
Calculations Module for RENO-TITAN
Business logic functions for mass balance, discrepancies, and analytics.
"""

import logging
import numpy as np
import pandas as pd
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

# ============================================================================
# UNIT VALUE CALCULATIONS
# ============================================================================

def calculate_unit_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate unit values (price per tonne) from trade data.
    
    Args:
        df: Trade DataFrame with columns ['value_usd', 'quantity']
    
    Returns:
        DataFrame with unit_value column added
    """
    df = df.copy()
    
    # Filter out zero/negative quantities
    df = df[df['quantity'] > 0].copy()
    
    # Calculate unit value
    df['unit_value'] = df['value_usd'] / df['quantity']
    
    # Remove infinite and NaN values
    df = df[~(df['unit_value'].isin([np.inf, -np.inf]))].copy()
    df = df[df['unit_value'].notna()].copy()
    
    return df

def identify_outliers(series: pd.Series, threshold: float = 3.0) -> pd.Series:
    """
    Identify outliers using Z-score method.
    
    Args:
        series: Data series
        threshold: Z-score threshold (default: 3.0 for 3-sigma)
    
    Returns:
        Boolean Series (True = outlier)
    """
    mean = series.mean()
    std = series.std()
    
    if std == 0:
        return pd.Series([False] * len(series))
    
    z_scores = np.abs((series - mean) / std)
    return z_scores > threshold

# ============================================================================
# MIRROR ANALYSIS
# ============================================================================

def calculate_mirror_discrepancies(exports: pd.DataFrame, imports: pd.DataFrame) -> pd.DataFrame:
    """
    Compare exporter-reported vs importer-reported values.
    
    Args:
        exports: Export records with columns ['reporter', 'partner', 'year', 'value']
        imports: Import records with columns ['reporter', 'partner', 'year', 'value']
    
    Returns:
        DataFrame with discrepancy analysis
    """
    # Merge exports with corresponding imports
    merged = exports.merge(
        imports,
        how='outer',
        left_on=['reporter', 'partner', 'year'],
        right_on=['partner', 'reporter', 'year'],
        suffixes=('_export', '_import')
    )
    
    # Calculate discrepancy percentage
    merged['export_value'] = merged['value_export']
    merged['import_value'] = merged['value_import']
    
    # Handle cases where values might be missing
    merged['export_value'] = merged['export_value'].fillna(0)
    merged['import_value'] = merged['import_value'].fillna(0)
    
    # Calculate percentage difference
    merged['discrepancy_pct'] = np.where(
        merged['export_value'] != 0,
        np.abs(merged['export_value'] - merged['import_value']) / merged['export_value'] * 100,
        0
    )
    
    # Classify severity
    merged['severity'] = pd.cut(
        merged['discrepancy_pct'],
        bins=[0, 5, 10, float('inf')],
        labels=['LOW', 'MEDIUM', 'HIGH']
    )
    
    return merged

# ============================================================================
# MASS BALANCE CALCULATIONS
# ============================================================================

def calculate_mass_balance(
    production: float,
    imports: float,
    exports: float,
    processing_splits: Optional[dict] = None
) -> dict:
    """
    Calculate material balance: P + I = E + PU + ΔS + L
    
    Args:
        production: Domestic production
        imports: Total imports
        exports: Total exports
        processing_splits: Dict of output proportions {output: ratio}
    
    Returns:
        Dict with balance components
    """
    inputs = production + imports
    implied_processing_use = inputs - exports
    
    # If processing splits provided, calculate outputs
    outputs = {}
    if processing_splits:
        for output_material, split_ratio in processing_splits.items():
            outputs[output_material] = implied_processing_use * split_ratio
    
    return {
        'inputs': inputs,
        'production': production,
        'imports': imports,
        'exports': exports,
        'implied_processing_use': implied_processing_use,
        'outputs': outputs,
        'balance': inputs - (exports + implied_processing_use)  # Should be ~0
    }

# ============================================================================
# DATA QUALITY METRICS
# ============================================================================

def calculate_discrepancy_percentage(value1: float, value2: float) -> float:
    """
    Calculate percentage discrepancy between two values.
    
    Args:
        value1: First value
        value2: Second value
    
    Returns:
        Discrepancy percentage
    """
    if value1 == 0 and value2 == 0:
        return 0.0
    elif value1 == 0:
        return 100.0
    
    return np.abs(value1 - value2) / value1 * 100

def flag_data_quality_issues(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flag potential data quality issues.
    
    Args:
        df: Data frame with production or trade data
    
    Returns:
        DataFrame with quality_issue column
    """
    df = df.copy()
    issues = []
    
    # Check for zero values
    if 'quantity' in df.columns:
        issues.append(df['quantity'] <= 0)
    
    # Check for missing values
    issues.append(df.isnull().any(axis=1))
    
    # Check for outliers
    if 'quantity' in df.columns and len(df) > 10:
        outliers = identify_outliers(df['quantity'])
        issues.append(outliers)
    
    # Combine issues
    if issues:
        df['quality_issue'] = pd.concat(issues, axis=1).any(axis=1)
    else:
        df['quality_issue'] = False
    
    return df

# ============================================================================

if __name__ == "__main__":
    logger.info("Calculations module loaded successfully")
