# solar_simulator/modules/consumption.py
import numpy as np
from typing import List, Dict

class ConsumptionSimulator:
    def __init__(self, appliances: List[Dict]):
        self.appliances = appliances
        self.hours_per_year = 8760
    
    def run(self) -> Dict:
        """Génère le profil de consommation annuel"""
        hourly_consumption = np.zeros(self.hours_per_year)
        
        for app in self.appliances:
            profile = self._generate_appliance_profile(app)
            hourly_consumption += profile
        
        return {
            "hourly": hourly_consumption,
            "daily": self._aggregate_daily(hourly_consumption)
        }
    
    def _generate_appliance_profile(self, appliance: Dict) -> np.array:
        """Crée un profil horaire pour un appareil"""
        profile = np.zeros(self.hours_per_year)
        model = appliance["model"]
        power = APPLIANCE_DEFAULTS[appliance["name"]]["models"][model]
        
        # Application du planning
        for week in range(52):
            for (start, end) in appliance["schedule"]:
                day = self._select_usage_day(week)
                start_hour = int(day * 24 + start)
                end_hour = int(day * 24 + end)
                profile[start_hour:end_hour] = power["eco_power"] if appliance["eco_mode"] else power["power"]
        
        return profile
    
    def _select_usage_day(self, week: int) -> int:
        """Répartit les utilisations sur la semaine"""
        # Algorithme de répartition réaliste
        base_day = (week * 3) % 7  # Variation sur l'année
        return min(base_day, 6)  # 0=lundi, 6=dimanche
