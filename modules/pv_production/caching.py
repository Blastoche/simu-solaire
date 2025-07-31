# -*- coding: utf-8 -*-
"""
Gestion du cache mémoire et disque pour les simulations PV - VERSION CORRIGÉE
"""
import hashlib
import json
from functools import lru_cache
import pandas as pd
import os
from pathlib import Path
from core.exceptions import PVCalculationError

CACHE_DIR = Path("cache/pv_production")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def hash_parameters(params: dict) -> str:
    """Génère un hash unique pour les paramètres de simulation"""
    return hashlib.md5(
        json.dumps(params, sort_keys=True).encode()
    ).hexdigest()

# Cache mémoire global - dictionnaire simple pour éviter les problèmes LRU
_memory_cache = {}
_cache_max_size = 128

@lru_cache(maxsize=128)
def cached_simulation_memory(params_hash: str) -> dict:
    """
    Cache mémoire (LRU) - Max 128 simulations récentes
    Charge depuis le cache disque si nécessaire
    """
    # Vérification cache mémoire direct
    if params_hash in _memory_cache:
        return _memory_cache[params_hash]
    
    # Tentative de chargement depuis le disque
    cache_file = CACHE_DIR / f"{params_hash}.parquet"
    if cache_file.exists():
        try:
            df = pd.read_parquet(cache_file)
            result = {
                "hourly_production_kw": df["production_kw"],
                "annual_yield_kwh": float(df["production_kw"].sum()),
                "cached": True
            }
            
            # Sauvegarde en mémoire pour les prochains accès
            _add_to_memory_cache(params_hash, result)
            return result
            
        except Exception as e:
            raise PVCalculationError(f"Cache read error: {str(e)}")
    
    raise ValueError("Cache miss")

def save_to_cache(params_hash: str, results: dict):
    """
    Sauvegarde les résultats en cache disque (Parquet)
    et les garde en mémoire
    """
    try:
        # Sauvegarde disque
        cache_file = CACHE_DIR / f"{params_hash}.parquet"
        
        # Conversion de la série horaire en DataFrame
        hourly_data = results.get('hourly_production_kw', pd.Series())
        if isinstance(hourly_data, pd.Series):
            df = pd.DataFrame({"production_kw": hourly_data})
        else:
            df = pd.DataFrame({"production_kw": pd.Series(hourly_data)})
        
        df.to_parquet(cache_file)
        
        # Sauvegarde mémoire
        _add_to_memory_cache(params_hash, results)
        
    except Exception as e:
        raise PVCalculationError(f"Cache write error: {str(e)}")

def _add_to_memory_cache(params_hash: str, results: dict):
    """Ajoute un résultat au cache mémoire avec gestion de la taille"""
    global _memory_cache
    
    # Nettoyage si cache plein
    if len(_memory_cache) >= _cache_max_size:
        # Supprime le plus ancien (FIFO simple)
        oldest_key = next(iter(_memory_cache))
        del _memory_cache[oldest_key]
    
    _memory_cache[params_hash] = results

def clear_cache():
    """Vide tous les caches"""
    global _memory_cache
    _memory_cache.clear()
    
    # Suppression des fichiers cache
    for cache_file in CACHE_DIR.glob("*.parquet"):
        try:
            cache_file.unlink()
        except OSError:
            pass

def get_cache_stats() -> dict:
    """Retourne les statistiques du cache"""
    disk_files = len(list(CACHE_DIR.glob("*.parquet")))
    memory_entries = len(_memory_cache)
    
    return {
        "memory_entries": memory_entries,
        "disk_files": disk_files,
        "cache_dir_size_mb": sum(f.stat().st_size for f in CACHE_DIR.glob("*.parquet")) / 1024 / 1024
    }
