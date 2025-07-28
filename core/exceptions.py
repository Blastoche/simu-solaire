# -*- coding: utf-8 -*-
"""
Gestion centralisée des erreurs métier
"""

class SolarSimulatorError(Exception):
    """Classe de base pour les erreurs métier"""
    pass

class WeatherDataError(SolarSimulatorError):
    """Erreur de récupération des données météo"""
    def __init__(self, message="Erreur lors de la récupération des données météo"):
        self.message = message
        super().__init__(self.message)

class PVCalculationError(SolarSimulatorError):
    """Erreur dans le calcul PV"""
    pass
