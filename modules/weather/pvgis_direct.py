# -*- coding: utf-8 -*-
"""
Accès direct à l'API publique PVGIS sans clé requise.
Limite : 1 requête/minute, données 2005-2020.
"""
import requests
import pandas as pd
from datetime import datetime

BASE_URL = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"

def fetch_pvgis_direct(
    lat: float,
    lon: float,
    tilt: float = 30,
    azimuth: float = 180,
    start_year: int = 2020,
    end_year: int = 2020
) -> pd.DataFrame:
    """Remplace l'ancien weather.py pour les tests"""
    params = {
        "lat": lat,
        "lon": lon,
        "angle": tilt,
        "aspect": azimuth,
        "startyear": start_year,
        "endyear": end_year,
        "outputformat": "json",
        "pvcalculation": 0  # Données brutes seulement
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        return _parse_response(response.json())
    except requests.exceptions.RequestException as e:
        raise Exception(f"Erreur PVGIS: {str(e)}")

def _parse_response(json_data: dict) -> pd.DataFrame:
    """Formate les données PVGIS en DataFrame standard"""
    df = pd.DataFrame(json_data["outputs"]["hourly"])
    df["time"] = pd.to_datetime(df["time"], format="%Y%m%d:%H%M")
    return df.rename(columns={
        "G(i)": "ghi",
        "T2m": "temp_air",
        "WS10m": "wind_speed"
    }).set_index("time")
