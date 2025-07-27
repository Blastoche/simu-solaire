import requests
import pandas as pd

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
