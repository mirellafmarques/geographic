import streamlit as st
from datetime import datetime
import numpy as np
from PIL import Image
#magnetic
from datetime import datetime

st.set_page_config(layout="wide", page_title="Geographic")  # Esta linha deve vir antes de qualquer st.write(), st.title(), etc.

# Construindo o Sidebar
st.sidebar.title("Geographic")
#page = st.sidebar.radio("Aplicações", ["Geografico", "Magnetico"])
st.sidebar.image("Earth.jpeg")
st.sidebar.title("About")
st.sidebar.info("Geographic")

import streamlit as st
import pandas as pd
import pydeck as pdk
from pyproj import Transformer
from geographiclib.geodesic import Geodesic

st.title("Cálculo de Área Geodésica")
st.write("Insira ao menos 3 pontos geográficos para visualizar e calcular a área geodésica do polígono.")

# Função para converter lat/lon para UTM
def latlon_to_utm(lat, lon):
    zone_number = int((lon + 180) / 6) + 1
    is_northern = lat >= 0
    utm_crs = f"+proj=utm +zone={zone_number} +datum=WGS84 +units=m +no_defs {'+north' if is_northern else '+south'}"
    transformer = Transformer.from_crs("epsg:4326", utm_crs, always_xy=True)
    easting, northing = transformer.transform(lon, lat)
    return easting, northing, zone_number

# Inicializar session state
if "pontos" not in st.session_state:
    st.session_state["pontos"] = []

# Entrada de dados
with st.form("form_pontos"):
    nome = st.text_input("Nome do ponto")
    lat = st.number_input("Latitude", format="%.6f")
    lon = st.number_input("Longitude", format="%.6f")
    submit = st.form_submit_button("Adicionar")

if submit and nome:
    st.session_state["pontos"].append({"nome": nome, "latitude": lat, "longitude": lon})

# Mostrar dados e processar
if st.session_state["pontos"]:
    df = pd.DataFrame(st.session_state["pontos"])
    df[["easting", "northing", "fuso"]] = df.apply(
        lambda row: pd.Series(latlon_to_utm(row["latitude"], row["longitude"])), axis=1
    )
    st.dataframe(df)

    # Mapa com pontos e polígono
    scatter = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_color=[255, 0, 0, 160],
        get_radius=50000,
    )

    layers = [scatter]

    if len(df) >= 3:
        coords = [[row["longitude"], row["latitude"]] for _, row in df.iterrows()]
        coords.append(coords[0])  # Fecha o polígono
        polygon_layer = pdk.Layer(
            "PolygonLayer",
            data=[{"polygon": coords}],
            get_polygon="polygon",
            get_fill_color=[0, 100, 200, 80],
            get_line_color=[0, 100, 200],
            line_width_min_pixels=2
        )
        layers.append(polygon_layer)

    view = pdk.ViewState(
        latitude=df["latitude"].mean(),
        longitude=df["longitude"].mean(),
        zoom=3
    )

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        layers=layers,
        initial_view_state=view
    ))

    # Cálculo da área com geod.Polygon()
    if len(df) >= 3:
        geod = Geodesic.WGS84
        p = geod.Polygon()
        for _, row in df.iterrows():
            p.AddPoint(row["latitude"], row["longitude"])

        _, perim, area = p.Compute()
        area_km2 = abs(area) / 1e6

        st.success(f"Área Geodésica: {abs(area):,.2f} m² ({area_km2:.4f} km²)")
        st.info(f"Perímetro aproximado: {perim:,.2f} metros")
