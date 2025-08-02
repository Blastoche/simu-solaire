# -*- coding: utf-8 -*-
"""
Accès direct à l'API publique PVGIS sans clé requise.
Limite : 1 requête/minute, données 2005-2020.
"""
import requests
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"

def fetch_pvgis_direct(
    lat: float,
    lon: float,
    tilt: float = 30,
    azimuth: float = 180,
    start_year: int = 2020,
    end_year: int = 2020
) -> pd.DataFrame:
    """
    Récupère les données PVGIS directement depuis l'API publique
    
    Args:
        lat, lon: Coordonnées géographiques
        tilt: Inclinaison des panneaux (degrés)
        azimuth: Orientation des panneaux (degrés, 180=Sud)
        start_year, end_year: Années de données
    
    Returns:
        DataFrame avec données météo horaires
    """
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
        logger.info(f"Requête PVGIS pour lat={lat}, lon={lon}")
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        return parse_response(data)
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur requête PVGIS: {str(e)}")
        raise Exception(f"Erreur PVGIS: {str(e)}")
    except KeyError as e:
        logger.error(f"Structure de réponse PVGIS inattendue: {e}")
        raise Exception(f"Données PVGIS malformées: {str(e)}")

def parse_response(json_data: dict) -> pd.DataFrame:
    """
    Formate les données PVGIS en DataFrame standard
    
    Args:
        json_data: Réponse JSON de l'API PVGIS
    
    Returns:
        DataFrame formaté avec colonnes standardisées
    """
    try:
        # Extraction des données horaires
        hourly_data = json_data["outputs"]["hourly"]
        df = pd.DataFrame(hourly_data)
        
        # Conversion du timestamp
        df["time"] = pd.to_datetime(df["time"], format="%Y%m%d:%H%M")
        
        # Renommage des colonnes pour correspondre aux standards pvlib
        column_mapping = {
            "G(i)": "ghi",           # Irradiation globale sur plan incliné
            "Gb(i)": "dni",          # Irradiation directe sur plan incliné
            "Gd(i)": "dhi",          # Irradiation diffuse sur plan incliné
            "T2m": "temp_air",       # Température de l'air à 2m
            "WS10m": "wind_speed",   # Vitesse du vent à 10m
            "RH": "humidity"         # Humidité relative (si disponible)
        }
        
        # Application du mapping avec gestion des colonnes manquantes
        available_columns = {}
        for pvgis_col, standard_col in column_mapping.items():
            if pvgis_col in df.columns:
                available_columns[pvgis_col] = standard_col
            else:
                logger.warning(f"Colonne PVGIS manquante: {pvgis_col}")
        
        df = df.rename(columns=available_columns)
        
        # Définition de l'index temporel
        df = df.set_index("time")
        
        # Vérification et correction des valeurs aberrantes
        df = clean_weather_data(df)
        
        logger.info(f"Données PVGIS récupérées: {len(df)} points sur {df.index[0]} - {df.index[-1]}")
        return df
        
    except KeyError as e:
        logger.error(f"Clé manquante dans la réponse PVGIS: {e}")
        raise Exception(f"Structure de données PVGIS invalide: {str(e)}")
    except Exception as e:
        logger.error(f"Erreur parsing PVGIS: {str(e)}")
        raise Exception(f"Impossible de parser les données PVGIS: {str(e)}")

def clean_weather_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie et valide les données météorologiques
    
    Args:
        df: DataFrame avec données brutes
    
    Returns:
        DataFrame nettoyé
    """
    df_clean = df.copy()
    
    # Nettoyage de l'irradiation (GHI)
    if 'ghi' in df_clean.columns:
        df_clean['ghi'] = df_clean['ghi'].clip(lower=0, upper=1400)  # Max théorique ~1400 W/m²
        df_clean['ghi'] = df_clean['ghi'].fillna(0)
    
    # Nettoyage DNI
    if 'dni' in df_clean.columns:
        df_clean['dni'] = df_clean['dni'].clip(lower=0, upper=1000)
        df_clean['dni'] = df_clean['dni'].fillna(0)
    
    # Nettoyage DHI
    if 'dhi' in df_clean.columns:
        df_clean['dhi'] = df_clean['dhi'].clip(lower=0, upper=500)
        df_clean['dhi'] = df_clean['dhi'].fillna(0)
    
    # Nettoyage température
    if 'temp_air' in df_clean.columns:
        df_clean['temp_air'] = df_clean['temp_air'].clip(lower=-40, upper=60)
        df_clean['temp_air'] = df_clean['temp_air'].fillna(20)  # Valeur par défaut
    
    # Nettoyage vitesse du vent
    if 'wind_speed' in df_clean.columns:
        df_clean['wind_speed'] = df_clean['wind_speed'].clip(lower=0, upper=50)
        df_clean['wind_speed'] = df_clean['wind_speed'].fillna(2)  # Valeur par défaut
    
    # Nettoyage humidité
    if 'humidity' in df_clean.columns:
        df_clean['humidity'] = df_clean['humidity'].clip(lower=0, upper=100)
        df_clean['humidity'] = df_clean['humidity'].fillna(60)
    
    return df_clean
