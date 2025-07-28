from config.tariffs import TARIFFS

class FinancialAnalyzer:
    def __init__(self, pv_production: dict, consumption: dict):
        """
        Args:
            pv_production: {"hourly": pd.Series, "annual_kwh": float}
            consumption: {"hourly": pd.Series, "annual_kwh": float}
        """
        self.pv = pv_production
        self.conso = consumption

    def analyze(self) -> dict:
        """Calcule tous les indicateurs financiers"""
        # 1. Autoconsommation
        autoconsommation = np.minimum(self.pv["hourly"], self.conso["hourly"])
        
        # 2. Calculs annuels
        return {
            "autoconsommation_rate": autoconsommation.sum() / self.pv["annual_kwh"],
            "savings": {
                "direct": autoconsommation.sum() * TARIFFS["electricity"]["purchase"],
                "surplus": (self.pv["annual_kwh"] - autoconsommation.sum()) * self._get_surplus_tariff()
            },
            "roi": self._calculate_roi()
        }

    def _get_surplus_tariff(self) -> float:
        """Retourne le tarif de rachat selon la puissance"""
        if self.pv["power_kw"] <= 3:
            return TARIFFS["electricity"]["surplus_sell"]["≤3kWc"]
        else:
            return TARIFFS["electricity"]["surplus_sell"]["3-9kWc"]
            
    def _calculate_roi(self):
        investment = self.pv["power_kw"] * self.tariffs["pv_cost_per_kw"]
        annual_savings = self._get_annual_savings()
        return investment / annual_savings
