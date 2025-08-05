# Test rapide - créez un fichier test_pv.py à la racine
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from modules.pv_production.pvlib_wrapper import simulate_pv_system
    import pandas as pd
    
    # Test minimal
    location = {'lat': 48.8, 'lon': 2.3}
    system = {'power_kw': 3.0}
    weather = pd.DataFrame({'ghi': [100] * 24})
    
    result = simulate_pv_system(location, system, weather, use_simple_model=True)
    print("✅ Test réussi:", result['annual_yield_kwh'])
    
except Exception as e:
    print("❌ Erreur:", str(e))
    import traceback
    traceback.print_exc()
