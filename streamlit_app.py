#Importando as Bibliotecas
import streamlit as st
from datetime import datetime
from streamlit_folium import st_folium
import folium
import folium
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.plot import reshape_as_image
import numpy as np
from PIL import Image
#magnetic
from datetime import datetime
import ppigrf
import pydeck as pdk

st.set_page_config(layout="wide")  # Esta linha deve vir antes de qualquer st.write(), st.title(), etc.

# Construindo o Sidebar
st.sidebar.title("Geographic")
page = st.sidebar.radio("Aplicações", ["Home", "Magnetic"])

logo = "Earth.jpeg"
st.sidebar.image(logo)

st.sidebar.title("About")
st.sidebar.info("Geographic")


# Conteúdo condicional
if page == "Home":
    st.title("Geographic")
    st.write("Bem-vindo ao aplicativo Geographic!")


elif page == "Magnetic":
    st.title("Aplicações Magnéticas")
    st.write("Aqui você pode explorar as funcionalidades relacionadas ao campo magnético.")
    # Coloque seu código da seção 'Magnetic' aqui
    # "https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml?useFullSite=true"

# Dados iniciais para exibir no mapa (São Paulo)
default_lat = -22.4018
default_lon = -43.657

# Criar um ponto inicial no mapa
selected_location = st.session_state.get("selected_location", [default_lat, default_lon])

# Mostrar mapa com ponto
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=selected_location[0],
        longitude=selected_location[1],
        zoom=3,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=[{"position": [selected_location[1], selected_location[0]]}],
            get_position='position',
            get_color='[200, 30, 0, 160]',
            get_radius=50000,
        ),
    ],
))

# Entrada manual ou vinda do mapa (editável)
col1, col2, col3 = st.columns(3)

with col1:
    latitude = st.number_input("Latitude (°)", value=selected_location[0], format="%.6f")

with col2:
    longitude = st.number_input("Longitude (°)", value=selected_location[1], format="%.6f")

with col3:
    altitude_m = st.number_input("Altitude (m)", value=0.0, format="%.2f")

altitude_km = altitude_m / 1000.0
data_input = st.date_input("Data", value=datetime(2025, 5, 2))
data = datetime.combine(data_input, datetime.min.time())

if st.button("Calcular Campo Magnético"):
    Be, Bn, Bu = ppigrf.igrf(longitude, latitude, altitude_km, data)
    Bt = np.sqrt(Be**2 + Bn**2 + Bu**2)
    declinacao = np.degrees(np.arctan2(Be, Bn))

    st.subheader("Resultados:")
    #st.write(f"**Componente Leste (Be):** {Be.item():.2f} nT")
    #st.write(f"**Componente Norte (Bn):** {Bn.item():.2f} nT")
    #st.write(f"**Componente Vertical (Bu):** {Bu.item():.2f} nT")
    st.write(f"**Intensidade Total (Bt):** {Bt.item():.2f} nT")
    st.write(f"**Declinação Magnética:** {declinacao.item():.2f}°")


#Comparação Historica das Componentes Magnéticas
#https://www.ngdc.noaa.gov/geomag/magfield-wist/

# Mudança da Da Declinação
st.subheader("Mudança da Declinação Magnética em 10 anos")
image3 = Image.open("Change in Declination over 10 y.jpg")  # Altere o caminho para sua imagem
st.image(image3, caption="", use_container_width=True)

import streamlit as st
from streamlit_image_comparison import image_comparison

st.subheader("Mudança da Intensidade Total (F) do Campo Geomagnético em 100 anos")

# Comparação de imagens geomagnéticas entre 1920 e 2020
image_comparison(
    img1="/workspaces/geographic/F_map_mf_1920.jpg",  # Imagem do campo geomagnético de 1920
    img2="/workspaces/geographic/F_map_mf_2020.jpg",  # Imagem do campo geomagnético de 2020
)


