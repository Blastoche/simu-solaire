# -*- coding: utf-8 -*-
"""
Tarifs et aides financières (2025)
Source : photovoltaique.info
"""

TARIFFS = {
    "electricity": {
        "purchase": 0.20,  # €/kWh
        "sell": {
            "≤3kWc": 0.04,
            "3-9kWc": 0.04,
            "9-36kWc": 0.0731
        }
    },
    "subsidies": {
        "autoconsommation": {  # €/kWc
            "≤3kWc": 80,
            "3-9kWc": 80
        },
        "tva_reduced": 0.10  # TVA à 10%
    }
}

    "installation_cost": {         # €/kWc
        "1-3kWc": 2500,
        "3-9kWc": 2200
    }
}
