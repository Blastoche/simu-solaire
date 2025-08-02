# -*- coding: utf-8 -*-
"""
Calculs de dégradation et rendement à long terme
"""
import pandas as pd
import numpy as np

def calculate_yearly_degradation(
    initial_yield: float,
    years: int = 25,
    degradation_rate: float = 0.005
) -> pd.Series:
    """
    Calcule la production annuelle avec dégradation.
    
    Args:
        initial_yield: Production première année (kWh)
        degradation_rate: % de perte annuelle (ex: 0.005 = 0.5%)
    
    Returns:
        Série pandas avec production par année
    """
    return pd.Series([
        initial_yield * (1 - degradation_rate) ** year
        for year in range(years)
    ])

def calculate_performance_ratio(
    actual_yield: float,
    expected_yield: float,
    losses: dict = None
) -> float:
    """
    Calcule le Performance Ratio (PR).
    
    Args:
        losses: {
            'soiling': float,  # Pertes par salissure
            'inverter': float  # Pertes onduleur
        }
    """
    if losses:
        effective_losses = 1 - sum(losses.values())
    else:
        effective_losses = 1.0
    
    return (actual_yield / expected_yield) * effective_losses
