import pvlib

class PVSystem:
    def __init__(self, location, system_params):
        self.location = location
        self.params = system_params
    
    def calculate(self):
        """Calcule la production PV avec pvlib."""
        system = self._setup_pvsystem()
        weather = self._get_weather_data()
        return self._simulate(system, weather)
    
    def _setup_pvsystem(self):
        return pvlib.pvsystem.PVSystem(
            module_parameters={"pdc0": self.params["power_kw"] * 1000},
            inverter_parameters={...},
            surface_tilt=self.params["tilt"],
            surface_azimuth=self.params["azimuth"]
        )
