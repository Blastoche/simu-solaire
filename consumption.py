# -*- coding: utf-8 -*-
"""
Modélisation de la consommation électrique
"""
import numpy as np
import pandas as pd
from config.appliances import APPLIANCES

class ConsumptionSimulator:
    def __init__(self, appliances: list, dpe: str, occupants: int):
        self.appliances = appliances  # Liste des appareils
        self.dpe_coeff = {"A": 20, "B": 25, ...}[dpe]  # kW/m²/an
        self.occupants = occupants

    def calculate(self) -> dict:
        """Génère un profil horaire sur 1 an"""
        base_load = self._calculate_dpe_load()
        appliance_load = self._calculate_appliances_load()
        return {
            "hourly": base_load + appliance_load,
            "annual_kwh": (base_load + appliance_load).sum()
        }

    def _calculate_appliances_load(self) -> np.array:
        """Calcule la charge des appareils"""
        load = np.zeros(8760)  # 1 année en heures
        for app in self.appliances:
            profile = self._generate_profile(app)
            load += profile
        return load
