# =================
# config/api.py - VERSION CORRIGÉE
# =================
"""
Configuration des API externes avec gestion d'erreur
"""
import os

# PVGIS (service public européen, pas de clé requise)
PVGIS_URL = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"

# OpenWeatherMap (nécessite inscription gratuite)
OPENWEATHER_URL = "https://api.openweathermap.org/data/3.0/onecall"
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "votre_cle_ici")

# Headers par défaut
HEADERS = {
    "User-Agent": "SolarSimulator/2.0",
    "Accept": "application/json"
}

# Limites et timeouts
API_CONFIG = {
    "timeout": 30,
    "max_retries": 3,
    "rate_limit_delay": 1.0  # secondes entre requêtes
}
