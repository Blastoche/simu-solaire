# -*- coding: utf-8 -*-
"""
Modélisation détaillée des appareils électriques
"""
import numpy as np
import pandas as pd
import json
from pathlib import Path
from typing import List, Dict
import logging

from config.appliances import APPLIANCES

logger = logging.getLogger(__name__)

# Chargement des coefficients DPE
DPE_FILE = Path("assets/dpe_coefficients.json")
try:
    with open(DPE_FILE, 'r', encoding='utf-8') as f:
        DPE_COEFFICIENTS = json.load(f)
except FileNotFoundError:
    logger.warning("Fichier DPE non trouvé, utilisation valeurs par défaut")
    DPE_COEFFICIENTS = {
        "A": {"coeff": 20}, "B": {"coeff": 25}, "C": {"coeff": 35},
        "D": {"coeff": 50}, "E": {"coeff": 70}, "F": {"coeff": 90}, "G": {"coeff": 120}
    }

def simulate(appliances: List[Dict], dpe: str, occupants: int, surface: float = 100) -> Dict:
    """
    Simule la consommation électrique annuelle
    
    Args:
        appliances: Liste des appareils sélectionnés
        dpe: Classe énergétique du logement (A-G)
        occupants: Nombre d'occupants
        surface: Surface du logement en m²
    
    Returns:
        Dict avec consommation horaire et annuelle
    """
    try:
        # 1. Calcul de la consommation de base (chauffage, éclairage, etc.)
        base_consumption = _calculate_base_consumption(dpe, occupants, surface)
        
        # 2. Calcul de la consommation des appareils
        appliances_consumption = _calculate_appliances_consumption(appliances, occupants)
        
        # 3. Combinaison et lissage
        total_consumption = base_consumption + appliances_consumption
        
        # 4. Application de variations réalistes
        final_consumption = _apply_consumption_patterns(total_consumption, occupants)
        
        results = {
            'consumption_kw': final_consumption,
            'annual_consumption_kwh': float(final_consumption.sum()),
            'base_consumption_kwh': float(base_consumption.sum()),
            'appliances_consumption_kwh': float(appliances_consumption.sum()),
            'peak_consumption_kw': float(final_consumption.max()),
            'average_consumption_kw': float(final_consumption.mean())
        }
        
        logger.info(f"Consommation simulée: {results['annual_consumption_kwh']:.0f} kWh/an")
        return results
        
    except Exception as e:
        logger.error(f"Erreur simulation consommation: {str(e)}")
        raise

def _calculate_base_consumption(dpe: str, occupants: int, surface: float) -> pd.Series:
    """
    Calcule la consommation de base (chauffage, éclairage, ventilation)
    basée sur le DPE et les caractéristiques du logement
    """
    # Coefficient DPE en kWh/m²/an
    dpe_coeff = DPE_COEFFICIENTS.get(dpe, DPE_COEFFICIENTS["D"])["coeff"]
    
    # Consommation annuelle de base
    annual_base_kwh = dpe_coeff * surface
    
    # Facteur d'occupation (plus d'occupants = plus de consommation)
    occupancy_factor = 0.8 + (occupants - 1) * 0.1
    annual_base_kwh *= occupancy_factor
    
    # Génération du profil horaire sur une année
    hours_per_year = 8760
    time_index = pd.date_range('2020-01-01', periods=hours_per_year, freq='H')
    
    # Profil de base avec variations saisonnières et journalières
    base_profile = []
    
    for hour_idx, timestamp in enumerate(time_index):
        hour = timestamp.hour
        day_of_year = timestamp.timetuple().tm_yday
        is_weekend = timestamp.weekday() >= 5
        
        # Variation saisonnière (chauffage)
        seasonal_factor = 1.5 + 0.8 * np.cos(2 * np.pi * (day_of_year - 15) / 365)
        
        # Variation journalière
        if 6 <= hour <= 22:  # Heures de jour
            if is_weekend:
                daily_factor = 1.2  # Plus de consommation le weekend
            else:
                daily_factor = 0.8 if 9 <= hour <= 17 else 1.1  # Moins pendant les heures de travail
        else:  # Nuit
            daily_factor = 0.4
        
        # Facteur de charge horaire
        hourly_factor = seasonal_factor * daily_factor
        base_profile.append(hourly_factor)
    
    # Normalisation pour respecter la consommation annuelle
    base_profile = np.array(base_profile)
    base_profile = base_profile / base_profile.sum() * annual_base_kwh
    
    return pd.Series(base_profile, index=time_index)

def _calculate_appliances_consumption(appliances: List[Dict], occupants: int) -> pd.Series:
    """
    Calcule la consommation des appareils électroménagers
    """
    hours_per_year = 8760
    time_index = pd.date_range('2020-01-01', periods=hours_per_year, freq='H')
    total_consumption = pd.Series(0, index=time_index)
    
    for appliance in appliances:
        try:
            app_consumption = _simulate_single_appliance(appliance, occupants, time_index)
            total_consumption += app_consumption
        except Exception as e:
            logger.warning(f"Erreur simulation appareil {appliance.get('name', 'Unknown')}: {e}")
            continue
    
    return total_consumption

def _simulate_single_appliance(appliance: Dict, occupants: int, time_index: pd.DatetimeIndex) -> pd.Series:
    """
    Simule la consommation d'un appareil spécifique
    """
    name = appliance.get('name', 'Unknown')
    model = appliance.get('model', 'Standard')
    usage_hours = appliance.get('usage_hours', 1)
    
    # Recherche dans la base de données d'appareils
    app_data = _find_appliance_data(name, model)
    
    if not app_data:
        logger.warning(f"Appareil non trouvé: {name} {model}")
        return pd.Series(0, index=time_index)
    
    power_kw = app_data.get('power_kw', 0.1)
    usage_profile = app_data.get('usage_profile', {})
    
    # Génération du profil de consommation
    consumption = []
    
    for timestamp in time_index:
        hour = timestamp.hour
        is_weekend = timestamp.weekday() >= 5
        
        # Profil d'usage selon le type d'appareil
        if isinstance(usage_profile, dict):
            if 'weekday' in usage_profile and 'weekend' in usage_profile:
                profile = usage_profile['weekend'] if is_weekend else usage_profile['weekday']
                if hour < len(profile):
                    usage_factor = profile[hour]
                else:
                    usage_factor = 0
            else:
                usage_factor = usage_profile.get(str(hour), 0.1)
        elif isinstance(usage_profile, list) and len(usage_profile) == 24:
            usage_factor = usage_profile[hour]
        else:
            # Profil par défaut
            usage_factor = 0.5 if 8 <= hour <= 22 else 0.1
        
        # Application facteurs correctifs
        usage_factor *= (usage_hours / 7)  # Ajustement selon usage déclaré
        usage_factor *= min(occupants / 2, 1.5)  # Facteur occupation
        
        # Consommation horaire
        hourly_consumption = power_kw * usage_factor
        consumption.append(hourly_consumption)
    
    return pd.Series(consumption, index=time_index)

def _find_appliance_data(name: str, model: str) -> Dict:
    """
    Recherche les données d'un appareil dans la base
    """
    for category in APPLIANCES.values():
        if isinstance(category, dict):
            for device_name, models in category.items():
                if device_name.lower() in name.lower():
                    if isinstance(models, dict):
                        return models.get(model, models.get('Standard', models.get(list(models.keys())[0], {})))
    
    return {}

def _apply_consumption_patterns(consumption: pd.Series, occupants: int) -> pd.Series:
    """
    Applique des patterns de consommation réalistes
    """
    # Variation aléatoire réaliste
    noise = np.random.normal(1, 0.1, len(consumption))
    consumption = consumption * noise
    
    # Pics de consommation réalistes
    peak_hours = [7, 8, 12, 18, 19, 20]  # Heures de pointe
    for hour in peak_hours:
        mask = consumption.index.hour == hour
        consumption.loc[mask] *= 1.2
    
    # Limitation par la puissance souscrite (estimation)
    max_power_kw = 6 + occupants * 3  # 6-12 kW selon foyer
    consumption = consumption.clip(upper=max_power_kw)
    
    return consumption.clip(lower=0)
