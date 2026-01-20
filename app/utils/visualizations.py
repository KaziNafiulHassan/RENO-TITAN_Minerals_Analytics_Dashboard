"""
Visualization Utilities for RENO-TITAN
Functions for creating Plotly and Folium visualizations.
"""

import logging
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional, List

logger = logging.getLogger(__name__)

# ============================================================================
# PRODUCTION ANALYSIS VISUALIZATIONS
# ============================================================================

def plot_top_producers(df: pd.DataFrame, commodity: str, year: int) -> go.Figure:
    """
    Create bar chart of top producers.
    
    Args:
        df: DataFrame with columns ['Country', 'Production', 'Unit']
        commodity: Commodity name (for title)
        year: Year (for title)
    
    Returns:
        Plotly Figure object
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    fig = px.bar(
        df,
        x='Country',
        y='Production',
        title=f"Top 10 {commodity.title()} Producers - {year}",
        labels={'Production': 'Production (tonnes)'},
        color='Production',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        height=400,
        showlegend=False,
        hovermode='x unified'
    )
    
    return fig

def plot_production_trend(df: pd.DataFrame, commodity: str, countries: List[str] = None) -> go.Figure:
    """
    Create line chart of production trends over time.
    
    Args:
        df: DataFrame with columns ['year', 'country_iso3', 'quantity', 'data_source']
        commodity: Commodity name
        countries: List of countries to show (default: all)
    
    Returns:
        Plotly Figure object
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    # Filter by countries if specified
    if countries:
        df = df[df['country_iso3'].isin(countries)]
    
    fig = px.line(
        df,
        x='year',
        y='quantity',
        color='country_iso3',
        line_dash='data_source',
        title=f"{commodity.title()} Production Trends",
        labels={'quantity': 'Production (tonnes)', 'year': 'Year'}
    )
    
    fig.update_layout(
        height=500,
        hovermode='x unified',
        legend=dict(orientation="v", yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    return fig

def plot_comparison_bars(df: pd.DataFrame, commodity: str) -> go.Figure:
    """
    Create grouped bar chart comparing USGS vs BGS data.
    
    Args:
        df: Pivoted DataFrame with columns [year, USGS, BGS]
        commodity: Commodity name
    
    Returns:
        Plotly Figure object
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    fig = go.Figure()
    
    if 'USGS' in df.columns:
        fig.add_trace(go.Bar(
            x=df['year'],
            y=df['USGS'],
            name='USGS',
            marker_color='lightblue'
        ))
    
    if 'BGS' in df.columns:
        fig.add_trace(go.Bar(
            x=df['year'],
            y=df['BGS'],
            name='BGS',
            marker_color='darkblue'
        ))
    
    fig.update_layout(
        title=f"{commodity.title()} Production - USGS vs BGS",
        barmode='group',
        height=400,
        hovermode='x unified',
        yaxis_title='Production (tonnes)',
        xaxis_title='Year'
    )
    
    return fig

# ============================================================================
# TRADE ANALYSIS VISUALIZATIONS
# ============================================================================

def plot_top_routes(df: pd.DataFrame, limit: int = 10) -> go.Figure:
    """
    Create bar chart of top trade routes.
    
    Args:
        df: DataFrame with columns ['route', 'total_value_usd'] (or similar)
        limit: Number of top routes to show
    
    Returns:
        Plotly Figure object
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    df = df.head(limit)
    
    fig = px.bar(
        df,
        x='total_value_usd',
        y='route',
        orientation='h',
        title="Top Trade Routes by Value",
        labels={'total_value_usd': 'Trade Value (USD)'},
        color='total_value_usd',
        color_continuous_scale='Greens'
    )
    
    fig.update_layout(height=400, showlegend=False)
    
    return fig

def plot_unit_value_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Create box plot of unit value distribution by country.
    
    Args:
        df: DataFrame with columns ['country_iso3', 'unit_value']
    
    Returns:
        Plotly Figure object
    """
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available", showarrow=False)
        return fig
    
    fig = px.box(
        df,
        x='country_iso3',
        y='unit_value',
        title="Unit Value Distribution by Country",
        labels={'unit_value': 'Price per Tonne (USD)', 'country_iso3': 'Country'}
    )
    
    fig.update_layout(height=400, hovermode='x unified')
    
    return fig

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_large_number(num: float) -> str:
    """Format large numbers for display."""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return f"{num:.0f}"

# ============================================================================

if __name__ == "__main__":
    logger.info("Visualization utilities loaded successfully")
