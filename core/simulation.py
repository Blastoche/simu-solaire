# -*- coding: utf-8 -*-
"""
Noyau principal de simulation - Indépendant de l'UI
"""
from typing import Dict, List
import pandas as pd
from modules.weather import pvgis_client
from modules.pv_production import pvlib_wrapper
from modules.consumption import appliance_models
from modules.economics import roi_calculator

class SimulationEngine:
    def __init__(self):
        self.weather_data = None
        self.pv_production = None
        self.consumption = None

    def run(self, params: Dict) -> Dict:
        """Exécute la simulation complète"""
        # 1. Données météo
        self._fetch_weather_data(params['location'])
        
        # 2. Production PV
        self._calculate_pv_production(
            params['pv_system'],
            params['location']
        )
        
        # 3. Consommation
        self._calculate_consumption(
            params['appliances'],
            params['household']
        )
        
        # 4. Analyse économique
        return self._generate_results()

    def _fetch_weather_data(self, location: Dict):
        """Charge les données météo selon la localisation"""
        self.weather_data = pvgis_client.fetch(
            lat=location['lat'],
            lon=location['lon']
        )

    def _calculate_pv_production(self, system: Dict, location: Dict):
        """Simule la production solaire"""
        self.pv_production = pvlib_wrapper.simulate(
            weather=self.weather_data,
            tilt=location['tilt'],
            azimuth=location['azimuth'],
            power_kw=system['power_kw']
        )

    def _calculate_consumption(self, appliances: List, household: Dict):
        """Calcule la consommation électrique"""
        self.consumption = appliance_models.simulate(
            appliances=appliances,
            dpe=household['dpe'],
            occupants=household['occupants']
        )

    def _generate_results(self) -> Dict:
        """Compile les résultats finaux"""
        return {
            "production": self.pv_production,
            "consumption": self.consumption,
            "economics": roi_calculator.analyze(
                pv_production=self.pv_production,
                consumption=self.consumption
            )
        }
