# -*- coding: utf-8 -*-
"""
Construction de la sidebar Streamlit
"""
import streamlit as st
from config.appliances import APPLIANCES

def build_sidebar():
    with st.sidebar:
        st.header("📍 Localisation")
        st.session_state['latitude'] = st.number_input("Latitude", value=48.8534)
        st.session_state['longitude'] = st.number_input("Longitude", value=2.3488)
        st.session_state['orientation'] = st.selectbox(
            "Orientation", ["Sud", "Sud-Est", "Sud-Ouest", "Est", "Ouest"])
        
        st.header("🏠 Logement")
        st.session_state['dpe'] = st.selectbox(
            "DPE", ["A", "B", "C", "D", "E", "F", "G"])
        st.session_state['occupants'] = st.number_input("Nombre d'occupants", 1, 10, 3)
        
        st.header("🔌 Appareils")
        _build_appliance_inputs()

def _build_appliance_inputs():
    """Gère la sélection interactive des appareils"""
    st.session_state['selected_appliances'] = []
    
    for category, devices in APPLIANCES.items():
        with st.expander(f"{category}"):
            for device, models in devices.items():
                if st.checkbox(device):
                    model = st.selectbox(
                        f"Modèle {device}",
                        list(models.keys())
                    )
                    usage = st.slider(
                        f"Utilisation/semaine {device}",
                        1, 20, 3,
                        key=f"usage_{device}"
                    )
                    st.session_state['selected_appliances'].append({
                        "name": device,
                        "model": model,
                        "usage_hours": usage
                    })
