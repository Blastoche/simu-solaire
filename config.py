# Tarifs et coûts
TARIFS = {
    "electricity": 0.20,       # €/kWh
    "surplus_sell": 0.04,      # €/kWh
    "pv_cost_per_kw": 2500,    # €/kWc
    "autoconsumption_bonus": { # Prime à l'autoconsommation
        "<=3": 500,
        ">3": 0
    }
}

# Données par défaut
DEFAULT_APPLIANCES = {
    "gros_usage": {
        "Machine à laver": {"power": 1.0, "usage_weekly": 3},
        "Sèche-linge": {"power": 2.5, "usage_weekly": 2}
    },
    "petit_usage": {
        "Box internet": {"power": 0.01, "hours_day": 24}
    }
}
