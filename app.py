# solar_simulator/app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import time
from modules.consumption import ConsumptionSimulator
from modules.pv_production import PVSimulator
from modules.weather import fetch_pvgis_historical, fetch_openweather_forecast
from modules.economics import FinancialAnalyzer
from config.tariffs import TARIFFS
from config.appliances import APPLIANCES

# ======================
# CONFIGURATION DE LA PAGE
# ======================
st.set_page_config(
    page_title="Simulateur Solaire Pro",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================
# FONCTIONS AUXILIAIRES
# ======================
def geocode_address(address):
    """Géocodage via API Nominatim"""
    # [...] Implémentation complète

def display_results(results):
    """Affiche les résultats avec mise en forme avancée"""
    # [...] Graphiques interactifs + KPIs

# ======================
# INTERFACE UTILISATEUR
# ======================
def main():
    st.title("📊 Simulateur Solaire Complet")

    # ----- SIDEBAR -----
    with st.sidebar:
        st.header("📍 Localisation")
        location_mode = st.radio("Mode", ["Coordonnées", "Adresse"])
        
        if location_mode == "Coordonnées":
            lat = st.number_input("Latitude", value=48.8534, format="%.6f")
            lon = st.number_input("Longitude", value=2.3488, format="%.6f")
        else:
            address = st.text_input("Adresse")
            lat, lon = geocode_address(address)

        st.header("🌤️ Source Météo")
        weather_source = st.selectbox("Choix", ["Historique PVGIS", "Prévisions OpenWeather"])

    # ----- ONGLETS PRINCIPAUX -----
    tab1, tab2, tab3 = st.tabs(["🏠 Logement", "🔌 Appareils", "📊 Résultats"])

    with tab1:
        # Section détaillée logement
        col1, col2 = st.columns(2)
        with col1:
            surface = st.number_input("Surface (m²)", min_value=20, value=80)
            dpe = st.selectbox("DPE", ["A", "B", "C", "D", "E", "F", "G"])
        with col2:
            occupants = st.number_input("Occupants", min_value=1, value=3)
            heating_type = st.selectbox("Chauffage", ["Gaz", "Électrique", "PAC"])

    with tab2:
        # Sélection interactive des appareils
        selected_appliances = []
        for category, devices in APPLIANCES.items():
            with st.expander(f"🔧 {category}"):
                for device, models in devices.items():
                    if st.checkbox(device):
                        model = st.selectbox(
                            f"Modèle {device}",
                            list(models.keys())
                        )
                        usage = st.slider(
                            f"Utilisation/semaine {device}",
                            1, 20, 3
                        )
                        selected_appliances.append({
                            "name": device,
                            "model": model,
                            "usage": usage
                        })

    # ======================
    # SIMULATION
    # ======================
    if st.button("🚀 Lancer la simulation", type="primary"):
        with st.spinner("Calcul en cours..."):
            try:
                # 1. Données météo
                if weather_source == "Historique PVGIS":
                    weather_data = fetch_pvgis_historical(lat, lon)
                else:
                    weather_data = fetch_openweather_forecast(lat, lon)

                # 2. Simulation PV
                pv_system = PVSimulator(
                    location={"lat": lat, "lon": lon},
                    system_params={
                        "power_kw": st.session_state.get("pv_power", 3.0),
                        "tilt": st.session_state.get("tilt", 30),
                        "azimuth": 180
                    }
                )
                pv_prod = pv_system.calculate(weather_data)

                # 3. Simulation Consommation
                consumption = ConsumptionSimulator({
                    "appliances": selected_appliances,
                    "surface": surface,
                    "dpe": dpe,
                    "occupants": occupants
                }).calculate()

                # 4. Analyse Financière
                analysis = FinancialAnalyzer(
                    pv_production=pv_prod,
                    consumption=consumption
                ).analyze()

                # Affichage
                with tab3:
                    display_results(analysis)

            except Exception as e:
                st.error(f"Erreur : {str(e)}")

if __name__ == "__main__":
    main()
