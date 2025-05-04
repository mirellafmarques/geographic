import streamlit as st

st.set_page_config(layout="wide")  # Esta linha deve vir antes de qualquer st.write(), st.title(), etc.

# Construindo o Sidebar
st.sidebar.title("Geographic")
page = st.sidebar.radio("Aplicações", ["Home", "Magnetic"])

logo = "Earth.jpeg"
st.sidebar.image(logo)

st.sidebar.title("About")
st.sidebar.info("Geographic")

#Importando as Bibliotecas
import folium
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.plot import reshape_as_image
import numpy as np
from PIL import Image

# Conteúdo condicional
if page == "Home":
    st.title("Geographic")
    st.write("Bem-vindo ao aplicativo Geographic!")


elif page == "Magnetic":
    st.title("Aplicações Magnéticas")
    st.write("Aqui você pode explorar as funcionalidades relacionadas ao campo magnético.")
    # Coloque seu código da seção 'Magnetic' aqui
    # "https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml?useFullSite=true"

import ppigrf
from datetime import datetime

# Defina a localização e a data
latitude = -23.5505
longitude = -46.6333
altitude_km = 0  # em quilômetros
data = datetime(2025, 5, 2)

# Calcule os componentes do campo magnético
Be, Bn, Bu = ppigrf.igrf(longitude, latitude, altitude_km, data)

print(f"Componente Leste (Be): {Be.item():.2f} nT")
print(f"Componente Norte (Bn): {Bn.item():.2f} nT")
print(f"Componente Vertical (Bu): {Bu.item():.2f} nT")

  
