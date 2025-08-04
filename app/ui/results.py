# -*- coding: utf-8 -*-
"""
Affichage des résultats de simulation
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict
import logging

logger = logging.getLogger(__name__)

def display_results(results: Dict):
    """Affiche les résultats sous forme de dashboard robuste"""
    try:
        # Vérification de la structure des résultats
        if not results or 'production' not in results:
            st.error("Résultats de simulation invalides")
            return
        
        # Affichage de l'avertissement source de données si présent
        if results.get('warning'):
            st.warning(f"⚠️ {results['warning']}")
        
        if results.get('weather_source') == 'MOCK':
            st.info("ℹ️ Simulation utilisant des données météo simulées")
        
        # 1. KPI Principaux
        st.header("📊 Résultats de la simulation")
        
        production_data = results['production']
        consumption_data = results['consumption']
        economics_data = results.get('economics', {})
        
        # Extraction des valeurs avec gestion d'erreur
        try:
            annual_production = float(production_data.get('annual_yield_kwh', 
                                    production_data.get('hourly_production_kw', pd.Series()).sum()))
            annual_consumption = float(consumption_data.get('consumption_kw', pd.Series()).sum())
            autoconso_rate = float(economics_data.get('autoconsumption_rate', 0))
        except (ValueError, TypeError, AttributeError) as e:
            logger.warning(f"Erreur extraction métriques: {e}")
            st.error("Erreur dans le format des résultats")
            return
        
        # Affichage des KPI
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🌞 Production annuelle", 
                f"{annual_production:,.0f} kWh",
                help="Production solaire totale estimée sur une année"
            )
        
        with col2:
            st.metric(
                "🏠 Consommation annuelle", 
                f"{annual_consumption:,.0f} kWh",
                help="Consommation électrique totale du foyer"
            )
        
        with col3:
            st.metric(
                "⚡ Taux d'autoconsommation", 
                f"{autoconso_rate:.1%}",
                help="Part de la production consommée directement"
            )
        
        with col4:
            autonomy_rate = economics_data.get('autonomy_rate', 0)
            st.metric(
                "🔋 Taux d'autonomie",
                f"{autonomy_rate:.1%}",
                help="Part des besoins couverts par le solaire"
            )

        # 2. Graphiques de production vs consommation
        st.header("📈 Profils de production et consommation")
        
        try:
            # Préparation des données pour graphique
            prod_series = production_data.get('hourly_production_kw', pd.Series())
            cons_series = consumption_data.get('consumption_kw', pd.Series())
            
            if len(prod_series) > 0 and len(cons_series) > 0:
                # Limitation à une période raisonnable pour l'affichage
                display_period = min(len(prod_series), 24*7)  # 1 semaine max
                
                df_plot = pd.DataFrame({
                    'Heure': range(display_period),
                    'Production (kW)': prod_series.iloc[:display_period].values,
                    'Consommation (kW)': cons_series.iloc[:display_period].values
                })
                
                fig = px.line(
                    df_plot, 
                    x='Heure', 
                    y=['Production (kW)', 'Consommation (kW)'],
                    title="Production vs Consommation (première semaine)"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Graphique mensuel si données annuelles disponibles
                if len(prod_series) > 24*30:  # Plus d'un mois de données
                    monthly_prod = prod_series.resample('M').sum()
                    monthly_cons = cons_series.resample('M').sum()
                    
                    df_monthly = pd.DataFrame({
                        'Mois': monthly_prod.index.strftime('%B'),
                        'Production (kWh)': monthly_prod.values,
                        'Consommation (kWh)': monthly_cons.values
                    })
                    
                    fig_monthly = px.bar(
                        df_monthly,
                        x='Mois',
                        y=['Production (kWh)', 'Consommation (kWh)'],
                        title="Bilan énergétique mensuel",
                        barmode='group'
                    )
                    st.plotly_chart(fig_monthly, use_container_width=True)
            
        except Exception as e:
            logger.warning(f"Erreur création graphiques: {e}")
            st.warning("Impossible d'afficher les graphiques détaillés")

        # 3. Analyse économique
        st.header("💰 Analyse économique")
        
        if economics_data:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Flux énergétiques")
                energy_metrics = {
                    "Autoconsommation": f"{economics_data.get('autoconsumption_kwh', 0):,.0f} kWh",
                    "Surplus injecté": f"{economics_data.get('surplus_kwh', 0):,.0f} kWh",
                    "Déficit réseau": f"{economics_data.get('deficit_kwh', 0):,.0f} kWh"
                }
                
                for metric, value in energy_metrics.items():
                    st.write(f"**{metric}:** {value}")
            
            with col2:
                st.subheader("Indicateurs financiers")
                
                # ROI si disponible
                if 'roi_years' in economics_data:
                    st.write(f"**Retour sur investissement:** {economics_data['roi_years']:.1f} ans")
                
                # Économies annuelles
                if 'annual_savings' in economics_data:
                    st.write(f"**Économies annuelles:** {economics_data['annual_savings']:,.0f} €")
                
                # Subventions
                if 'subsidies_euro' in economics_data:
                    st.write(f"**Aides financières:** {economics_data['subsidies_euro']:,.0f} €")

        # 4. Recommandations
        st.header("💡 Recommandations")
        
        recommendations = []
        
        if autoconso_rate < 0.3:
            recommendations.append("🔋 Taux d'autoconsommation faible - considérez l'ajout d'une batterie")
        elif autoconso_rate > 0.7:
            recommendations.append("✅ Excellent taux d'autoconsommation - installation bien dimensionnée")
            
        if autonomy_rate < 0.4:
            recommendations.append("⚡ Autonomie limitée - envisagez d'augmenter la puissance installée")
        elif autonomy_rate > 0.8:
            recommendations.append("🎯 Très bonne autonomie énergétique atteinte")
        
        if annual_production > annual_consumption * 1.2:
            recommendations.append("📉 Surproduction importante - optimisez le dimensionnement")
        
        for rec in recommendations:
            st.info(rec)
        
        if not recommendations:
            st.success("🎉 Configuration équilibrée - aucune recommandation particulière")

        # 5. Détails techniques (collapsible)
        with st.expander("🔧 Détails techniques"):
            tech_details = {
                "Source météo": results.get('weather_source', 'Inconnue'),
                "Période simulation": "2020 (année type)",
                "Granularité": "Horaire",
                "Modèle PV": "PVLib avec pertes système",
            }
            
            for key, value in tech_details.items():
                st.write(f"**{key}:** {value}")
            
            # Affichage données brutes si demandé
            if st.checkbox("Afficher les données brutes"):
                st.subheader("Production horaire")
                st.dataframe(production_data.get('hourly_production_kw', pd.Series()).head(24))
                
                st.subheader("Consommation horaire") 
                st.dataframe(consumption_data.get('consumption_kw', pd.Series()).head(24))
        
    except Exception as e:
        logger.error(f"Erreur affichage résultats: {str(e)}", exc_info=True)
        st.error(f"Erreur lors de l'affichage des résultats: {str(e)}")
        
        # Affichage debug en cas d'erreur
        with st.expander("🐛 Informations de debug"):
            st.write("Structure des résultats reçus:")
            st.write(type(results))
            if isinstance(results, dict):
                st.write("Clés disponibles:", list(results.keys()))
