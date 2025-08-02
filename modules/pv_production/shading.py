# -*- coding: utf-8 -*-
"""
Gestion des pertes par masques solaires (ombrages) - VERSION CORRIGÉE
"""
import pandas as pd
import numpy as np
from pvlib import shading

def calculate_shading_losses(
    tilt: float,
    azimuth: float,
    shading_angles: dict,
    dni: pd.Series
) -> pd.Series:
    """
    Calcule les pertes dues aux ombrages.
    
    Args:
        tilt: Inclinaison des panneaux (degrés)
        azimuth: Orientation des panneaux (degrés)
        shading_angles: {
            'elevation': float,  # Angle en degrés
            'azimuth': float     # Orientation de l'obstacle
        }
        dni: Série de l'irradiation directe normale
    
    Returns:
        Série des pertes d'irradiation dues à l'ombrage
    """
    try:
        # Calcul de l'angle de masque avec pvlib
        mask_angle = shading.masking_angle(
            surface_tilt=tilt,
            surface_azimuth=azimuth,
            shading_elevation=shading_angles['elevation'],
            shading_azimuth=shading_angles['azimuth']
        )
        
        # Simplification : perte linéaire quand le soleil est sous l'angle
        shading_factor = np.clip(mask_angle / 90, 0, 1)
        return dni * shading_factor
        
    except Exception as e:
        # Fallback en cas d'erreur
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Erreur calcul ombrage, utilisation méthode simplifiée: {e}")
        
        # Méthode simplifiée
        shading_loss_factor = 0.1  # 10% de perte par défaut
        return dni * shading_loss_factor

def apply_shading_correction(
    production: pd.Series,
    shading_losses: pd.Series
) -> pd.Series:
    """
    Applique la correction d'ombrage à la production
    
    Args:
        production: Série de production PV (kW)
        shading_losses: Série de pertes d'ombrage (W/m²)
    
    Returns:
        Production corrigée de l'ombrage
    """
    # Conversion W/m² -> kW avec facteur de surface approximatif
    # Estimation : 1 kWc ≈ 6 m² de panneaux
    surface_factor = 6  # m²/kWc
    shading_losses_kw = shading_losses / 1000 * surface_factor
    
    # Application de la correction (soustraction des pertes)
    corrected_production = production - shading_losses_kw
    
    # S'assurer que la production reste positive
    return corrected_production.clip(lower=0)

def calculate_horizon_shading(
    solar_elevation: pd.Series,
    solar_azimuth: pd.Series,
    horizon_profile: dict = None
) -> pd.Series:
    """
    Calcule l'ombrage dû au profil d'horizon
    
    Args:
        solar_elevation: Élévation solaire (degrés)
        solar_azimuth: Azimut solaire (degrés)
        horizon_profile: Dictionnaire {azimut: élévation_horizon}
    
    Returns:
        Facteur de réduction dû à l'horizon (0-1)
    """
    if horizon_profile is None:
        # Pas d'ombrage d'horizon
        return pd.Series(1.0, index=solar_elevation.index)
    
    shading_factor = pd.Series(1.0, index=solar_elevation.index)
    
    for idx in solar_elevation.index:
        sun_az = solar_azimuth.loc[idx]
        sun_el = solar_elevation.loc[idx]
        
        if sun_el <= 0:
            shading_factor.loc[idx] = 0  # Soleil sous l'horizon
            continue
        
        # Trouve l'élévation d'horizon la plus proche de l'azimut solaire
        closest_horizon_az = min(horizon_profile.keys(), 
                                key=lambda x: abs(x - sun_az))
        horizon_elevation = horizon_profile[closest_horizon_az]
        
        # Si le soleil est sous l'horizon local, ombrage total
        if sun_el < horizon_elevation:
            shading_factor.loc[idx] = 0
    
    return shading_factor
