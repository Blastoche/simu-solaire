# -*- coding: utf-8 -*-
"""
Point d'entrée de l'application Streamlit
"""
import streamlit as st
import logging
from core.simulation import SimulationEngine
from core.adapters import ui_to_simulation_params
from core.exceptions import SimulationError
from ui.sidebar import build_sidebar
from ui.results import display_results

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    st.set_page_config(
        page_title="SolarSimulator Pro",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("☀️ SolarSimulator - Version Professionnelle")
    
    # Initialisation session state si nécessaire
    if 'simulation_results' not in st.session_state:
        st.session_state.simulation_results = None
    
    # 1. Sidebar avec paramètres
    try:
        build_sidebar()  # Remplit st.session_state
    except Exception as e:
        st.error(f"Erreur interface utilisateur: {str(e)}")
        st.stop()

    # 2. Validation et conversion des paramètres UI
    try:
        # Vérifier que les paramètres essentiels sont présents
        required_params = ['latitude', 'longitude', 'dpe', 'occupants']
        missing_params = [p for p in required_params if p not in st.session_state]
        
        if missing_params:
            st.warning(f"Veuillez renseigner: {', '.join(missing_params)}")
            st.stop()
        
        params = ui_to_simulation_params(st.session_state)
        
        # Ajout de paramètres par défaut si manquants
        params.setdefault('investment_cost', params['pv_system']['power_kw'] * 2500)  # 2500€/kWc
        params.setdefault('use_mock_weather', False)
        
    except KeyError as e:
        st.error(f"Paramètre manquant : {str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"Erreur validation paramètres: {str(e)}")
        st.stop()

    # 3. Affichage des paramètres (debug)
    with st.expander("🔍 Paramètres de simulation", expanded=False):
        st.json(params)

    # 4. Lancement de la simulation
    col1, col2 = st.columns([1, 4])
    
    with col1:
        run_simulation = st.button("🚀 Lancer la simulation", type="primary")
        use_mock = st.checkbox("Mode test (données simulées)", value=False)
    
    with col2:
        if st.session_state.simulation_results:
            st.success("✅ Dernière simulation réussie")
        
    if run_simulation:
        params['use_mock_weather'] = use_mock
        
        with st.spinner("🔄 Simulation en cours..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Initialisation
                status_text.text("Initialisation du moteur de simulation...")
                progress_bar.progress(10)
                engine = SimulationEngine()
                
                # Récupération données météo
                status_text.text("Récupération des données météo...")
                progress_bar.progress(30)
                
                # Lancement simulation
                status_text.text("Calcul de la production solaire...")
                progress_bar.progress(60)
                
                results = engine.run(params)
                
                status_text.text("Analyse économique...")
                progress_bar.progress(90)
                
                # Sauvegarde des résultats
                st.session_state.simulation_results = results
                progress_bar.progress(100)
                status_text.text("✅ Simulation terminée avec succès!")
                
                # Affichage immédiat des résultats
                st.rerun()
                
            except SimulationError as e:
                st.error(f"❌ Erreur de simulation: {str(e)}")
                logger.error(f"SimulationError: {str(e)}")
                
            except Exception as e:
                st.error(f"❌ Erreur inattendue: {str(e)}")
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)
                
            finally:
                progress_bar.empty()
                status_text.empty()

    # 5. Affichage des résultats si disponibles
    if st.session_state.simulation_results:
        try:
            display_results(st.session_state.simulation_results)
            
            # Option d'export
            with st.expander("💾 Export des résultats"):
                if st.button("Télécharger rapport PDF"):
                    st.info("Fonctionnalité d'export à implémenter")
                    
        except Exception as e:
            st.error(f"Erreur affichage résultats: {str(e)}")

if __name__ == "__main__":
    main()
