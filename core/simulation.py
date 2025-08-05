# -*- coding: utf-8 -*-
"""
Noyau principal de simulation - VERSION CORRIGÉE AVEC SUPPORT MODÈLE SIMPLE
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
            raise SimulationError(f"
