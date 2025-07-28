# -*- coding: utf-8 -*-
"""
Calcul des indicateurs économiques
"""
from config.tariffs import TARIFFS

class FinancialAnalyzer:
    def __init__(self, pv_production: dict, consumption: dict, pv_power: float):
        self.pv = pv_production
        self.conso = consumption
        self.pv_power = pv_power

    def analyze(self) -> dict:
        autoconsommation = np.minimum(self.pv["hourly"], self.conso["hourly"])
        return {
            "autoconsommation_rate": autoconsommation.sum() / self.pv["annual_kwh"],
            "roi_years": self._calculate_roi(),
            "subsidies": self._calculate_subsidies()
        }

    def _calculate_roi(self) -> float:
        cost = self.pv_power * TARIFFS["installation_cost"]
        savings = autoconsommation.sum() * TARIFFS["electricity"]["purchase"]
        return cost / savings
