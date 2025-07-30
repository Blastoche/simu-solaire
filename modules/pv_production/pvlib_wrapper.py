from .database import DatabaseManager
from .caching import hash_parameters
import logging

# Initialisation
db_manager = DatabaseManager()
logger = logging.getLogger(__name__)

def _original_pv_calculation(location: dict, system: dict, weather: pd.DataFrame) -> dict:
    """Calcul PV original (fonction manquante dans votre code)"""
    return simulate_pv_system(location, system, weather, use_cache=False)

def simulate_pv_system(
    location: dict,
    system: dict,
    weather: pd.DataFrame,
    use_cache: bool = True,
    use_db: bool = True,
    **kwargs
) -> dict:
    """
    Version finale avec cache + SGBD
    """
    # Génération du hash unique
    params = {
        "location": location,
        "system": system,
        "weather_hash": hash_parameters(weather.mean().to_dict())
    }
    params_hash = hash_parameters(params)

    # 1. Vérification du cache mémoire
    if use_cache:
        try:
            cached = cached_simulation_memory(params_hash)
            logger.info("Cache mémoire hit")
            return cached
        except ValueError:
            pass  # Cache miss

    # 2. Vérification de la base de données
    if use_db:
        db_results = db_manager.get_simulation(params_hash)
        if db_results:
            logger.info("Cache SGBD hit")
            save_to_cache(params_hash, db_results)  # Mise en cache mémoire
            return db_results

    # 3. Calcul complet si aucun cache
    try:
        results = _original_pv_calculation(location, system, weather)
        
        # Sauvegarde dans les systèmes de cache
        if use_cache:
            save_to_cache(params_hash, results)
        
        if use_db:
            db_manager.save_simulation(params_hash, params, results)
        
        return results

    except Exception as e:
        logger.error(f"Erreur de simulation : {str(e)}")
        raise
