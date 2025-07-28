from .caching import hash_parameters, cached_simulation_memory, save_to_cache
import logging

logger = logging.getLogger(__name__)

def simulate_pv_system(
    location: dict,
    system: dict,
    weather: pd.DataFrame,
    use_cache: bool = True,
    **kwargs
) -> dict:
    """
    Version avec cache et logging
    """
    # Génération de la signature unique
    params = {
        "location": location,
        "system": system,
        "weather_hash": hash_parameters(weather.mean().to_dict())
    }
    params_hash = hash_parameters(params)

    # 1. Vérification du cache
    if use_cache:
        try:
            cached = cached_simulation_memory(params_hash)
            logger.info(f"Using cached results for {params_hash}")
            return cached
        except ValueError:
            pass  # Cache miss, continuer

    # 2. Calcul complet si cache miss
    try:
        results = _original_pv_calculation(location, system, weather)
        
        # Sauvegarde dans le cache
        if use_cache:
            save_to_cache(params_hash, results)
            logger.info(f"Saved to cache: {params_hash}")
        
        return results

    except Exception as e:
        logger.error(f"Simulation failed: {str(e)}")
        raise

def _original_pv_calculation(location, system, weather):
    """Version originale des calculs (isolée pour clarté)"""
    # [...] (Le code PVLib précédent)
