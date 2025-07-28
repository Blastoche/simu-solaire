# -*- coding: utf-8 -*-
"""
Simulation de production photovoltaïque avec pvlib
"""
from pvlib import location, pvsystem, modelchain
import pandas as pd

def simulate(lat: float, lon: float, tilt: float, azimuth: float, weather: pd.DataFrame) -> dict:
    """Calcule la production horaire"""
    site = location.Location(lat, lon)
    system = pvsystem.PVSystem(
        surface_tilt=tilt,
        surface_azimuth=azimuth,
        module_parameters={"pdc0": 300, "gamma_pdc": -0.004},  # 300W/module
        inverter_parameters={"pdc0": 3000}  # 3kW
    )
    mc = modelchain.ModelChain(system, site)
    mc.run_model(weather)
    return {
        "hourly": mc.results.ac,
        "annual_kwh": mc.results.ac.sum()
    }
