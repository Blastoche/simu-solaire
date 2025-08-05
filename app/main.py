# -*- coding: utf-8 -*-
"""
Point d'entrée de l'application Streamlit - VERSION CORRIGÉE AVEC MODÈLE SIMPLE
"""
import streamlit as st
import logging
import sys
from pathlib import Path

# Ajout du répertoire racine au path Python
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Imports du simulateur
try:
    from core.simulation import SimulationEngine
    from core.adapters import ui_to_simulation_params
    from core.exceptions import SolarSimulatorError as SimulationError
    from app.ui.sidebar import build_sidebar
    from app.ui.results import display_results
    from config.logging import setup_logging
except ImportError as e:
    st.error(f"Erreur d'import: {e}")
    st.error("Vérifiez que tous les modules sont présents et correctement configurés")
    st.stop()

# Configuration logging
setup_logging(level=logging.INFO)
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
        logger.error(f"Erreur sidebar: {e}", exc_info=True)
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
        if 'pv_system' in params and 'power_kw' in params['pv_system']:
            params.setdefault('investment_cost', params['pv_system']['power_kw'] * 2500)  # 2500€/kWc
        params.setdefault('use_mock_weather', False)
        
    except KeyError as e:
        st.error(f"Paramètre manquant : {str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"Erreur validation paramètres: {str(e)}")
        logger.error(f"Erreur paramètres: {e}", exc_info=True)
        st.stop()

    # 3. Affichage des paramètres (debug)
    with st.expander("🔍 Paramètres de simulation", expanded=False):
        st.json(params)

    # 4. Options de simulation
    st.header("⚙️ Options de simulation")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        use_mock = st.checkbox("Mode test (données simulées)", value=True)  # Par défaut en mode test
    
    with col2:
        use_simple_model = st.checkbox(
            "Modèle PV simplifié", 
            value=True,  # Par défaut activé pour éviter les erreurs
            help="Utilise le modèle PVWatts plus robuste et rapide"
        )
    
    with col3:
        if st.session_state.simulation_results:
            st.success("✅ Dernière simulation réussie")

    # 5. Lancement de la simulation
    run_simulation = st.button("🚀 Lancer la simulation", type="primary")
    
    if run_simulation:
        params['use_mock_weather'] = use_mock
        params['use_simple_model'] = use_simple_model  # NOUVEAU PARAMÈTRE
        
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
                if use_simple_model:
                    status_text.text("Calcul de la production solaire (modèle PVWatts)...")
                else:
                    status_text.text("Calcul de la production solaire (modèle avancé)...")
                progress_bar.progress(60)
                
                results = engine.run(params)
                
                status_text.text("Analyse économique...")
                progress_bar.progress(90)
                
                # Sauvegarde des résultats
                st.session_state.simulation_results = results
                progress_bar.progress(100)
                status_text.text("✅ Simulation terminée avec succès!")
                
                # Affichage du modèle utilisé
                model_used = results.get('production', {}).get('model_used', 'Unknown')
                st.info(f"📊 Modèle PV utilisé: {model_used}")
                
                # Nettoyage de l'interface
                progress_bar.empty()
                status_text.empty()
                
                # Rerun pour afficher les résultats
                st.rerun()
                
            except SimulationError as e:
                st.error(f"❌ Erreur de simulation: {str(e)}")
                logger.error(f"SimulationError: {str(e)}")
                
                # Suggestion d'utiliser le modèle simple si pas déjà activé
                if not use_simple_model:
                    st.info("💡 Conseil: Essayez d'activer l'option 'Modèle PV simplifié' pour plus de robustesse")
                
            except Exception as e:
                st.error(f"❌ Erreur inattendue: {str(e)}")
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)
                
                # Affichage d'informations de debug
                with st.expander("🐛 Informations de debug"):
                    st.write("Type d'erreur:", type(e).__name__)
                    st.write("Message:", str(e))
                    if hasattr(e, '__traceback__'):
                        import traceback
                        st.code(traceback.format_exc())
                
            finally:
                progress_bar.empty()
                status_text.empty()

    # 6. Affichage des résultats si disponibles
    if st.session_state.simulation_results:
        try:
            display_results(st.session_state.simulation_results)
            
            # Option d'export
            with st.expander("💾 Export des résultats"):
                if st.button("Télécharger rapport PDF"):
                    st.info("Fonctionnalité d'export à implémenter")
                    
        except Exception as e:
            st.error(f"Erreur affichage résultats: {str(e)}")
            logger.error(f"Erreur affichage: {e}", exc_info=True)

    # 7. Aide et documentation
    with st.expander("📚 Aide et conseils"):
        st.markdown("""
        ### Conseils d'utilisation :
        
        **🔧 Modèle PV simplifié**
        - ✅ Recommandé pour la plupart des cas
        - Plus robuste et rapide
        - Utilise le modèle PVWatts éprouvé
        
        **⚡ Modèle PV avancé**
        - Plus précis mais plus sensible aux erreurs
        - Utilise des modèles thermiques détaillés
        - Désactivez en cas d'erreur de simulation
        
        **🌤️ Données météo**
        - Mode test : données simulées réalistes
        - Mode réel : données PVGIS (nécessite connexion)
        
        **🏠 Paramètres importants**
        - DPE : impact majeur sur la consommation
        - Orientation Sud recommandée pour production maximale
        - Inclinaison 30° optimale pour la France
        """)

if __name__ == "__main__":
    main()
