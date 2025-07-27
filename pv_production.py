from pvlib import pvsystem, modelchain
import pandas as pd
from typing import Dict

def calculate_with_pvlib(weather_data: pd.DataFrame, system_params: Dict) -> pd.DataFrame:
    """
    Calcule la production PV avec pvlib pour une modélisation précise
    Args:
        weather_data: DataFrame avec GHI, T2m, etc.
        system_params: Dictionnaire de configuration système
    Returns:
        DataFrame avec la production horaire
    """
    # 1. Configuration du système
    system = pvsystem.PVSystem(
        surface_tilt=system_params["tilt"],
        surface_azimuth=system_params["azimuth"],
        module_parameters={'pdc0': system_params["power_kw"] * 1000, 'gamma_pdc': -0.004},
        inverter_parameters={'pdc0': system_params["power_kw"] * 1000}
    )
    
    # 2. Localisation
    site = location.Location(
        latitude=system_params["lat"],
        longitude=system_params["lon"]
    )
    
    # 3. Préparation des données météo
    weather_data = weather_data.set_index("time")
    weather_data["dni"] = irradiance.disc(
        weather_data["GHI"],
        weather_data.index,
        site.latitude,
        site.longitude
    )["dni"]
    
    # 4. Simulation
    mc = modelchain.ModelChain(
        system, site,
        aoi_model="physical",
        spectral_model="no_loss"
    )
    mc.run_model(weather_data)
    
    return mc.results.ac.to_frame("production_kw")
