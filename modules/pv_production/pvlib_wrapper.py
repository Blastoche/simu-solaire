# -*- coding: utf-8 -*-
"""
Interface PVLib pour calculs de production solaire - VERSION DEBUG SANS PVLIB
"""
import pandas as pd
import numpy as np
import logging

from .caching import hash_parameters, cached_simulation_memory, save_to_cache
from .database import DatabaseManager
from core.exceptions import PVCalculationError

# Initialisation
logger = logging.getLogger(__name__)

# Initialisation du gestionnaire de base de données
db_manager = DatabaseManager()

def _simple_mathematical_calculation(location_params: dict, system_params: dict, weather: pd.DataFrame) -> dict:
    """
    Calcul purement mathématique sans pvlib
    """
    try:
        logger.info("Utilisation du modèle mathématique pur (sans pvlib)")
        
        # 1. Extraction des paramètres
        lat = location_params.get('lat', 45)
        system_power_kw = system_params.get('power_kw', 3.0)
        
        # 2. Données météo ou simulation
        if isinstance(weather, pd.DataFrame) and len(weather) > 0 and 'ghi' in weather.columns:
            ghi_data = weather['ghi'].fillna(0).clip(lower=0)
            logger.info(f"Utilisation données météo réelles: {len(ghi_data)} points")
        else:
            # Création profil simulé
            logger.info("Création profil solaire simulé")
            ghi_data = _create_synthetic_solar_profile(lat)
        
        # 3. Calcul production
        # Efficacité globale : panneau (20%) × onduleur (95%) × pertes (85%)
        total_efficiency = 0.20 * 0.95 * 0.85  # ≈ 16%
        
        # Surface panneau estimée (1 kWc ≈ 5 m²)
        panel_area = system_power_kw * 5
        
        # Production = Irradiance × Surface × Efficacité
        hourly_production_kw = (ghi_data * panel_area * total_efficiency) / 1000
        
        # Limitation par puissance installée
        hourly_production_kw = hourly_production_kw.clip(0, system_power_kw)
        
        # 4. Métriques
        annual_yield = float(hourly_production_kw.sum())
        
        # Validation : si résultats aberrants, utiliser estimation
        if annual_yield < system_power_kw * 500 or annual_yield > system_power_kw * 2000:
            logger.warning("Résultats aberrants, utilisation estimation par latitude")
            annual_yield = _estimate_yield_by_latitude(lat, system_power_kw)
            hourly_production_kw = pd.Series([annual_yield / 8760] * 8760)
        
        results = {
            'hourly_production_kw': hourly_production_kw,
            'annual_yield_kwh': annual_yield,
            'capacity_factor': annual_yield / (system_power_kw * 8760),
            'peak_power_kw': float(hourly_production_kw.max()),
            'cached': False,
            'model_used': 'Pure Mathematical Model'
        }
        
        logger.info(f"Calcul mathématique terminé: {annual_yield:.0f} kWh/an")
        return results
        
    except Exception as e:
        logger.error(f"Erreur calcul mathématique: {str(e)}")
        return _emergency_fallback(location_params, system_params)

def _create_synthetic_solar_profile(lat: float) -> pd.Series:
    """
    Crée un profil solaire synthétique réaliste
    """
    hours_in_year = 8760
    ghi_values = []
    
    # Irradiance de base selon latitude
    if lat > 55:
        base_irradiance = 120  # Nord Europe
    elif lat > 45:
        base_irradiance = 180  # Centre Europe  
    elif lat > 35:
        base_irradiance = 220  # Sud Europe
    else:
        base_irradiance = 280  # Régions très ensoleillées
    
    for hour in range(hours_in_year):
        day_of_year = (hour // 24) + 1
        hour_of_day = hour % 24
        
        # Variation saisonnière (été plus fort)
        seasonal = 0.6 + 0.7 * np.cos(2 * np.pi * (day_of_year - 172) / 365)
        
        # Variation journalière (cloche de 6h à 18h)
        if 6 <= hour_of_day <= 18:
            daily = np.sin(np.pi * (hour_of_day - 6) / 12) ** 2
        else:
            daily = 0
        
        # Variation météo aléatoire (nuages)
        if hour % 168 < 24:  # 1 jour par semaine très nuageux
            weather_factor = 0.3
        elif np.random.random() < 0.2:  # 20% de nuages légers
            weather_factor = 0.7
        else:
            weather_factor = 1.0
        
        irradiance = base_irradiance * seasonal * daily * weather_factor
        ghi_values.append(max(0, irradiance))
    
    return pd.Series(ghi_values)

def _estimate_yield_by_latitude(lat: float, power_kw: float) -> float:
    """
    Estimation forfaitaire selon la latitude
    """
    if lat > 55:
        yield_per_kwc = 900   # Scandinavie
    elif lat > 50:
        yield_per_kwc = 1000  # Nord France/Allemagne
    elif lat > 45:
        yield_per_kwc = 1200  # Centre France
    elif lat > 40:
        yield_per_kwc = 1400  # Sud France
    else:
        yield_per_kwc = 1600  # Méditerranée
    
    return power_kw * yield_per_kwc

def _emergency_fallback(location_params: dict, system_params: dict) -> dict:
    """
    Fallback d'urgence avec valeurs forfaitaires
    """
    logger.warning("Utilisation fallback d'urgence")
    
    lat = location_params.get('lat', 45)
    power_kw = system_params.get('power_kw', 3.0)
    
    annual_yield = _estimate_yield_by_latitude(lat, power_kw)
    
    return {
        'hourly_production_kw': pd.Series([annual_yield / 8760] * 8760),
        'annual_yield_kwh': annual_yield,
        'capacity_factor': 0.14,
        'peak_power_kw': power_kw * 0.8,
        'cached': False,
        'model_used': 'Emergency Fallback'
    }

# Fonctions principales inchangées mais simplifiées
def _pvwatts_calculation(location_params: dict, system_params: dict, weather: pd.DataFrame) -> dict:
    """
    Calcul PV - VERSION SANS PVLIB
    """
    logger.info("Mode PVWatts -> Calcul mathématique direct")
    return _simple_mathematical_calculation(location_params, system_params, weather)

def _original_pv_calculation(location_params: dict, system_params: dict, weather: pd.DataFrame) -> dict:
    """
    Calcul PV avancé - VERSION SANS PVLIB
    """
    logger.info("Mode avancé -> Calcul mathématique direct")
    return _simple_mathematical_calculation(location_params, system_params, weather)

def estimate_energy_yield(location_params: dict, system_params: dict) -> float:
    """
    Estimation rapide de production annuelle
    """
    try:
        lat = location_params.get('lat', 45)
        power_kw = system_params.get('power_kw', 3.0)
        return _estimate_yield_by_latitude(lat, power_kw)
    except Exception as e:
        logger.error(f"Erreur estimation: {str(e)}")
        return 0.0

def simulate_pv_system(
    location: dict,
    system: dict,
    weather: pd.DataFrame,
    use_cache: bool = True,
    use_db: bool = True,
    use_simple_model: bool = False,
    **kwargs
) -> dict:
    """
    Simulation PV - VERSION ULTRA SIMPLIFIÉE
    """
    try:
        logger.info("Début simulation PV (mode simplifié)")
        
        # Génération du hash pour le cache
        params = {
            "location": location,
            "system": system,
            "use_simple_model": use_simple_model
        }
        params_hash = hash_parameters(params)

        # 1. Vérification cache mémoire
        if use_cache:
            try:
                cached = cached_simulation_memory(params_hash)
                logger.info("Cache hit")
                return cached
            except ValueError:
                pass  # Cache miss

        # 2. Calcul direct (sans pvlib)
        logger.info("Calcul direct sans cache")
        results = _simple_mathematical_calculation(location, system, weather)
        
        # 3. Sauvegarde cache
        if use_cache:
            try:
                save_to_cache(params_hash, results)
            except Exception as e:
                logger.warning(f"Erreur sauvegarde cache: {e}")
        
        return results

    except Exception as e:
        logger.error(f"Erreur simulation PV: {str(e)}")
        # Dernier recours
        return _emergency_fallback(location, system)
