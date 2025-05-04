import streamlit as st
from datetime import datetime

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


# Inputs do usuário
col1, col2, col3 = st.columns(3)

with col1:
    latitude = st.number_input("Latitude (°)", value=-23.5505, format="%.6f")
with col2:
    longitude = st.number_input("Longitude (°)", value=-46.6333, format="%.6f")
with col3:
    altitude_km = st.number_input("Altitude (km)", value=0.0, format="%.2f")

data_input = st.date_input("Data", value=datetime(2025, 5, 2))
data = datetime.combine(data_input, datetime.min.time())

# Botão para calcular
if st.button("Calcular as Componentes Magnéticas"):
    # Cálculo do campo magnético
    Be, Bn, Bu = ppigrf.igrf(longitude, latitude, altitude_km, data)
    
    # Intensidade total e declinação magnética
    Bt = np.sqrt(Be**2 + Bn**2 + Bu**2)
    declinacao = np.degrees(np.arctan2(Be, Bn))

# Exibir resultados
st.subheader("Resultados:")
#st.write(f"**Componente Leste (Be):** {Be.item():.2f} nT")
#st.write(f"**Componente Norte (Bn):** {Bn.item():.2f} nT")
#st.write(f"**Componente Vertical (Bu):** {Bu.item():.2f} nT")
st.write(f"**Intensidade Total (Bt):** {Bt.item():.2f} nT")
st.write(f"**Declinação Magnética:** {declinacao.item():.2f}°")  

  
