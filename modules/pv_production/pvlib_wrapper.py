# -*- coding: utf-8 -*-
"""
Interface PVLib pour calculs de production solaire - VERSION CORRIGÉE AVEC PVWATTS
"""
import pandas as pd
import numpy as np
from pvlib import pvsystem, modelchain, location, irradiance, atmosphere
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
import logging

from .caching import hash_parameters, cached_simulation_memory, save_to_cache
from .database import DatabaseManager
from core.exceptions import PVCalculationError

# Initialisation
logger = logging.getLogger(__name__)

# Initialisation du gestionnaire de base de données
db_manager = DatabaseManager()

def _decompose_ghi(ghi, solar_elevation):
    """
    Décompose GHI en DNI et DHI en utilisant un modèle simple
    """
    # Modèle de Erbs et al. pour la fraction diffuse
    kt = ghi / (1367 * np.sin(np.radians(np.maximum(solar_elevation, 1))))  # Indice de clarté
    kt = np.clip(kt, 0, 1)
    
    # Fraction diffuse selon l'indice de clarté
    diffuse_fraction = np.where(
        kt <= 0.22, 1.0 - 0.09 * kt,
        np.where(kt <= 0.8, 0.9511 - 0.1604 * kt + 4.388 * kt**2 - 16.638 * kt**3 + 12.336 * kt**4,
                 0.165)
    )
    
    dhi = ghi * diffuse_fraction
    
    # DNI calculé géométriquement
    dni = np.where(
        solar_elevation > 0,
        (ghi - dhi) / np.sin(np.radians(solar_elevation)),
        0
    )
    
    return dni, dhi

def _pvwatts_calculation(location_params: dict, system_params: dict, weather: pd.DataFrame) -> dict:
    """
    Calcul PV avec le modèle PVWatts simplifié - PLUS ROBUSTE
    """
    try:
        logger.info("Utilisation du modèle PVWatts simplifié")
        
        # 1. Création de la localisation
        site = location.Location(
            latitude=location_params['lat'],
            longitude=location_params['lon'],
            tz='UTC',  # UTC pour éviter les problèmes de timezone
            altitude=location_params.get('altitude', 100)
        )
        
        # 2. Paramètres PVWatts standard
        pvwatts_params = {
            'pdc0': system_params['power_kw'] * 1000,  # Puissance DC en watts
            'gamma_pdc': -0.004,  # Coefficient de température standard
        }
        
        # 3. Création du système avec PVWatts
        system = pvsystem.PVSystem(
            surface_tilt=location_params.get('tilt', 30),
            surface_azimuth=location_params.get('azimuth', 180),
            module_parameters=pvwatts_params,
            inverter_parameters={'pdc0': system_params['power_kw'] * 1000, 'eta_inv_nom': 0.95}
        )
        
        # 4. Préparation des données météo minimales
        weather_clean = weather.copy()
        
        # Colonnes requises pour PVWatts
        required_columns = ['ghi', 'temp_air', 'wind_speed']
        
        # Vérification et calcul des composantes manquantes
        if 'ghi' not in weather_clean.columns:
            raise PVCalculationError("Colonne GHI manquante dans les données météo")
        
        # Ajout des colonnes manquantes avec valeurs par défaut
        if 'temp_air' not in weather_clean.columns:
            weather_clean['temp_air'] = 20  # Température par défaut
            logger.warning("Température de l'air manquante, utilisation de 20°C")
        
        if 'wind_speed' not in weather_clean.columns:
            weather_clean['wind_speed'] = 1  # Vitesse de vent par défaut
            logger.warning("Vitesse du vent manquante, utilisation de 1 m/s")
        
        # DNI et DHI si manquants
        if 'dni' not in weather_clean.columns or 'dhi' not in weather_clean.columns:
            logger.info("Calcul DNI/DHI à partir de GHI")
            solar_position = site.get_solarposition(weather_clean.index)
            weather_clean['dni'], weather_clean['dhi'] = _decompose_ghi(
                weather_clean['ghi'], solar_position['elevation']
            )
        
        # Nettoyage des données
        for col in ['ghi', 'dni', 'dhi']:
            if col in weather_clean.columns:
                weather_clean[col] = weather_clean[col].fillna(0).clip(lower=0)
        
        weather_clean['temp_air'] = weather_clean['temp_air'].fillna(20)
        weather_clean['wind_speed'] = weather_clean['wind_speed'].fillna(1).clip(lower=0)
        
        # 5. Création du ModelChain avec PVWatts
        mc = modelchain.ModelChain.with_pvwatts(
            system, site,
            module_parameters=pvwatts_params,
            inverter_parameters={'pdc0': system_params['power_kw'] * 1000, 'eta_inv_nom': 0.95}
        )
        
        # 6. Exécution de la simulation
        logger.info("Lancement simulation PVWatts...")
        mc.run_model(weather_clean)
        
        # 7. Extraction des résultats
        if mc.results.ac is None:
            raise PVCalculationError("Résultats de simulation vides")
        
        ac_power_kw = mc.results.ac / 1000  # Conversion W -> kW
        
        # Nettoyage des valeurs aberrantes
        ac_power_kw = ac_power_kw.fillna(0).clip(lower=0)
        
        # Limitation par la puissance installée (avec marge pour les pics)
        max_power = system_params['power_kw'] * 1.2  # 20% de marge
        ac_power_kw = ac_power_kw.clip(upper=max_power)
        
        results = {
            'hourly_production_kw': ac_power_kw,
            'annual_yield_kwh': float(ac_power_kw.sum()),
            'capacity_factor': float(ac_power_kw.mean() / system_params['power_kw']),
            'peak_power_kw': float(ac_power_kw.max()),
            'cached': False,
            'model_used': 'PVWatts'
        }
        
        logger.info(f"Simulation PVWatts terminée: {results['annual_yield_kwh']:.0f} kWh/an")
        return results
        
    except Exception as e:
        logger.error(f"Erreur calcul PVWatts: {str(e)}")
        raise PVCalculationError(f"Calcul PVWatts échoué: {str(e)}")

def _original_pv_calculation(location_params: dict, system_params: dict, weather: pd.DataFrame) -> dict:
    """
    Calcul PV réel avec PVLib - FONCTION CORRIGÉE MAIS OPTIONNELLE
    """
    try:
        # 1. Création de la localisation
        site = location.Location(
            latitude=location_params['lat'],
            longitude=location_params['lon'],
            tz='Europe/Paris',  # À adapter selon la localisation
            altitude=location_params.get('altitude', 100)
        )
        
        # 2. Configuration du système PV avec paramètres de température explicites
        
        # Paramètres du module avec modèle de température SAPM
        module_params = {
            'pdc0': system_params['power_kw'] * 1000,  # Puissance DC en watts
            'gamma_pdc': -0.004,  # Coefficient de température (%/°C)
            # Ajout des paramètres nécessaires pour le modèle SAPM
            'A': 0.031,  # Paramètre SAPM
            'B': -1.26,  # Paramètre SAPM
            'C': 0.34,   # Paramètre SAPM (pour modules en verre/cellule/verre)
        }
        
        # Paramètres de l'onduleur
        inverter_params = {
            'pdc0': system_params['power_kw'] * 1000,
            'eta_inv_nom': system_params.get('inverter_efficiency', 0.95),
            'eta_inv_ref': system_params.get('inverter_efficiency', 0.95)
        }
        
        # 3. Configuration du système complet avec paramètres explicites
        system = pvsystem.PVSystem(
            surface_tilt=location_params.get('tilt', 30),
            surface_azimuth=location_params.get('azimuth', 180),
            module_parameters=module_params,
            inverter_parameters=inverter_params,
            modules_per_string=1,
            strings_per_inverter=1,
            # Ajout explicite du modèle de montage et type de module
            racking_model='open_rack',  # Montage en toiture ventilée
            module_type='glass_glass'   # Type de module standard
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
        
        # 5. Création du modèle de chaîne de production avec paramètres explicites
        mc = modelchain.ModelChain(
            system, site,
            aoi_model='physical',
            spectral_model='no_loss',
            temperature_model='sapm',  # Modèle de température explicite
            losses_model='pvwatts',
            # Paramètres additionnels pour le modèle de température
            temperature_model_parameters={
                'A': module_params['A'],
                'B': module_params['B'], 
                'C': module_params['C']
            }
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
            'cached': False,
            'model_used': 'Advanced'
        }
        
        logger.info(f"Simulation PV avancée terminée: {results['annual_yield_kwh']:.0f} kWh/an")
        return results
        
    except Exception as e:
        logger.error(f"Erreur calcul PVLib avancé: {str(e)}")
        # En cas d'erreur, on bascule sur PVWatts
        logger.info("Basculement vers PVWatts...")
        return _pvwatts_calculation(location_params, system_params, weather)

def estimate_energy_yield(location_params: dict, system_params: dict) -> float:
    """
    Estimation rapide de production annuelle sans données météo détaillées
    """
    try:
        # Estimation basée sur l'irradiation moyenne par région
        latitude = location_params['lat']
        
        # Irradiation annuelle estimée selon la latitude (Europe)
        if latitude > 50:  # Nord de l'Europe
            annual_irradiation = 1000  # kWh/m²/an
        elif latitude > 45:  # Centre Europe
            annual_irradiation = 1200
        else:  # Sud Europe
            annual_irradiation = 1400
        
        # Facteurs de correction
        tilt_factor = 1.0  # Simplification : pas de correction d'inclinaison
        azimuth_factor = 1.0  # Simplification : pas de correction d'orientation
        system_efficiency = 0.85  # Rendement global du système
        
        # Calcul de la production estimée
        annual_yield = (system_params['power_kw'] * annual_irradiation * 
                       tilt_factor * azimuth_factor * system_efficiency)
        
        return annual_yield
        
    except Exception as e:
        logger.error(f"Erreur estimation production: {str(e)}")
        return 0.0

def simulate_pv_system(
    location: dict,
    system: dict,
    weather: pd.DataFrame,
    use_cache: bool = True,
    use_db: bool = True,
    use_simple_model: bool = False,  # NOUVEAU PARAMÈTRE
    **kwargs
) -> dict:
    """
    Simulation PV avec cache et base de données - VERSION CORRIGÉE AVEC OPTION SIMPLE
    """
    # Génération du hash unique
    params = {
        "location": location,
        "system": system,
        "weather_hash": hash_parameters(weather.mean().to_dict() if not weather.empty else {}),
        "use_simple_model": use_simple_model  # Inclus dans le hash
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

    # 3. Calcul complet si aucun cache
    try:
        # CHOIX DU MODÈLE
        if use_simple_model:
            logger.info("Utilisation du modèle PVWatts simplifié")
            results = _pvwatts_calculation(location, system, weather)
        else:
            logger.info("Tentative avec modèle avancé, fallback PVWatts si échec")
            try:
                results = _original_pv_calculation(location, system, weather)
            except Exception as e:
                logger.warning(f"Modèle avancé échoué: {e}, basculement vers PVWatts")
                results = _pvwatts_calculation(location, system, weather)
        
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
