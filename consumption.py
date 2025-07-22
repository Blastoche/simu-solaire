class HouseholdConsumption:
    def __init__(self, household_params):
        self.params = household_params
    
    def calculate(self):
        """Calcule la consommation totale en kWh/an."""
        return {
            "total": self._calculate_total(),
            "breakdown": self._get_breakdown()
        }
    
    def _calculate_total(self):
        # Logique de calcul détaillé
        total = 0
        for appliance in self.params["appliances"]:
            total += appliance["power"] * appliance["usage"]
        return total
    
    def _get_breakdown(self):
        # Retourne un détail par poste (chauffage, ECS, etc.)
        return {...}
