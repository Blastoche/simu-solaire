# -*- coding: utf-8 -*-
"""
Interface unifiée pour les données météo.
Choix automatique de la meilleure source disponible.
"""
from .pvgis_direct import fetch_pvgis_direct
from .mock_weather import generate_mock_weather
from core.exceptions import WeatherDataError

def get_weather_data(lat: float, lon: float, **kwargs) -> dict:
    """
    Tente PVGIS -> Si échec, utilise les données mock.
    
    Args:
        use_mock: bool - Force l'utilisation des données simulées
    """
    try:
        if kwargs.get('use_mock'):
            raise WeatherDataError("Mode mock forcé")
            
        return {
            'source': 'PVGIS',
            'data': fetch_pvgis_direct(lat, lon, **kwargs)
        }
    except Exception as e:
        return {
            'source': 'MOCK',
            'data': generate_mock_weather(lat, lon),
            'warning': f"PVGIS indisponible: {str(e)}"
        }
