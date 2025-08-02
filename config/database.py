# -*- coding: utf-8 -*-
"""
Configuration de la base de données
"""
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///solar_simulator.db"  # Fallback SQLite
)

# Paramètres optionnels
DB_PARAMS = {
    "pool_size": 5,
    "max_overflow": 10,
    "echo": False  # Active le logging SQL (désactivé en prod)
}
