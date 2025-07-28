import streamlit as st
from modules.weather import get_weather_data

st.title("🌤️ Test des Sources Météo")

lat = st.number_input("Latitude", value=48.85)
lon = st.number_input("Longitude", value=2.35)
use_mock = st.checkbox("Forcer les données simulées")

if st.button("Tester"):
    data = get_weather_data(lat, lon, use_mock=use_mock)
    
    st.write(f"Source utilisée : **{data['source']}**")
    st.line_chart(data["data"]["ghi"])
    st.json(data["data"].describe())
