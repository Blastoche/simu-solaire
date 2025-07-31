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

# =================
# modules/consumption/__init__.py - NOUVEAU FICHIER
# =================
"""
Module de simulation de consommation électrique
"""
from .appliance_models import simulate

__all__ = ['simulate']

# =================
# modules/economics/__init__.py - NOUVEAU FICHIER  
# =================
"""
Module d'analyse économique
"""
from .roi_calculator import analyze, generate_economic_report

__all__ = ['analyze', 'generate_economic_report']

# =================
# core/__init__.py - NOUVEAU FICHIER
# =================
"""
Noyau du simulateur solaire
"""

# =================
# requirements.txt - DÉPENDANCES NÉCESSAIRES
# =================
"""
# Calculs scientifiques
pandas>=1.5.0
numpy>=1.21.0

# Photovoltaïque  
pvlib>=0.10.0

# Interface utilisateur
streamlit>=1.28.0
plotly>=5.15.0

# Base de données
sqlalchemy>=1.4.0

# API et requêtes
requests>=2.28.0

# Utilitaires
pathlib
hashlib
functools
logging
json
datetime
typing
"""
