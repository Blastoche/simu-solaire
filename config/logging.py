# -*- coding: utf-8 -*-
"""
Configuration du système de logging
"""
import logging
import sys
from pathlib import Path

def setup_logging(level=logging.INFO, log_file=None):
    """Configure le système de logging"""
    
    # Format des messages
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configuration du logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Handler fichier optionnel
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger
    
# Initialisation par défaut
setup_logging(level=logging.INFO, log_file="logs/solar_simulator.log")
