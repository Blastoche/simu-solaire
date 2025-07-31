# -*- coding: utf-8 -*-
"""
Noyau principal de simulation - VERSION CORRIGÉE
"""
from typing import Dict, List
import pandas as pd
import logging

from modules.weather import get_weather_data
from modules.pv_production import simulate_pv_system, estimate_energy_yield
from modules.consumption import simulate as simulate_consumption
from modules.economics import analyze as analyze_economics
from core.exceptions import SolarSimulatorError

logger = logging.getLogger(__name__)

class SimulationError(SolarSimulatorError):
    """Erreur spécifique à la simulation"""
    pass

class SimulationEngine:
    """
    Moteur de simulation principal - Indépendant de l'UI
    """
    
    def __init__(self):
        self.weather_data = None
        self.pv_production = None
        self.consumption = None
        self._validation_errors = []

    def run(self, params: Dict) -> Dict:
        """
        Exécute la simulation complète
        
        Args:
            params: Paramètres de simulation validés
            
        Returns:
            Dict avec tous les résultats
            
        Raises:
            SimulationError: En cas d'erreur de simulation
        """
        try:
            logger.info("Début de la simulation")
            
            # Validation des paramètres d'entrée
            self._validate_params(params)
            
            # 1. Récupération des données météo
            logger.info("Récupération données météo...")
            weather_response = self._fetch_weather_data(params)
            
            # 2. Calcul de la production PV
            logger.info("Calcul production solaire...")
            self.pv_production = self._calculate_pv_production(params, weather_response)
            
            # 3. Simulation de la consommation
            logger.info("Simulation consommation...")
            self.consumption = self._calculate_consumption(params)
            
            # 4. Analyse économique
            logger.info("Analyse économique...")
            economics = self._perform_economic_analysis(params)
            
            # 5. Compilation des résultats finaux
            results = self._compile_results(weather_response, economics)
            
            logger.info("Simulation terminée avec succès")
            return results
            
        except Exception as e:
            logger.error(f"Erreur simulation: {str(e)}", exc_info=True)
            raise SimulationError(f"Échec de la simulation: {str(e)}")

    def _validate_params(self, params: Dict):
        """Valide les paramètres de simulation"""
        required_keys = ['location', 'pv_system', 'household']
        missing_keys = [key for key in required_keys if key not in params]
        
        if missing_keys:
            raise SimulationError(f"Paramètres manquants: {missing_keys}")
        
        # Validation spécifique
        location = params['location']
        if not (-90 <= location.get('lat', 0) <= 90):
            raise SimulationError(f"Latitude invalide: {location.get('lat')}")
        
        if not (-180 <= location.get('lon', 0) <= 180):
            raise SimulationError(f"Longitude invalide: {location.get('lon')}")
        
        pv_system = params['pv_system']
        if pv_system.get('power_kw', 0) <= 0:
            raise SimulationError(f"Puissance PV invalide: {pv_system.get('power_kw')}")

    def _fetch_weather_data(self, params: Dict) -> Dict:
        """Récupère les données météorologiques"""
        try:
            location = params['location']
            use_mock = params.get('use_mock_weather', False)
            
            weather_response = get_weather_data(
                lat=location['lat'],
                lon=location['lon'],
                use_mock=use_mock
            )
            
            self.weather_data = weather_response['data']
            
            if self.weather_data is None or self.weather_data.empty:
                raise SimulationError("Données météo vides ou invalides")
            
            return weather_response
            
        except Exception as e:
            logger.error(f"Erreur récupération météo: {str(e)}")
            raise SimulationError(f"Impossible de récupérer les données météo: {str(e)}")

    def _calculate_pv_production(self, params: Dict, weather_response: Dict) -> Dict:
        """Calcule la production photovoltaïque"""
        try:
            production_results = simulate_pv_system(
                location=params['location'],
                system=params['pv_system'],
                weather=self.weather_data,
                use_cache=params.get('use_cache', True),
                use_db=params.get('use_db', True)
            )
            
            # Validation des résultats
            if not production_results or 'annual_yield_kwh' not in production_results:
                raise SimulationError("Résultats de production PV invalides")
            
            return production_results
            
        except Exception as e:
            logger.error(f"Erreur calcul production PV: {str(e)}")
            raise SimulationError(f"Calcul de production PV échoué: {str(e)}")

    def _calculate_consumption(self, params: Dict) -> Dict:
        """Calcule la consommation électrique"""
        try:
            household = params['household']
            appliances = params.get('appliances', [])
            
            consumption_results = simulate_consumption(
                appliances=appliances,
                dpe=household['dpe'],
                occupants=household['occupants'],
                surface=household.get('surface', 100)
            )
            
            # Validation des résultats
            if not consumption_results or 'consumption_kw' not in consumption_results:
                raise SimulationError("Résultats de consommation invalides")
            
            return consumption_results
            
        except Exception as e:
            logger.error(f"Erreur calcul consommation: {str(e)}")
            raise SimulationError(f"Simulation de consommation échouée: {str(e)}")

    def _perform_economic_analysis(self, params: Dict) -> Dict:
        """Effectue l'analyse économique"""
        try:
            economics_results = analyze_economics(
                pv_production=self.pv_production,
                consumption=self.consumption,
                investment_cost=params.get('investment_cost'),
                tariffs=params.get('tariffs'),
                system_power_kw=params['pv_system'].get('power_kw')
            )
            
            return economics_results
            
        except Exception as e:
            logger.warning(f"Erreur analyse économique: {str(e)}")
            # L'analyse économique n'est pas critique, on retourne des valeurs par défaut
            return {
                'autoconsumption_rate': 0.0,
                'autonomy_rate': 0.0,
                'annual_savings': 0.0,
                'roi_years': float('inf'),
                'error': 'Analyse économique indisponible'
            }

    def _compile_results(self, weather_response: Dict, economics: Dict) -> Dict:
        """Compile tous les résultats en un dictionnaire final"""
        return {
            "production": self.pv_production,
            "consumption": self.consumption,
            "economics": economics,
            "weather_source": weather_response.get('source', 'Unknown'),
            "warning": weather_response.get('warning'),
            "simulation_metadata": {
                "weather_data_points": len(self.weather_data) if self.weather_data is not None else 0,
                "production_data_points": len(self.pv_production.get('hourly_production_kw', [])),
                "consumption_data_points": len(self.consumption.get('consumption_kw', [])),
            }
        }

    def get_simulation_summary(self) -> Dict:
        """Retourne un résumé de la dernière simulation"""
        if not all([self.weather_data, self.pv_production, self.consumption]):
            return {"status": "No simulation completed"}
        
        return {
            "status": "Completed",
            "annual_production_kwh": self.pv_production.get('annual_yield_kwh', 0),
            "annual_consumption_kwh": self.consumption.get('annual_consumption_kwh', 0),
            "weather_data_source": "Real" if self.weather_data is not None else "Mock"
        }
