# -*- coding: utf-8 -*-
"""
Profils techniques des appareils électroménagers
Sources : ADEME, fabricants
"""

APPLIANCES = {
    # Gros électroménager
    "heavy_usage": {
        "Machine à laver": {
            "Classique": {
                "power_kw": 1.2,
                "duration_hours": 1.8,
                "usage_profile": {
                    "weekday": [0, 0, 0, 0, 0, 0, 0.2, 0.4, 0.3, 0.1, 0, 0, 0, 0, 0.5, 0.8, 0.7, 0.3, 0, 0, 0, 0, 0, 0],
                    "weekend": [0]*10 + [0.3, 0.5, 0.7, 0.6, 0.4, 0.2] + [0]*8
                }
            }
        }
    },

    # Éclairage
    "lighting": {
        "LED 10W": {
            "power_kw": 0.01,
            "usage_profile": {
                "winter": [0.8]*6 + [0.3]*12 + [0.8]*6,
                "summer": [0.2]*6 + [0.1]*12 + [0.5]*6
            }
        }
    }
}
