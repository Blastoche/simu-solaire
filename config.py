# -*- coding: utf-8 -*-
"""
Configuration actualisée 2025 - Sources officielles (photovoltaique.info + CRE)
Dernière vérification : juillet 2025
"""

TARIFFS = {
    # ---------------------------------------------------
    # 1. TARIFS ÉLECTRICITÉ (€)
    # ---------------------------------------------------
    "electricity": {
        "purchase_price": 0.20,  # Prix moyen TTC du kWh acheté
        "evolution_rate": 0.03,  # Taux d'augmentation annuel
        "subscription": {        # Coûts fixes (€/an)
            "6kVA": 120,
            "9kVA": 150
        }
    },
    
    # ---------------------------------------------------
    # 2. TARIFS DE RACHAT (€/kWh)
    # ---------------------------------------------------
    "surplus": {
        "residential": {
            "≤3kWc": 0.04,
            "3-9kWc": 0.04,
            "9-36kWc": 0.0731,
            "36-100kWc": 0.0731
        },
        "collective": {  # Ajout pour les projets collectifs
            "≤3kWc": 0.10,
            "3-36kWc": 0.08
        }
    },
    
    # ---------------------------------------------------
    # 3. AIDES & FINANCEMENT (€)
    # ---------------------------------------------------
    "subsidies": {
        "autoconsommation": {
            "≤3kWc": 80,
            "3-9kWc": 80,
            "9-36kWc": 180,
            "36-100kWc": 90
        },
        "local_bonus": {  # Primes locales optionnelles
            "Île-de-France": 200,
            "Occitanie": 150
        },
        "tva_reduced": 0.10  # Applicable ≤3kWc
    },
    
    # ---------------------------------------------------
    # 4. COÛTS D'INSTALLATION (€)
    # ---------------------------------------------------
    "costs": {
        "pv": {
            "≤3kWc": 2500,
            "3-9kWc": 2200,
            "9-36kWc": 1800,
            "battery_surcharge": 0.15  # % supplémentaire
        },
        "battery": {
            "lithium": {
                "price_per_kwh": 600,
                "lifespan": 10,  # années
                "warranty": 5     # années garantie
            }
        }
    }
}

# ---------------------------------------------------
# FONCTIONS UTILITAIRES
# ---------------------------------------------------
def get_surplus_tariff(pv_power: float, is_collective: bool = False) -> float:
    """Retourne le tarif de rachat adapté au projet."""
    tariff_table = TARIFFS["surplus"]["collective"] if is_collective else TARIFFS["surplus"]["residential"]
    
    if pv_power <= 3:
        return tariff_table["≤3kWc"]
    elif 3 < pv_power <= 9:
        return tariff_table.get("3-9kWc", tariff_table["≤3kWc"])  # Fallback sécurisé
    elif 9 < pv_power <= 36:
        return tariff_table["9-36kWc"]
    else:
        return tariff_table.get("36-100kWc", 0)  # Retourne 0 si non éligible

def estimate_installation_cost(pv_power: float, battery_size: float = 0) -> dict:
    """Calcule le devis détaillé."""
    costs = TARIFFS["costs"]
    
    # Coût PV de base
    if pv_power <= 3:
        pv_cost = pv_power * costs["pv"]["≤3kWc"]
    elif 3 < pv_power <= 9:
        pv_cost = pv_power * costs["pv"]["3-9kWc"]
    else:
        pv_cost = pv_power * costs["pv"]["9-36kWc"]
    
    # Coût batterie
    battery_cost = battery_size * costs["battery"]["lithium"]["price_per_kwh"]
    
    return {
        "pv": pv_cost,
        "battery": battery_cost,
        "total": pv_cost * (1 + costs["pv"]["battery_surcharge"]) + battery_cost
    }
