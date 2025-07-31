#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification et configuration du simulateur solaire
À exécuter avant le premier lancement
"""
import os
import sys
import subprocess
from pathlib import Path
import importlib.util

def check_python_version():
    """Vérifie la version de Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requis")
        return False
    print(f"✅ Python {sys.version.split()[0]} OK")
    return True

def check_dependencies():
    """Vérifie les dépendances Python"""
    required_packages = [
        'pandas', 'numpy', 'pvlib', 'streamlit', 
        'plotly', 'sqlalchemy', 'requests'
    ]
    
    missing = []
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} installé")
        except ImportError:
            print(f"❌ {package} manquant")
            missing.append(package)
    
    if missing:
        print(f"\n📦 Pour installer les dépendances manquantes:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True

def create_directory_structure():
    """Crée la structure de répertoires nécessaire"""
    directories = [
        "cache/pv_production",
        "cache/weather",
        "logs",
        "data/weather",
        "assets"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Répertoire créé: {directory}")

def create_missing_init_files():
    """Crée les fichiers __init__.py manquants"""
    init_files = [
        "modules/__init__.py",
        "modules/consumption/__init__.py",
        "modules/economics/__init__.py",
        "core/__init__.py",
        "config/__init__.py",
        "app/__init__.py",
        "app/ui/__init__.py"
    ]
    
    for init_file in init_files:
        file_path = Path(init_file)
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text('# -*- coding: utf-8 -*-\n')
            print(f"✅ Créé: {init_file}")

def verify_module_imports():
    """Teste les imports des modules principaux"""
    test_imports = [
        ("modules.weather", "get_weather_data"),
        ("modules.pv_production", "simulate_pv_system"),
        ("core.simulation", "SimulationEngine"),
        ("core.adapters", "ui_to_simulation_params")
    ]
    
    all_good = True
    for module_name, function_name in test_imports:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, function_name):
                print(f"✅ {module_name}.{function_name} OK")
            else:
                print(f"❌ {module_name}.{function_name} manquant")
                all_good = False
        except ImportError as e:
            print(f"❌ Import {module_name} échoué: {e}")
            all_good = False
    
    return all_good

def create_env_template():
    """Crée un fichier .env template"""
    env_content = """# Configuration du simulateur solaire
# Copiez ce fichier en .env et renseignez vos clés API

# Base de données (optionnel)
DATABASE_URL=sqlite:///solar_simulator.db

# OpenWeatherMap API (optionnel, pour données météo en temps réel)
OPENWEATHER_API_KEY=votre_cle_ici

# Configuration logs
LOG_LEVEL=INFO

# Configuration cache
CACHE_ENABLED=true
CACHE_TTL_HOURS=24
"""
    
    env_file = Path(".env.template")
    if not env_file.exists():
        env_file.write_text(env_content)
        print("✅ Fichier .env.template créé")

def run_basic_test():
    """Exécute un test basique du simulateur"""
    print("\n🧪 Test basique du simulateur...")
    
    try:
        # Test données météo mock
        from modules.weather.mock_weather import generate_mock_weather
        mock_data = generate_mock_weather(48.8566, 2.3522, year=2020)
        
        if len(mock_data) > 0:
            print(f"✅ Données météo mock: {len(mock_data)} points")
        else:
            print("❌ Échec génération données mock")
            return False
        
        # Test configuration DPE
        from pathlib import Path
        import json
        
        dpe_file = Path("assets/dpe_coefficients.json")
        if dpe_file.exists():
            with open(dpe_file, 'r') as f:
                dpe_data = json.load(f)
            print(f"✅ Configuration DPE: {len(dpe_data)} classes")
        else:
            print("❌ Fichier DPE manquant")
            return False
        
        print("✅ Tests basiques réussis")
        return True
        
    except Exception as e:
        print(f"❌ Test échoué: {e}")
        return False

def main():
    """Fonction principale de vérification"""
    print("🔍 Vérification de l'installation du simulateur solaire\n")
    
    checks = [
        ("Version Python", check_python_version),
        ("Dépendances", check_dependencies),
        ("Structure répertoires", lambda: (create_directory_structure(), True)[1]),
        ("Fichiers __init__.py", lambda: (create_missing_init_files(), True)[1]),
        ("Template .env", lambda: (create_env_template(), True)[1]),
        ("Imports modules", verify_module_imports),
        ("Tests basiques", run_basic_test)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}:")
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Erreur lors de {check_name}: {e}")
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 Installation vérifiée avec succès!")
        print("\n🚀 Pour lancer le simulateur:")
        print("streamlit run app/main.py")
    else:
        print("⚠️ Problèmes détectés - Consultez les messages ci-dessus")
        print("\n📚 Aide:")
        print("1. Installez les dépendances manquantes avec pip")
        print("2. Vérifiez la structure des fichiers")
        print("3. Consultez la documentation")
    
    return all_passed

if __name__ == "__main__":
    main()
