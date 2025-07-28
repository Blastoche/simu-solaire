# -*- coding: utf-8 -*-
"""
Encapsulation des calculs PVLib avec gestion d'erreurs et logging.
"""
import pandas as pd
import numpy as np
import pvlib
from pvlib.modelchain import ModelChain
from pvlib.location import Location
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
from core.exceptions import PVCalculationError

# Configurations des modules PV (SANDBIA Database)
MODULE_PARAMS = {
    'mono-Si': {
        'pdc0': 300,       # Puissance DC nominale (W)
        'gamma_pdc': -0.004, # Coefficient de température
        'module_type': 'glass_polymer'
    },
    'poly-Si': {
        'pdc0': 290,
        'gamma_pdc': -0.0038,
        'module_type': 'glass_glass'
    }
}

INVERTER_PARAMS = {
    'standard': {
        'pdc0': 5000,      # Puissance nominale onduleur (W)
        'eta_inv_nom': 0.96 # Rendement
    }
}

def simulate_pv_system(
    location: dict,
    system: dict,
    weather: pd.DataFrame,
    **kwargs
) -> dict:
    """
    Simule la production PV heure par heure.
    
    Args:
        location: {
            'lat': float, 'lon': float,
            'altitude': float (optionnel),
            'tz': str (optionnel, ex: 'Europe/Paris')
        }
        system: {
            'module_type': str (ex: 'mono-Si'),
            'power_kw': float,
            'tilt': float,
            'azimuth': float,
            'racking': str ('ground', 'roof')
        }
        weather: DataFrame avec colonnes ['GHI', 'DHI', 'DNI', 'temp_air']
    
    Returns:
        {
            'hourly': pd.Series,  # Production horaire (kWh)
            'annual_yield': float # Production annuelle (kWh)
        }
    """
    try:
        # 1. Configuration du site
        site = Location(
            latitude=location['lat'],
            longitude=location['lon'],
            altitude=location.get('altitude', 0),
            tz=location.get('tz', 'UTC')
        )

        # 2. Paramètres du système
        module_type = system.get('module_type', 'mono-Si')
        temperature_params = TEMPERATURE_MODEL_PARAMETERS['sapm'][
            system.get('racking', 'roof')
        ]

        system = PVSystem(
            surface_tilt=system['tilt'],
            surface_azimuth=system['azimuth'],
            module_parameters=MODULE_PARAMS[module_type],
            inverter_parameters=INVERTER_PARAMS['standard'],
            temperature_model_parameters=temperature_params
        )

        # 3. Chaîne de calcul
        mc = ModelChain(
            system, site,
            aoi_model='physical',
            spectral_model='no_loss',
            dc_model='sapm',
            ac_model='pvsyst',
            losses_model='no_loss'
        )

        # 4. Simulation
        mc.run_model(weather)
        
        # Conversion W -> kW et index temporel propre
        ac_power = mc.results.ac / 1000  
        ac_power.name = 'production_kw'
        ac_power.index = weather.index

        return {
            'hourly': ac_power,
            'annual_yield': ac_power.sum(),
            'performance': mc.results.dc
        }

    except Exception as e:
        raise PVCalculationError(
            f"Erreur dans simulate_pv_system: {str(e)}"
        )

def estimate_energy_yield(
    location: dict,
    system: dict
) -> float:
    """
    Estimation rapide sans données météo détaillées.
    Utilise les données PVGIS intégrées.
    """
    # [...] Implémentation simplifiée pour calculs préliminaires
