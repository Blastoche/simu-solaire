import requests
import pandas as pd
from pvlib import location, irradiance
from config.api import PVGIS_URL, OPENWEATHER_URL, OPENWEATHER_API_KEY, HEADERS
import streamlit as st
from typing import Optional, Dict

@st.cache_data(ttl=3600)  # Cache de 1 heure
def fetch_pvgis_historical(lat: float, lon: float, year: int = 2020) -> Optional[pd.DataFrame]:
    """Récupère les données PVGIS avec gestion d'erreur et cache"""
    try:
        params = {
            "lat": lat, "lon": lon,
            "startyear": year, "endyear": year,
            "outputformat": "json",
            "pvcalculation": 0
        }
        response = requests.get(PVGIS_URL, params=params, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        df = pd.DataFrame(response.json()["outputs"]["hourly"])
        df["time"] = pd.to_datetime(df["time"], format="%Y%m%d:%H%M")
        return df[["time", "GHI", "T2m", "RH"]]  # Ajout de l'humidité relative
        
    except Exception as e:
        st.error(f"Erreur PVGIS : {str(e)}")
        return None

@st.cache_data(ttl=1800)  # Cache de 30 minutes
def fetch_openweather_forecast(lat: float, lon: float) -> Optional[Dict]:
    """Récupère les prévisions OpenWeatherMap"""
    try:
        params = {
            "lat": lat, "lon": lon,
            "exclude": "minutely,daily",
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        response = requests.get(OPENWEATHER_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.warning(f"Prévisions non disponibles : {str(e)}")
        return None
