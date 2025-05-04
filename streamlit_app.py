import streamlit as st
import pandas as pd
from pyproj import Transformer
import pydeck as pdk
from geographiclib.geodesic import Geodesic


# Função para converter latitude/longitude para UTM
def latlon_to_utm(lat, lon):
    zone_number = int((lon + 180) / 6) + 1
    is_northern = lat >= 0
    utm_crs = f"+proj=utm +zone={zone_number} +datum=WGS84 +units=m +no_defs {'+north' if is_northern else '+south'}"
    transformer = Transformer.from_crs("epsg:4326", utm_crs, always_xy=True)
    easting, northing = transformer.transform(lon, lat)
    return easting, northing, zone_number

st.title("Entrada de Pontos Geográficos e Conversão para UTM com Visualização no Mapa")

if "pontos" not in st.session_state:
    st.session_state["pontos"] = []

# Entrada de coordenadas
with st.form("entrada_pontos"):
    nome = st.text_input("Nome do ponto")
    lat = st.number_input("Latitude", format="%.6f")
    lon = st.number_input("Longitude", format="%.6f")
    submit = st.form_submit_button("Adicionar Ponto")

if submit and nome:
    st.session_state["pontos"].append({"nome": nome, "latitude": lat, "longitude": lon})

# Mostrar os pontos inseridos
if st.session_state["pontos"]:
    df = pd.DataFrame(st.session_state["pontos"])
    df[["easting", "northing", "fuso"]] = df.apply(lambda row: pd.Series(latlon_to_utm(row["latitude"], row["longitude"])), axis=1)
    st.write("Coordenadas convertidas:")
    st.dataframe(df)

    # Exibir mapa com os pontos
    layers = [
        pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position=["longitude", "latitude"],
            get_color=[200, 30, 0, 160],
            get_radius=50000,
            pickable=True,
            auto_highlight=True,
        )
    ]

    map = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=df["latitude"].mean(),
            longitude=df["longitude"].mean(),
            zoom=3,
            pitch=0,
        ),
        layers=layers,
    )

    st.pydeck_chart(map)

    # Escolher dois pontos para calcular distância
    pontos_nomes = df["nome"].tolist()
    ponto1 = st.selectbox("Escolha o ponto de origem", pontos_nomes)
    ponto2 = st.selectbox("Escolha o ponto de destino", pontos_nomes)

    if ponto1 != ponto2:
        coord1 = df[df["nome"] == ponto1].iloc[0]
        coord2 = df[df["nome"] == ponto2].iloc[0]

        # Calcular a distância e o azimute
        geod = Geodesic.WGS84
        g = geod.Inverse(coord1["latitude"], coord1["longitude"], coord2["latitude"], coord2["longitude"])

        st.write(f"Distância entre {ponto1} e {ponto2}: {g['s12']:.2f} metros")
        st.write(f"Azimute: {g['azi1']:.2f}°")


#------------------------------------
