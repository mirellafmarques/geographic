import streamlit as st
import pandas as pd
from geographiclib.geodesic import Geodesic
from geographiclib.polygonarea import PolygonArea
import pydeck as pdk

# Título
st.title("Cálculo da Área")
st.subheader("Coordenadas Geodésicas")
st.write("Adicione as coordenadas de pelo menos 3 pontos para que a área seja calculada. O sistema de referência utilizado é o WGS84.")

# Lista de pontos
if "pontos" not in st.session_state:
    st.session_state["pontos"] = []

# Entrada dos dados
with st.form("entrada_pontos"):
    nome = st.text_input("Nome do ponto")
    lat = st.number_input("Latitude", format="%.6f")
    lon = st.number_input("Longitude", format="%.6f")
    submit = st.form_submit_button("Adicionar Ponto")

if submit and nome:
    st.session_state["pontos"].append({"nome": nome, "latitude": lat, "longitude": lon})

# Processar pontos
if st.session_state["pontos"]:
    df = pd.DataFrame(st.session_state["pontos"])

    st.subheader("Tabela de Pontos")
    st.dataframe(df)

    st.subheader("Visualização no Mapa")

    # Camada de pontos
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_color=[200, 30, 0, 160],
        get_radius=5000,
        pickable=True,
    )

    # Criar lista de coordenadas
    if len(df) >= 3:
        polygon_coords = [[row["longitude"], row["latitude"]] for _, row in df.iterrows()]
        polygon_coords.append(polygon_coords[0])  # Fecha o polígono

        polygon_layer = pdk.Layer(
            "PolygonLayer",
            data=[{
                "polygon": polygon_coords,
                "name": "Área"
            }],
            get_polygon="polygon",
            get_fill_color=[0, 100, 255, 80],
            get_line_color=[0, 100, 255],
            line_width_min_pixels=1,
            pickable=True,
        )

        layers = [scatter_layer, polygon_layer]
    else:
        layers = [scatter_layer]

    view_state = pdk.ViewState(
        latitude=df["latitude"].mean(),
        longitude=df["longitude"].mean(),
        zoom=3,
        pitch=0,
    )

    deck = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        layers=layers,
        initial_view_state=view_state
    )
    st.pydeck_chart(deck)

    # Cálculo da área
    if len(df) >= 3:
        st.write("Pontos usados no cálculo de área:")
        st.dataframe(df[["nome", "latitude", "longitude"]])

        polygon_points = [(row["latitude"], row["longitude"]) for _, row in df.iterrows()]
        geod = Geodesic.WGS84
        polygon = PolygonArea(geod, False)

        for lat, lon in polygon_points:
            polygon.AddPoint(lat, lon)

        _, _, area = polygon.Compute(False, True)
        area_m2 = abs(area)
        area_km2 = area_m2 / 1e6

        st.success(f"Área Geodésica: {area_m2:,.2f} m² ({area_km2:,.4f} km²)")
