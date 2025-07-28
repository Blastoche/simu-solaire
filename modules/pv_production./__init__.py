# -*- coding: utf-8 -*-
"""
Interface publique du module PV Production.
Expose uniquement les fonctions nécessaires.
"""
from .pvlib_wrapper import (
    simulate_pv_system,
    estimate_energy_yield
)
from .shading import (
    calculate_shading_losses,
    apply_shading_correction
)

__all__ = [
    'simulate_pv_system',
    'estimate_energy_yield',
    'calculate_shading_losses'
]
