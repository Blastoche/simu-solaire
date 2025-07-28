# -*- coding: utf-8 -*-
"""
Affichage des résultats de simulation
"""
import streamlit as st
import pandas as pd
import plotly.express as px

def display_results(results: Dict):
    """Affiche les résultats sous forme de dashboard"""
    
    # 1. KPI Principaux
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Production annuelle", f"{results['production']['annual_kwh']:.0f} kWh")
    with col2:
        st.metric("Consommation annuelle", f"{results['consumption']['annual_kwh']:.0f} kWh")
    with col3:
        st.metric("Taux d'autoconsommation", 
                 f"{results['economics']['autoconsommation_rate']:.1%}")

    # 2. Graphique interactif
    df = pd.DataFrame({
        "Production (kWh)": results['production']['hourly'],
        "Consommation (kWh)": results['consumption']['hourly']
    })
    fig = px.line(df, title="Production vs Consommation")
    st.plotly_chart(fig, use_container_width=True)

    # 3. Détails économiques
    with st.expander("📊 Détails financiers"):
        st.dataframe(pd.DataFrame.from_dict(
            results['economics'],
            orient='index',
            columns=['Valeur']
        ))
