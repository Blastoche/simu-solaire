class FinancialAnalysis:
    def __init__(self, consumption, pv_production, tariffs):
        self.conso = consumption
        self.pv = pv_production
        self.tariffs = tariffs
    
    def analyze(self):
        return {
            "roi_years": self._calculate_roi(),
            "cashflow": self._generate_cashflow()
        }
    
    def _calculate_roi(self):
        investment = self.pv["power_kw"] * self.tariffs["pv_cost_per_kw"]
        annual_savings = self._get_annual_savings()
        return investment / annual_savings
