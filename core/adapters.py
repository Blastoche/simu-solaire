# -*- coding: utf-8 -*-
"""
Adapte les entrées UI au format attendu par le moteur de simulation
"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

def ui_to_simulation_params(ui_state: Dict) -> Dict:
    """Version robuste de la conversion UI vers paramètres simulation"""
    try:
        # Vérification des paramètres obligatoires
        required_params = {
            'latitude': float,
            'longitude': float,
            'dpe': str,
            'occupants': int
        }
        
        for param, param_type in required_params.items():
            if param not in ui_state:
                raise KeyError(f"Paramètre obligatoire manquant: {param}")
            
            # Conversion de type si nécessaire
            try:
                ui_state[param] = param_type(ui_state[param])
            except (ValueError, TypeError):
                raise ValueError(f"Type invalide pour {param}: attendu {param_type.__name__}")
        
        # Construction des paramètres de simulation
        params = {
            "location": {
                "lat": ui_state['latitude'],
                "lon": ui_state['longitude'],
                "tilt": ui_state.get('tilt', 30),
                "azimuth": _orientation_to_degrees(ui_state.get('orientation', 'Sud'))
            },
            "pv_system": {
                "power_kw": ui_state.get('pv_power', 3.0),
                "module_type": ui_state.get('module_type', 'standard'),
                "inverter_efficiency": ui_state.get('inverter_efficiency', 0.95)
            },
            "appliances": _parse_appliances(ui_state.get('selected_appliances', [])),
            "household": {
                "dpe": ui_state['dpe'],
                "occupants": ui_state['occupants'],
                "surface": ui_state.get('surface', 100),
                "heating_type": ui_state.get('heating_type', 'electric')
            }
        }
        
        # Validation des valeurs
        _validate_simulation_params(params)
        
        return params
        
    except Exception as e:
        logger.error(f"Erreur conversion paramètres UI: {str(e)}")
        raise

def _validate_simulation_params(params: Dict):
    """Valide les paramètres de simulation"""
    location = params['location']
    
    # Validation géographique
    if not (-90 <= location['lat'] <= 90):
        raise ValueError(f"Latitude invalide: {location['lat']}")
    if not (-180 <= location['lon'] <= 180):
        raise ValueError(f"Longitude invalide: {location['lon']}")
    
    # Validation système PV
    pv_system = params['pv_system']
    if pv_system['power_kw'] <= 0 or pv_system['power_kw'] > 1000:
        raise ValueError(f"Puissance PV invalide: {pv_system['power_kw']} kW")
    
    # Validation foyer
    household = params['household']
    if household['occupants'] <= 0 or household['occupants'] > 20:
        raise ValueError(f"Nombre d'occupants invalide: {household['occupants']}")

def _orientation_to_degrees(orientation: str) -> int:
    """Convertit l'orientation texte en degrés avec gestion d'erreur"""
    mapping = {
        'Nord': 0, 'Nord-Est': 45, 'Est': 90, 'Sud-Est': 135,
        'Sud': 180, 'Sud-Ouest': 225, 'Ouest': 270, 'Nord-Ouest': 315
    }
    
    result = mapping.get(orientation, 180)  # Sud par défaut
    if orientation not in mapping:
        logger.warning(f"Orientation inconnue '{orientation}', utilisation 'Sud'")
    
    return result

def _parse_appliances(appliances: List[Dict]) -> List[Dict]:
    """Parse et valide la liste des appareils"""
    parsed = []
    
    for app in appliances:
        try:
            parsed_app = {
                "name": str(app.get('name', 'Inconnu')),
                "model": str(app.get('model', 'Standard')),
                "usage_hours": max(0, float(app.get('usage_hours', 1)))
            }
            parsed.append(parsed_app)
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Appareil invalide ignoré: {app}, erreur: {e}")
            continue
    
    return parsed
