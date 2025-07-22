import streamlit as st
from modules.consumption import HouseholdConsumption
from modules.pv_production import PVSystem
from modules.economics import FinancialAnalysis
from config import TARIFFS, DEFAULT_APPLIANCES

def main():
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
