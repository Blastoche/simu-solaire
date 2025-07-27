import requests
import pandas as pd
from config.api import PVGIS_BASE_URL, HEADERS

def fetch_pvgis_historical(lat: float, lon: float, year: int = 2020):
    """
    Récupère les données météo historiques de PVGIS (année typique)
    Retourne un DataFrame avec : GHI (W/m²), Température (°C), etc.
    """
    params = {
        "lat": lat,
        "lon": lon,
        "startyear": year,
        "endyear": year,
        "outputformat": "json",
        "pvcalculation": 0  # Désactive le calcul PV pour avoir les données brutes
    }
    
    try:
        response = requests.get(PVGIS_BASE_URL, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Transformation en DataFrame
        df = pd.DataFrame(data["outputs"]["hourly"])
        df["time"] = pd.to_datetime(df["time"], format="%Y%m%d:%H%M")
        return df[["time", "GHI", "T2m"]]  # Global Horizontal Irradiation, Température à 2m
        
    except Exception as e:
        raise Exception(f"Erreur PVGIS : {str(e)}")


class WeatherFetcher:
    BASE_URLS = {
        "PVGIS": "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc",
        "OpenWeather": "https://api.openweathermap.org/data/3.0/onecall"
    }

    def __init__(self, api_keys):
        self.api_keys = api_keys

    def fetch_historical(self, lat, lon, year):
        """Récupère les données PVGIS"""
        params = {
            "lat": lat, "lon": lon,
            "startyear": year, "endyear": year,
            "outputformat": "json"
        }
        response = requests.get(self.BASE_URLS["PVGIS"], params=params)
        return self._parse_pvgis(response.json())

    def _parse_pvgis(self, data):
        """Transforme la réponse PVGIS en DataFrame"""
        df = pd.DataFrame(data["outputs"]["hourly"])
        df["time"] = pd.to_datetime(df["time"], format="%Y%m%d:%H%M")
        return df[["time", "GHI", "T2m"]]  # Irradiation + température

    def fetch_forecast(self, lat, lon):
        """Récupère les prévisions OpenWeather"""
        params = {
            "lat": lat, "lon": lon,
            "exclude": "minutely,daily",
            "appid": self.api_keys["openweather"]
        }
        response = requests.get(self.BASE_URLS["OpenWeather"], params=params)
        return self._parse_owm(response.json())
