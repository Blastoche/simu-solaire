# -*- coding: utf-8 -*-
"""
Interface PV Production - VERSION MINIMAL SANS PVLIB
"""
import pandas as pd
import numpy as np
import logging

# Imports locaux sans pvlib
from .caching import hash_parameters, cached_simulation_memory, save_to_cache
from .database import DatabaseManager
from core.exceptions import PVCalculationError

logger = logging.getLogger(__name__)

# Initialisation DB
try:
    db_manager = DatabaseManager()
except Exception as e:
    logger.warning(f"DB Manager init failed: {e}")
    db_manager = None

def simulate_pv_system(
    location: dict,
    system: dict,
    weather: pd.DataFrame,
    use_cache: bool = True,
    use_db: bool = True,
    use_simple_model: bool = True,  # Forcé à True
    **kwargs
) -> dict:
    """
    Simulation PV - VERSION ULTRA SIMPLIFIÉE SANS PVLIB
    """
    try:
        logger.info("Début simulation PV (mode ultra-simplifié)")
        
        # Paramètres
        lat = location.get('lat', 45)
        lon = location.get('lon', 2)
        power_kw = system.get('power_kw', 3.0)
        
        # Données météo ou simulation
        if isinstance(weather, pd.DataFrame) and len(weather) > 0 and 'ghi' in weather.columns:
            ghi_data = weather['ghi'].fillna(0).clip(lower=0)
            logger.info(f"Données météo: {len(ghi_data)} points")
        else:
            logger.info("Création profil solaire synthétique")
            ghi_data = create_solar_profile(lat)
        
        # Calcul production
        hourly_production = calculate_pv_production(ghi_data, power_kw, lat)
        
        # Métriques
        annual_yield = float(hourly_production.sum())
        capacity_factor = annual_yield / (power_kw * 8760) if power_kw > 0 else 0
        
        results = {
            'hourly_production_kw': hourly_production,
            'annual_yield_kwh': annual_yield,
            'capacity_factor': capacity_factor,
            'peak_power_kw': float(hourly_production.max()),
            'cached': False,
            'model_used': 'Mathematical Model (No PVLib)'
        }
        
        logger.info(f"Production calculée: {annual_yield:.0f} kWh/an")
        return results
        
    except Exception as e:
        logger.error(f"Erreur simulation: {str(e)}")
        # Fallback d'urgence
        return emergency_fallback(location, system)

def create_solar_profile(lat: float, hours: int = 8760) -> pd.Series:
    """
    Crée un profil solaire synthétique
    """
    # Irradiance de base selon latitude
    base_irradiance = max(50, 300 - abs(lat - 35) * 4)
    
    ghi_values = []
    for hour in range(hours):
        day_of_year = (hour // 24) + 1
        hour_of_day = hour % 24
        
        # Variation saisonnière
        seasonal = 0.7 + 0.6 * np.cos(2 * np.pi * (day_of_year - 172) / 365)
        
        # Variation journalière
        if 6 <= hour_of_day <= 18:
            daily = np.sin(np.pi * (hour_of_day - 6) / 12) ** 1.5
        else:
            daily = 0
        
        # Facteur météo aléatoire
        weather_factor = 0.4 + 0.6 * np.random.random()
        
        irradiance = base_irradiance * seasonal * daily * weather_factor
        ghi_values.append(max(0, irradiance))
    
    return pd.Series(ghi_values)

def calculate_pv_production(ghi: pd.Series, power_kw: float, lat: float) -> pd.Series:
    """
    Calcule la production PV à partir de l'irradiance
    """
    # Efficacité système globale
    module_eff = 0.20      # Efficacité modules 20%
    inverter_eff = 0.95    # Efficacité onduleur 95%  
    system_eff = 0.85      # Pertes système 15%
    total_eff = module_eff * inverter_eff * system_eff
    
    # Surface de panneaux (approximation)
    panel_area = power_kw * 5  # 5 m²/kWc
    
    # Production = Irradiance × Surface × Efficacité
    production = (ghi * panel_area * total_eff) / 1000
    
    # Limitation par puissance installée
    return production.clip(0, power_kw)

def emergency_fallback(location: dict, system: dict) -> dict:
    """
    Fallback d'urgence avec valeurs forfaitaires
    """
    logger.warning("Utilisation valeurs forfaitaires")
    
    lat = location.get('lat', 45)
    power_kw = system.get('power_kw', 3.0)
    
    # Production selon latitude
    if lat > 50:
        yield_per_kwc = 1000
    elif lat > 45:
        yield_per_kwc = 1200
    else:
        yield_per_kwc = 1400
    
    annual_yield = power_kw * yield_per_kwc
    
    return {
        'hourly_production_kw': pd.Series([annual_yield / 8760] * 8760),
        'annual_yield_kwh': annual_yield,
        'capacity_factor': 0.14,
        'peak_power_kw': power_kw * 0.8,
        'cached': False,
        'model_used': 'Emergency Default'
    }

def estimate_energy_yield(location_params: dict, system_params: dict) -> float:
    """
    Estimation rapide de production
    """
    try:
        lat = location_params.get('lat', 45)
        power_kw = system_params.get('power_kw', 3.0)
        
        if lat > 50:
            return power_kw * 1000
        elif lat > 45:
            return power_kw * 1200
        else:
            return power_kw * 1400
    except:
        return 0.0
