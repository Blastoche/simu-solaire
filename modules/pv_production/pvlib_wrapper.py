# -*- coding: utf-8 -*-
"""
Interface PVLib pour calculs de production solaire
Version corrigée sans référence circulaire
"""
import pandas as pd
import numpy as np
from pvlib import pvsystem, modelchain, location, irradiance, atmosphere
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
import logging

from .caching import hash_parameters, cached_simulation_memory, save_to_cache
from .database import DatabaseManager  # ✅ Import ajouté
from core.exceptions import PVCalculationError

# Initialisation
logger = logging.getLogger(__name__)

# ✅ Initialisation du gestionnaire de base de données
db_manager = DatabaseManager()

def _original_pv_calculation(location_params: dict, system_params: dict, weather: pd.DataFrame) -> dict:
    """
    Calcul PV réel avec PVLib - FONCTION CORRIGÉE
    """
    try:
        # 1. Création de la localisation
        site = location.Location(
            latitude=location_params['lat'],
            longitude=location_params['lon'],
            tz='Europe/Paris',  # À adapter selon la localisation
            altitude=location_params.get('altitude', 100)
        )
        
        # 2. Configuration du système PV
        module_params = {
            'pdc0': system_params['power_kw'] * 1000,  # Puissance DC en watts
            'gamma_pdc': -0.004,  # Coefficient de température (%/°C)
        }
        
        inverter_params = {
            'pdc0': system_params['power_kw'] * 1000,
            'eta_inv_nom': system_params.get('inverter_efficiency', 0.95)
        }
        
        # 3. Configuration du système complet
        system = pvsystem.PVSystem(
            surface_tilt=location_params.get('tilt', 30),
            surface_azimuth=location_params.get('azimuth', 180),
            module_parameters=module_params,
            inverter_parameters=inverter_params,
            modules_per_string=1,
            strings_per_inverter=1
        )
        
        # 4. Préparation des données météo pour PVLib
        weather_pvlib = weather.copy()
        required_columns = ['ghi', 'dni', 'dhi', 'temp_air', 'wind_speed']
        
        # Vérification et calcul des composantes manquantes
        if 'dni' not in weather_pvlib.columns or 'dhi' not in weather_pvlib.columns:
            if 'ghi' in weather_pvlib.columns:
                # Calcul DNI/DHI à partir de GHI avec modèle de décomposition
                solar_position = site.get_solarposition(weather_pvlib.index)
                weather_pvlib['dni'], weather_pvlib['dhi'] = _decompose_ghi(
                    weather_pvlib['ghi'], solar_position['elevation']
                )
        
        # Valeurs par défaut si colonnes manquantes
        for col, default_val in [('temp_air', 20), ('wind_speed', 1)]:
            if col not in weather_pvlib.columns:
                weather_pvlib[col] = default_val
                logger.warning(f"Colonne {col} manquante, valeur par défaut: {default_val}")
        
        # 5. Création du modèle de chaîne de production
        mc = modelchain.ModelChain(
            system, site,
            aoi_model='physical',
            spectral_model='no_loss',
            temperature_model='sapm',
            losses_model='pvwatts'
        )
        
        # 6. Exécution de la simulation
        mc.run_model(weather_pvlib)
        
        # 7. Extraction des résultats
        ac_power_kw = mc.results.ac / 1000  # Conversion W -> kW
        
        # Nettoyage des valeurs aberrantes
        ac_power_kw = ac_power_kw.fillna(0).clip(lower=0)
        
        results = {
            'hourly_production_kw': ac_power_kw,
            'annual_yield_kwh': float(ac_power_kw.sum()),
            'capacity_factor': float(ac_power_kw.mean() / system_params['power_kw']),
            'peak_power_kw': float(ac_power_kw.max()),
            'cached': False
        }
        
        logger.info(f"Simulation PV terminée: {results['annual_yield_kwh']:.0f} kWh/an")
        return results
        
    except Exception as e:
        logger.error(f"Erreur calcul PVLib: {str(e)}")
        raise PVCalculationError(f"Échec du calcul PV: {str(e)}")

# ... (reste des fonctions inchangées)

def simulate_pv_system(
    location: dict,
    system: dict,
    weather: pd.DataFrame,
    use_cache: bool = True,
    use_db: bool = True,
    **kwargs
) -> dict:
    """
    Simulation PV avec cache et base de données - VERSION CORRIGÉE
    """
    # Génération du hash unique
    params = {
        "location": location,
        "system": system,
        "weather_hash": hash_parameters(weather.mean().to_dict() if not weather.empty else {})
    }
    params_hash = hash_parameters(params)

    # 1. Vérification du cache mémoire
    if use_cache:
        try:
            cached = cached_simulation_memory(params_hash)
            logger.info("Cache mémoire hit")
            return cached
        except ValueError:
            pass  # Cache miss

    # 2. Vérification de la base de données
    if use_db:
        try:
            db_results = db_manager.get_simulation(params_hash)
            if db_results:
                logger.info("Cache SGBD hit")
                save_to_cache(params_hash, db_results)
                return db_results
        except Exception as e:
            logger.warning(f"Erreur accès base de données: {e}")

    # 3. Calcul complet si aucun cache - APPEL CORRIGÉ
    try:
        results = _original_pv_calculation(location, system, weather)
        
        # Sauvegarde dans les systèmes de cache
        if use_cache:
            try:
                save_to_cache(params_hash, results)
            except Exception as e:
                logger.warning(f"Erreur sauvegarde cache: {e}")
        
        if use_db:
            try:
                db_manager.save_simulation(params_hash, params, results)
            except Exception as e:
                logger.warning(f"Erreur sauvegarde DB: {e}")
        
        return results

    except Exception as e:
        logger.error(f"Erreur de simulation : {str(e)}")
        raise PVCalculationError(f"Simulation PV échouée: {str(e)}")
