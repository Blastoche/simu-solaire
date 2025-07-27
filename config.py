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
# -*- coding: utf-8 -*-
"""
Profils de consommation des appareils électriques (données 2025)
Sources : ADEME, UFC-Que Choisir, fabricants
"""

APPLIANCES = {
    # ---------------------------------------------------
    # 1. GROS ÉLECTROMÉNAGER (USAGE PONCTUEL)
    # ---------------------------------------------------
    "heavy_usage": {
        "Machine à laver": {
            "power_kw": 1.2,      # Puissance moyenne (cycle standard)
            "eco_power_kw": 0.8,   # Puissance en mode éco
            "usage_weekly": 4,     # Nombre moyen d'utilisations
            "duration_hours": 1.8, # Durée moyenne (h)
            "standby_w": 1.5       # Veille (W)
        },
        "Sèche-linge": {
            "power_kw": 2.8,      # Résistance
            "heat_pump_kw": 1.2,  # Si modèle pompe à chaleur
            "usage_weekly": 3,
            "duration_hours": 2.5
        },
        "Lave-vaisselle": {
            "power_kw": 1.5,
            "eco_power_kw": 0.9,
            "usage_weekly": 5,
            "duration_hours": 1.5
        }
    },

    # ---------------------------------------------------
    # 2. ÉLECTROMÉNAGER CONTINU
    # ---------------------------------------------------
    "continuous": {
        "Réfrigérateur": {
            "class_A+": {"power_kw": 0.10, "hours_day": 24},
            "class_A++": {"power_kw": 0.07, "hours_day": 24},
            "américain": {"power_kw": 0.25, "hours_day": 24}
        },
        "Congélateur": {
            "coffre": {"power_kw": 0.12, "hours_day": 24},
            "armoire": {"power_kw": 0.15, "hours_day": 24}
        }
    },

    # ---------------------------------------------------
    # 3. PETIT ÉLECTROMÉNAGER
    # ---------------------------------------------------
    "small_appliances": {
        "Multimédia": {
            "Box internet": {"power_kw": 0.015, "hours_day": 24},
            "TV LED 55\"": {"power_kw": 0.12, "hours_day": 4},
            "PC portable": {"power_kw": 0.06, "hours_day": 6}
        },
        "Cuisine": {
            "Grille-pain": {"power_kw": 1.2, "duration_mins": 5, "usage_weekly": 3},
            "Bouilloire": {"power_kw": 2.0, "duration_mins": 4, "usage_weekly": 7}
        }
    },

    # ---------------------------------------------------
    # 4. CHAUFFAGE/CLIM
    # ---------------------------------------------------
    "thermal": {
        "Radiateur électrique": {
            "1000W": {"power_kw": 1.0, "usage_hours_day": 8},
            "2000W": {"power_kw": 2.0, "usage_hours_day": 6}
        },
        "Climatisation": {
            "split_12000BTU": {"power_kw": 1.2, "usage_hours_day": 5},
            "inverter": {"power_kw": 0.8, "usage_hours_day": 7}
        }
    }
}

# ---------------------------------------------------
# FONCTIONS UTILITAIRES
# ---------------------------------------------------
def get_appliance_consumption(appliance_type: str, model: str = None) -> dict:
    """Retourne la consommation d'un appareil avec gestion des sous-catégories."""
    for category in APPLIANCES.values():
        if appliance_type in category:
            if model and isinstance(category[appliance_type], dict):
                return category[appliance_type].get(model, category[appliance_type])
            return category[appliance_type]
    return {}

def estimate_yearly_consumption(appliance_data: dict) -> float:
    """Calcule la consommation annuelle en kWh."""
    if "hours_day" in appliance_data:  # Appareil continu
        return appliance_data["power_kw"] * appliance_data["hours_day"] * 365
    else:  # Appareil ponctuel
        return (appliance_data["power_kw"] * 
                appliance_data.get("duration_hours", 1) * 
                appliance_data["usage_weekly"] * 52)
        
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

