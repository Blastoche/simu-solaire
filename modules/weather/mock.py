# modules/weather/mock_weather.py
# -*- coding: utf-8 -*-
"""
Générateur de données météo simulées pour tests et fallback.
Basé sur des modèles climatologiques par région géographique.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional
import math

# Zones climatiques simplifiées (lat, lon) -> paramètres
CLIMATE_ZONES = {
    # France métropolitaine
    'france_north': {
        'lat_range': (47, 51), 'lon_range': (-5, 8),
        'ghi_annual': 1100, 'temp_avg': 11, 'temp_range': 25,
        'cloud_factor': 0.6, 'seasonal_variation': 0.8
    },
    'france_south': {
        'lat_range': (43, 47), 'lon_range': (-1, 8),
        'ghi_annual': 1400, 'temp_avg': 14, 'temp_range': 28,
        'cloud_factor': 0.4, 'seasonal_variation': 0.9
    },
    # Méditerranée
    'mediterranean': {
        'lat_range': (35, 45), 'lon_range': (-10, 40),
        'ghi_annual': 1600, 'temp_avg': 16, 'temp_range': 30,
        'cloud_factor': 0.3, 'seasonal_variation': 1.0
    },
    # Europe du Nord
    'northern_europe': {
        'lat_range': (50, 70), 'lon_range': (-10, 30),
        'ghi_annual': 900, 'temp_avg': 8, 'temp_range': 20,
        'cloud_factor': 0.7, 'seasonal_variation': 0.6
    },
    # Zone par défaut
    'default': {
        'lat_range': (-90, 90), 'lon_range': (-180, 180),
        'ghi_annual': 1200, 'temp_avg': 12, 'temp_range': 25,
        'cloud_factor': 0.5, 'seasonal_variation': 0.7
    }
}

def generate_mock_weather(
    lat: float, 
    lon: float, 
    year: int = 2020,
    add_noise: bool = True,
    realistic_patterns: bool = True
) -> pd.DataFrame:
    """
    Génère des données météo simulées réalistes.
    
    Args:
        lat, lon: Coordonnées géographiques
        year: Année de simulation
        add_noise: Ajoute du bruit réaliste
        realistic_patterns: Utilise des patterns météo réalistes
    
    Returns:
        DataFrame avec colonnes: ghi, dni, dhi, temp_air, wind_speed, humidity
    """
    # Détection de la zone climatique
    climate = _get_climate_zone(lat, lon)
    
    # Génération de l'index temporel
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1)
    time_index = pd.date_range(start_date, end_date, freq='H', inclusive='left')
    
    # Calcul des angles solaires
    solar_angles = _calculate_solar_angles(lat, time_index)
    
    # Génération des composantes météo
    weather_data = {
        'ghi': _generate_ghi(solar_angles, climate, add_noise, realistic_patterns),
        'temp_air': _generate_temperature(time_index, lat, climate, add_noise),
        'wind_speed': _generate_wind_speed(time_index, climate, add_noise),
        'humidity': _generate_humidity(time_index, climate, add_noise)
    }
    
    # Calcul DNI et DHI à partir de GHI
    weather_data['dni'], weather_data['dhi'] = _split_irradiance(
        weather_data['ghi'], solar_angles['elevation'], climate
    )
    
    df = pd.DataFrame(weather_data, index=time_index)
    
    # Ajout de patterns météo réalistes
    if realistic_patterns:
        df = _apply_weather_patterns(df, climate)
    
    return df

def _get_climate_zone(lat: float, lon: float) -> Dict:
    """Détermine la zone climatique selon les coordonnées"""
    for zone_name, zone_data in CLIMATE_ZONES.items():
        if zone_name == 'default':
            continue
        
        lat_min, lat_max = zone_data['lat_range']
        lon_min, lon_max = zone_data['lon_range']
        
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            return zone_data
    
    return CLIMATE_ZONES['default']

def _calculate_solar_angles(lat: float, time_index: pd.DatetimeIndex) -> Dict:
    """Calcule les angles solaires (élévation, azimut)"""
    lat_rad = math.radians(lat)
    
    # Jour de l'année (1-365)
    day_of_year = time_index.dayofyear
    
    # Déclinaison solaire
    declination = 23.45 * np.sin(np.radians(360 * (284 + day_of_year) / 365))
    declination_rad = np.radians(declination)
    
    # Angle horaire
    hour_angle = 15 * (time_index.hour - 12)
    hour_angle_rad = np.radians(hour_angle)
    
    # Élévation solaire
    elevation_rad = np.arcsin(
        np.sin(lat_rad) * np.sin(declination_rad) + 
        np.cos(lat_rad) * np.cos(declination_rad) * np.cos(hour_angle_rad)
    )
    elevation = np.degrees(elevation_rad)
    elevation = np.maximum(elevation, 0)  # Pas de soleil sous l'horizon
    
    # Azimut solaire (simplifié)
    azimuth = 180 + np.degrees(np.arctan2(
        np.sin(hour_angle_rad),
        np.cos(hour_angle_rad) * np.sin(lat_rad) - 
        np.tan(declination_rad) * np.cos(lat_rad)
    ))
    
    return {
        'elevation': elevation,
        'azimuth': azimuth,
        'day_of_year': day_of_year
    }

def _generate_ghi(solar_angles: Dict, climate: Dict, add_noise: bool, realistic: bool) -> np.ndarray:
    """Génère l'irradiance globale horizontale"""
    elevation = solar_angles['elevation']
    day_of_year = solar_angles['day_of_year']
    
    # Irradiance extraterrestre
    solar_constant = 1367  # W/m²
    earth_sun_distance = 1 + 0.033 * np.cos(2 * np.pi * day_of_year / 365)
    
    # Irradiance théorique au niveau de la mer
    theoretical_ghi = solar_constant * earth_sun_distance * np.sin(np.radians(elevation))
    theoretical_ghi = np.maximum(theoretical_ghi, 0)
    
    # Facteur de transmission atmosphérique
    clear_sky_factor = 0.7  # Ciel clair typique
    
    # Variation saisonnière
    seasonal_factor = 1 + 0.2 * np.cos(2 * np.pi * (day_of_year - 172) / 365)
    seasonal_factor *= climate['seasonal_variation']
    
    # Application de la nébulosité
    cloud_factor = 1 - climate['cloud_factor']
    
    # GHI de base
    ghi = theoretical_ghi * clear_sky_factor * seasonal_factor * cloud_factor
    
    if realistic:
        # Patterns nuageux réalistes
        cloud_noise = _generate_cloud_patterns(len(elevation), climate['cloud_factor'])
        ghi *= cloud_noise
    
    if add_noise:
        # Bruit aléatoire réaliste
        noise = np.random.normal(0, 0.1, len(ghi))
        ghi *= (1 + noise)
    
    # Ajustement pour correspondre à la moyenne annuelle attendue
    annual_target = climate['ghi_annual']  # kWh/m²/an
    current_annual = np.sum(ghi) / 1000  # Conversion W -> kWh
    if current_annual > 0:
        ghi *= annual_target / current_annual
    
    return np.maximum(ghi, 0)

def _generate_cloud_patterns(length: int, cloud_factor: float) -> np.ndarray:
    """Génère des patterns nuageux réalistes"""
    # Base: alternance jour/nuit
    base_pattern = np.ones(length)
    
    # Ajout de systèmes nuageux (fronts de 2-5 jours)
    num_fronts = int(length / (24 * 3))  # ~1 front tous les 3 jours
    
    for _ in range(num_fronts):
        start_idx = np.random.randint(0, length - 72)  # Front de 3 jours max
        duration = np.random.randint(24, 120)  # 1-5 jours
        end_idx = min(start_idx + duration, length)
        
        # Intensité du front (0.2 = très nuageux, 0.8 = peu nuageux)
        intensity = np.random.uniform(0.2, 0.8)
        base_pattern[start_idx:end_idx] *= intensity
    
    # Variabilité à petite échelle (passages nuageux)
    small_scale_noise = np.random.normal(1, 0.15, length)
    base_pattern *= small_scale_noise
    
    # Ajustement pour respecter le facteur de nébulosité moyen
    current_mean = np.mean(base_pattern)
    target_mean = 1 - cloud_factor
    base_pattern *= target_mean / current_mean
    
    return np.clip(base_pattern, 0.1, 1.0)

def _split_irradiance(ghi: np.ndarray, elevation: np.ndarray, climate: Dict) -> tuple:
    """Sépare GHI en composantes directe (DNI) et diffuse (DHI)"""
    # Modèle de Erbs et al. pour la fraction diffuse
    kt = ghi / (1367 * np.sin(np.radians(np.maximum(elevation, 1))))  # Indice de clarté
    kt = np.clip(kt, 0, 1)
    
    # Fraction diffuse selon l'indice de clarté
    diffuse_fraction = np.where(
        kt <= 0.22, 1.0 - 0.09 * kt,
        np.where(kt <= 0.8, 0.9511 - 0.1604 * kt + 4.388 * kt**2 - 16.638 * kt**3 + 12.336 * kt**4,
                 0.165)
    )
    
    dhi = ghi * diffuse_fraction
    
    # DNI calculé géométriquement
    dni = np.where(
        elevation > 0,
        (ghi - dhi) / np.sin(np.radians(elevation)),
        0
    )
    
    return dni, dhi

def _generate_temperature(time_index: pd.DatetimeIndex, lat: float, climate: Dict, add_noise: bool) -> np.ndarray:
    """Génère la température de l'air"""
    day_of_year = time_index.dayofyear
    hour = time_index.hour
    
    # Température moyenne annuelle
    temp_annual_avg = climate['temp_avg']
    
    # Variation saisonnière
    seasonal_variation = climate['temp_range'] / 2 * np.cos(2 * np.pi * (day_of_year - 200) / 365)
    
    # Variation diurne
    diurnal_variation = 8 * np.cos(2 * np.pi * (hour - 14) / 24)
    
    # Température de base
    temp = temp_annual_avg + seasonal_variation + diurnal_variation
    
    if add_noise:
        # Bruit météorologique
        noise = np.random.normal(0, 2, len(temp))
        temp += noise
    
    return temp

def _generate_wind_speed(time_index: pd.DatetimeIndex, climate: Dict, add_noise: bool) -> np.ndarray:
    """Génère la vitesse du vent"""
    length = len(time_index)
    
    # Vitesse de base (dépend de la zone climatique)
    base_speed = 3.5 if 'france' in str(climate) else 4.0
    
    # Variation saisonnière (plus de vent en hiver)
    seasonal = 1 + 0.3 * np.cos(2 * np.pi * (time_index.dayofyear - 50) / 365)
    
    # Variation diurne (plus de vent l'après-midi)
    diurnal = 1 + 0.2 * np.cos(2 * np.pi * (time_index.hour - 15) / 24)
    
    wind_speed = base_speed * seasonal * diurnal
    
    if add_noise:
        # Distribution log-normale pour réalisme
        noise = np.random.lognormal(0, 0.3, length)
        wind_speed *= noise
    
    return np.clip(wind_speed, 0.5, 15)  # Limites réalistes

def _generate_humidity(time_index: pd.DatetimeIndex, climate: Dict, add_noise: bool) -> np.ndarray:
    """Génère l'humidité relative"""
    day_of_year = time_index.dayofyear
    hour = time_index.hour
    
    # Humidité de base selon la zone
    base_humidity = 70 if climate['cloud_factor'] > 0.5 else 60
    
    # Variation saisonnière
    seasonal = 10 * np.cos(2 * np.pi * (day_of_year - 20) / 365)
    
    # Variation diurne (plus humide la nuit)
    diurnal = -15 * np.cos(2 * np.pi * (hour - 6) / 24)
    
    humidity = base_humidity + seasonal + diurnal
    
    if add_noise:
        noise = np.random.normal(0, 5, len(humidity))
        humidity += noise
    
    return np.clip(humidity, 20, 95)

def _apply_weather_patterns(df: pd.DataFrame, climate: Dict) -> pd.DataFrame:
    """Applique des patterns météo réalistes (corrélations entre variables)"""
    # Corrélation température-humidité
    temp_normalized = (df['temp_air'] - df['temp_air'].mean()) / df['temp_air'].std()
    df['humidity'] -= temp_normalized * 5  # Plus chaud = moins humide
    
    # Corrélation GHI-température
    ghi_effect = (df['ghi'] - df['ghi'].mean()) / df['ghi'].max() * 3
    df['temp_air'] += ghi_effect  # Plus de soleil = plus chaud
    
    # Jours de pluie (GHI faible + humidité haute + vent modéré)
    rainy_days = df['ghi'] < df['ghi'].quantile(0.15)
    df.loc[rainy_days, 'humidity'] += 15
    df.loc[rainy_days, 'wind_speed'] *= 0.7
    
    # Contraintes finales
    df['humidity'] = np.clip(df['humidity'], 20, 95)
    df['wind_speed'] = np.clip(df['wind_speed'], 0.5, 15)
    
    return df

def validate_mock_data(df: pd.DataFrame) -> Dict[str, bool]:
    """Valide la cohérence des données mock générées"""
    checks = {
        'no_negative_ghi': (df['ghi'] >= 0).all(),
        'realistic_temp_range': df['temp_air'].between(-30, 50).all(),
        'valid_humidity': df['humidity'].between(0, 100).all(),
        'positive_wind': (df['wind_speed'] >= 0).all(),
        'complete_year': len(df) >= 8760,
        'no_missing_values': not df.isnull().any().any()
    }
    
    return checks

# Fonction utilitaire pour les tests
def compare_with_real_data(mock_df: pd.DataFrame, real_df: pd.DataFrame) -> Dict:
    """Compare les données mock avec des vraies données pour validation"""
    if real_df is None or real_df.empty:
        return {'comparison': 'no_real_data_available'}
    
    comparison = {}
    
    for col in ['ghi', 'temp_air']:
        if col in both_dataframes:
            mock_mean = mock_df[col].mean()
            real_mean = real_df[col].mean()
            comparison[f'{col}_ratio'] = mock_mean / real_mean if real_mean > 0 else 1.0
    
    return comparison
