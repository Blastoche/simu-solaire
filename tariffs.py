# Tarifs officiels 2025
TARIFFS = {
    "electricity": {
        "purchase": 0.20,          # €/kWh acheté
        "surplus_sell": {          # Tarifs de rachat
            "≤3kWc": 0.04,
            "3-9kWc": 0.04,
            "9-36kWc": 0.0731
        }
    },
    "subsidies": {
        "autoconsommation": {      # Prime à l'installation
            "≤3kWc": 80,
            "3-9kWc": 80,
            "9-36kWc": 180
        },
        "tva_reduced": 0.10        # TVA réduite
    },
    "installation_cost": {         # €/kWc
        "1-3kWc": 2500,
        "3-9kWc": 2200
    }
}
