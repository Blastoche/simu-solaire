# -*- coding: utf-8 -*-
"""
Gestion du cache mémoire et disque pour les simulations PV
"""
import hashlib
import json
from functools import lru_cache
import pandas as pd
import os
from pathlib import Path
from core.exceptions import PVCalculationError
from .caching import hash_parameters, cached_simulation_memory, save_to_cache

CACHE_DIR = Path("cache/pv_production")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def hash_parameters(params: dict) -> str:
    """Génère un hash unique pour les paramètres de simulation"""
    return hashlib.md5(
        json.dumps(params, sort_keys=True).encode()
    ).hexdigest()

@lru_cache(maxsize=128)
def cached_simulation_memory(params_hash: str) -> dict:
    """
    Cache mémoire (LRU) - Max 128 simulations récentes
    Charge depuis le cache disque si nécessaire
    """
    cache_file = CACHE_DIR / f"{params_hash}.parquet"
    if cache_file.exists():
        try:
            df = pd.read_parquet(cache_file)
            return {
                "hourly": df["production_kw"],
                "annual_yield": df["production_kw"].sum(),
                "cached": True
            }
        except Exception as e:
            raise PVCalculationError(f"Cache read error: {str(e)}")
    raise ValueError("Cache miss")

def save_to_cache(params_hash: str, results: dict):
    """
    Sauvegarde les résultats en cache disque (Parquet)
    et les garde en mémoire via LRU
    """
    cache_file = CACHE_DIR / f"{params_hash}.parquet"
    try:
        pd.DataFrame({
            "production_kw": results["hourly"]
        }).to_parquet(cache_file)
    except Exception as e:
        raise PVCalculationError(f"Cache write error: {str(e)}")
