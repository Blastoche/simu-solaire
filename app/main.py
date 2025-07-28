# -*- coding: utf-8 -*-
"""
Point d'entrée de l'application Streamlit
"""
import streamlit as st
from core.simulation import SimulationEngine
from core.adapters import ui_to_simulation_params
from ui.sidebar import build_sidebar
from ui.results import display_results

def main():
    # Configuration de la page
    st.set_page_config(
        page_title="SolarSimulator Pro",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Construction de l'interface
    st.title("☀️ SolarSimulator - Version Professionnelle")
    
    # 1. Sidebar avec paramètres
    build_sidebar()  # Remplit st.session_state

    # 2. Conversion des paramètres UI
    try:
        params = ui_to_simulation_params(st.session_state)
    except KeyError as e:
        st.error(f"Paramètre manquant : {str(e)}")
        st.stop()

    # 3. Lancement de la simulation
    if st.button("🚀 Lancer la simulation", type="primary"):
        with st.spinner("Simulation en cours..."):
            try:
                engine = SimulationEngine()
                results = engine.run(params)
                display_results(results)
            except Exception as e:
                st.error(f"Erreur lors de la simulation : {str(e)}")

if __name__ == "__main__":
    main()
