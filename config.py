# -*- coding: utf-8 -*-
"""
Configuration actualisée avec les tarifs 2025 (source : photovoltaique.info)
Dernière vérification : juillet 2025
"""

# -------------------------------
# 1. TARIFS OFFICIELS 2025 (€)
# -------------------------------
TARIFFS = {
    # Électricité achetée (moyenne nationale)
    "electricity": {
        "residential": 0.20,  # Prix moyen TTC (hors abonnement)
        "evolution_rate": 0.03  # Taux d'augmentation annuel estimé
    },
    
    # Vente du surplus (tarifs EDF OA Juin 2025)
    "surplus_sell": {
        "<=3_kWc": 0.04,  # Toutes orientations, €/kWh
        "3_9_kWc": 0.04,
        "9_36_kWc": 0.0731,
        "36_100_kWc": 0.0731
    },
    
    # Coûts d'installation (moyenne marché 2024)
    "installation_costs": {
        "pv": {
            "residential": {
                "1_3_kWc": 2500,  # €/kWc
                "3_9_kWc": 2200,
                "9_36_kWc": 1800
            },
            "battery_included": 0.15  # Surcoût si batterie intégrée (%)
        },
        "battery": {
            "lithium": 600,  # €/kWh (capacité utile)
            "lifecycle": 6000  # Nombre de cycles typiques
        }
    },
    
    # Aides financières (2025)
    "subsidies": {
        "prime_autoconsommation": {  # Prime à l'installation (€/kWc)
            "0_3_kWc": 80,
            "3_9_kWc": 80,
            "9_36_kWc": 180,
            "36_100_kWc": 90
        },
        "tva_reduced": 0.10  # TVA à 10% pour <3kWc
    }
}

# -------------------------------
# 2. EXEMPLES DE CALCUL AUTOMATISÉ
# -------------------------------
def get_surplus_tariff(pv_power_kWc):
    """Retourne le tarif de rachat selon la puissance installée."""
    if pv_power_kWc <= 3:
        return TARIFFS["surplus_sell"]["<=3_kWc"]
    elif 3 < pv_power_kWc <= 9:
        return TARIFFS["surplus_sell"]["3_9_kWc"]
    # [...] autres tranches

def get_installation_cost(pv_power_kWc, with_battery=False):
    """Calcule le coût total d'installation."""
    if pv_power_kWc <= 3:
        base_cost = pv_power_kWc * TARIFFS["installation_costs"]["pv"]["residential"]["1_3_kWc"]
    elif 3 < pv_power_kWc <= 9:
        base_cost = pv_power_kWc * TARIFFS["installation_costs"]["pv"]["residential"]["3_9_kWc"]
    # [...] autres tranches
    
    if with_battery:
        base_cost *= (1 + TARIFFS["installation_costs"]["pv"]["battery_included"])
    
    return base_cost
