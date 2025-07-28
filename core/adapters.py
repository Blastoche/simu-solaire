# -*- coding: utf-8 -*-
"""
Adapte les entrées UI au format attendu par le moteur de simulation
"""
from typing import Dict

def ui_to_simulation_params(ui_state: Dict) -> Dict:
    """
    Transforme les données de l'interface utilisateur 
    en paramètres pour SimulationEngine.
    """
    return {
        "location": {
            "lat": ui_state['latitude'],
            "lon": ui_state['longitude'],
            "tilt": ui_state.get('tilt', 30),
            "azimuth": _orientation_to_degrees(ui_state['orientation'])
        },
        "pv_system": {
            "power_kw": ui_state['pv_power'],
            "module_type": ui_state.get('module_type', 'standard')
        },
        "appliances": _parse_appliances(ui_state['selected_appliances']),
        "household": {
            "dpe": ui_state['dpe'],
            "occupants": ui_state['occupants']
        }
    }

def _orientation_to_degrees(orientation: str) -> int:
    """Convertit 'Sud' → 180°, 'Est' → 90°, etc."""
    mapping = {
        'Sud': 180,
        'Sud-Est': 135,
        'Sud-Ouest': 225,
        'Est': 90,
        'Ouest': 270
    }
    return mapping.get(orientation, 180)

def _parse_appliances(appliances: List[Dict]) -> List[Dict]:
    """Normalise la structure des appareils"""
    return [
        {
            "name": app['name'],
            "model": app['model'],
            "usage_hours": app['usage_hours']
        }
        for app in appliances
    ]
