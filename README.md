solar_simulator/
│
├── app/                      # Version Streamlit complète
│   ├── ui/                   # Composants d'interface
│   │   ├── sidebar.py        # Paramètres utilisateur
│   │   ├── results_display.py# Visualisations
│   │   └── appliance_inputs.py # Saisie des appareils
│   └── main.py               # Point d'entrée
│
├── core/                     # Noyau de calcul
│   ├── simulation.py         # Logique principale
│   ├── adapters.py           # Conversion UI → paramètres
│   └── exceptions.py         # Gestion des erreurs
│
├── modules/                  # Modules métier
│   ├── weather/              # Tout ce qui concerne la météo
│   │   ├── pvgis_client.py   # Appels à PVGIS
│   │   ├── openweather.py    # Appels à OpenWeather
│   │   └── weather_models.py # Modèles de données
│   │
│   ├── pv_production/        # Production solaire
│   │   ├── pvlib_wrapper.py  # Adapteur pour PVLib
│   │   └── shading.py        # Gestion des masques solaires
│   │
│   ├── consumption/          # Consommation électrique
│   │   ├── appliance_models.py # Profils des appareils
│   │   └── dpe_calculator.py # Calculs DPE
│   │
│   └── economics/            # Analyse financière
│       ├── subsidies.py      # Gestion des aides
│       └── roi_calculator.py # Calcul de rentabilité
│
├── config/                   # Configuration
│   ├── api.py                # Clés et endpoints externes
│   ├── tariffs.py            # Tarifs énergétiques
│   ├── appliances.py         # Base de données appareils
│   └── __init__.py
│
├── assets/                   # Ressources statiques
│   ├── dpe_coefficients.json # Données DPE
│   ├── images/               # Logos/illustrations
│   └── geo/                  # Fichiers géographiques
│
├── tests/                    # Tests automatisés
│   ├── test_weather.py
│   └── test_pv_production.py
│
└── requirements.txt          # Dépendances Python
