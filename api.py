# -*- coding: utf-8 -*-
"""
Configuration des API externes
"""

PVGIS_URL = "https://re.jrc.ec.europa.eu/api/v5_2/PVcalc"
OPENWEATHER_URL = "https://api.openweathermap.org/data/3.0/onecall"

# Obtenez une clé gratuite sur : https://openweathermap.org/api
OPENWEATHER_API_KEY = "votre_clé_api"  # À remplacer

HEADERS = {
    "User-Agent": "SolarSimulator/1.0 (contact@example.com)"
}
