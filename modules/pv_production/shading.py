# -*- coding: utf-8 -*-
"""
Gestion des pertes par masques solaires (ombrages)
"""
import numpy as np
from pvlib.shading import masking_angle

def calculate_shading_losses(
    tilt: float,
    azimuth: float,
    shading_angles: dict,
    dni: pd.Series
) -> pd.Series:
    """
    Calcule les pertes dues aux ombrages.
    
    Args:
        shading_angles: {
            'elevation': float,  # Angle en degrés
            'azimuth': float     # Orientation de l'obstacle
        }
    """
    mask_angle = masking_angle(
        tilt=tilt,
        azimuth=azimuth,
        shading_elevation=shading_angles['elevation'],
        shading_azimuth=shading_angles['azimuth']
    )
    
    # Simplification : perte linéaire quand le soleil est sous l'angle
    shading_factor = np.clip(mask_angle / 90, 0, 1)
    return dni * shading_factor

def apply_shading_correction(
    production: pd.Series,
    shading_losses: pd.Series
) -> pd.Series:
    """Applique la correction d'ombrage à la production"""
    return production - (shading_losses / 1000)  # Conversion W -> kW
