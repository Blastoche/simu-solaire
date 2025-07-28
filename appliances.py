# -*- coding: utf-8 -*-
"""
Base de données complète des appareils électroménagers (2025)
Sources : ADEME, fabricants, études de consommation
"""

APPLIANCES = {
    # ---------------------------------------------------
    # 1. GROS ÉLECTROMÉNAGER (USAGE INTENSIF)
    # ---------------------------------------------------
    "heavy_usage": {
        "Machine à laver": {
            "Classique": {
                "power_kw": 1.2,
                "duration_hours": 1.8,
                "usage_profile": {
                    "weekday": [0]*7 + [0.2, 0.4, 0.3] + [0]*14,
                    "weekend": [0]*10 + [0.5, 0.7, 0.6] + [0]*9
                }
            },
            "Éco": {
                "power_kw": 0.8,
                "duration_hours": 2.2,
                "usage_profile": {
                    "weekday": [0]*6 + [0.1, 0.3, 0.2] + [0]*14,
                    "weekend": [0]*9 + [0.4, 0.6, 0.5] + [0]*10
                }
            }
        },
        "Lave-vaisselle": {
            "Standard": {
                "power_kw": 1.5,
                "duration_hours": 1.5,
                "usage_profile": {
                    "weekday": [0]*8 + [0.1, 0.3, 0.2] + [0]*12,
                    "weekend": [0]*10 + [0.6, 0.8, 0.7] + [0]*7
                }
            }
        },
        "Four": {
            "Électrique": {
                "power_kw": 2.5,
                "duration_hours": 1.0,
                "usage_profile": {
                    "weekday": [0]*11 + [0.7, 0.9, 0.5] + [0]*10,
                    "weekend": [0]*10 + [0.8, 0.9, 0.8] + [0]*7
                }
            },
            "Micro-ondes": {
                "power_kw": 0.9,
                "duration_mins": 15,
                "usage_profile": {
                    "weekday": [0]*7 + [0.3]*3 + [0]*14,
                    "weekend": [0]*9 + [0.5]*4 + [0]*11
                }
            }
        }
    },

    # ---------------------------------------------------
    # 2. FROID (FONCTIONNEMENT CONTINU)
    # ---------------------------------------------------
    "cold_appliances": {
        "Réfrigérateur": {
            "A+": {
                "power_kw": 0.10,
                "usage_profile": [0.8, 0.7, 0.6, 0.5, 0.5, 0.6, 0.9, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.7, 0.8, 0.9, 1.0, 1.1, 1.3, 1.5, 1.2, 1.0, 0.9, 0.8]
            },
            "Américain": {
                "power_kw": 0.25,
                "usage_profile": [1.0]*24  # Charge constante
            }
        },
        "Congélateur": {
            "Coffre": {
                "power_kw": 0.12,
                "usage_profile": [0.7]*24
            }
        }
    },

    # ---------------------------------------------------
    # 3. AUDIOVISUEL & INFORMATIQUE
    # ---------------------------------------------------
    "entertainment": {
        "Téléviseur": {
            "LED 55\"": {
                "power_kw": 0.12,
                "usage_profile": {
                    "weekday": [0]*8 + [0.1, 0.2, 0.1, 0.2, 0.4, 0.8, 0.9, 1.0, 0.8, 0.5, 0.3, 0.1] + [0]*4,
                    "weekend": [0]*9 + [0.2, 0.4, 0.6, 0.8, 1.0, 1.0, 0.9, 0.8, 0.7, 0.5, 0.3, 0.1]
                }
            }
        },
        "Ordinateur": {
            "Portable": {
                "power_kw": 0.06,
                "usage_profile": {
                    "weekday": [0]*7 + [0.3, 0.5, 0.5, 0.4, 0.3, 0.2, 0.4, 0.6, 0.5, 0.3] + [0]*7,
                    "weekend": [0]*10 + [0.4, 0.6, 0.7, 0.6, 0.5] + [0]*7
                }
            }
        }
    },

    # ---------------------------------------------------
    # 4. PETIT ÉLECTROMÉNAGER
    # ---------------------------------------------------
    "small_appliances": {
        "Cafetière": {
            "Classique": {
                "power_kw": 1.0,
                "duration_mins": 10,
                "usage_profile": {
                    "weekday": [0.8, 0.2] + [0]*22,
                    "weekend": [0.6, 0.3] + [0]*22
                }
            }
        },
        "Aspirateur": {
            "Standard": {
                "power_kw": 0.8,
                "duration_mins": 30,
                "usage_profile": {
                    "weekday": [0]*9 + [0.3, 0.4] + [0]*13,
                    "weekend": [0]*11 + [0.5, 0.6] + [0]*11
                }
            }
        }
    }
}
