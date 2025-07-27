import streamlit as st
from modules.consumption import HouseholdConsumption
from modules.pv_production import PVSystem
from modules.economics import FinancialAnalysis
from config import TARIFFS, DEFAULT_APPLIANCES

# Section données météo

def get_weather_params():
    st.sidebar.header("🌤️ Données Météo")
    
    # 1. Localisation
    mode = st.sidebar.radio("Mode de localisation", ["Adresse", "Coordonnées"])
    if mode == "Adresse":
        address = st.sidebar.text_input("Adresse complète")
        lat, lon = geocode(address)  # À implémenter
    else:
        lat = st.sidebar.number_input("Latitude", value=48.85)
        lon = st.sidebar.number_input("Longitude", value=2.35)
    
    # 2. Type de données
    data_type = st.sidebar.selectbox(
        "Source météo",
        ["Historique (PVGIS)", "Prévisions (OpenWeatherMap)"]
    )
    
    # 3. Paramètres avancés
    with st.sidebar.expander("⚙️ Options avancées"):
        if data_type == "Historique":
            year = st.selectbox("Année de référence", range(2005, 2024), index=18)
        resolution = st.radio("Résolution", ["Horaire", "Quotidienne"])
    
    return {
        "lat": lat,
        "lon": lon,
        "data_type": data_type,
        "year": year if data_type == "Historique" else None,
        "resolution": resolution
    }

def main():
    
# Intégration des données météo
    weather_params = get_weather_params()
    pv_data = PVSimulator(weather_params).fetch_production_data()

    # Configuration de la page
    st.set_page_config(
        page_title="Simulateur Solaire Intelligent",
        layout="wide",
        page_icon="☀️"
    )
    
    # Sidebar pour les entrées utilisateur
    with st.sidebar:
        st.header("Paramètres du Projet")
        location = get_location_input()
        household = get_household_input()
    
    # Onglets principaux
    tab1, tab2, tab3 = st.tabs(["Consommation", "Production PV", "Rentabilité"])
    
    with tab1:
        consumption = HouseholdConsumption(household).calculate()
        display_consumption(consumption)
    
    with tab2:
        pv_system = PVSystem(location, household).calculate()
        display_production(pv_system)
    
    with tab3:
        analysis = FinancialAnalysis(consumption, pv_system, TARIFFS).analyze()
        display_economics(analysis)

def get_location_input():
    """Récupère la localisation via coordonnées ou code postal."""
    # ... (votre code existant adapté)
    return {"latitude": lat, "longitude": lon}

if __name__ == "__main__":
    main()
