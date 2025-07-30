# -*- coding: utf-8 -*-
"""
Noyau principal de simulation - Indépendant de l'UI
"""
from typing import Dict, List
import pandas as pd
# -*- coding: utf-8 -*-
"""
Noyau principal de simulation - Indépendant de l'UI
"""
from typing import Dict, List
import pandas as pd
from modules.weather import get_weather_data
from modules.pv_production import simulate_pv_system, estimate_energy_yield
from modules.consumption.appliance_models import simulate as simulate_consumption
from modules.economics.roi_calculator import analyze as analyze_economics

class SimulationEngine:
    def __init__(self):
        self.weather_data = None
        self.pv_production = None
        self.consumption = None

    def run(self, params: Dict) -> Dict:
        """Exécute la simulation complète - VERSION CORRIGÉE"""
        try:
            # 1. Données météo avec gestion d'erreur
            weather_response = get_weather_data(
                lat=params['location']['lat'],
                lon=params['location']['lon'],
                use_mock=params.get('use_mock_weather', False)
            )
            self.weather_data = weather_response['data']
            
            # 2. Production PV
            self.pv_production = simulate_pv_system(
                location=params['location'],
                system=params['pv_system'],
                weather=self.weather_data
            )
            
            # 3. Consommation
            self.consumption = simulate_consumption(
                appliances=params['appliances'],
                dpe=params['household']['dpe'],
                occupants=params['household']['occupants'],
                surface=params['household'].get('surface', 100)
            )
            
            # 4. Analyse économique
            economics = analyze_economics(
                pv_production=self.pv_production,
                consumption=self.consumption,
                investment_cost=params.get('investment_cost'),
                tariffs=params.get('tariffs')
            )
            
            return {
                "production": self.pv_production,
                "consumption": self.consumption,
                "economics": economics,
                "weather_source": weather_response['source'],
                "warning": weather_response.get('warning')
            }
            
        except Exception as e:
            logger.error(f"Erreur simulation: {str(e)}")
            raise SimulationError(f"Échec de la simulation: {str(e)}")

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
