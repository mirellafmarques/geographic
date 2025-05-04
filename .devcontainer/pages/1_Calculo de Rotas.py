import streamlit as st
import pandas as pd
from pyproj import Transformer
import pydeck as pdk
from geographiclib.geodesic import Geodesic

#"mapbox://styles/mapbox/satellite-v9"

st.title("Cálculo de Rotas")
#st.subheader("Exemplo")
st.write("Ao definir coordenadas no Rio de Janeiro e em Buenos Aires, este exemplo calcula a distância e a linha de rumo entre elas. Esse cálculo é fundamental para o planejamento eficiente de rotas na navegação aérea e marítima.")
         
# Definir Pontos de Origem e Destino (fixos)
latitude_origem = -22.9068  # Rio de Janeiro
longitude_origem = -43.1729
latitude_destino = -34.6037  # Buenos Aires
longitude_destino = -58.3816

# Calcular geodésica
geod = Geodesic.WGS84
npts = 50
points = [(longitude_origem, latitude_origem)]

# Distância e azimute inicial
g = geod.Inverse(latitude_origem, longitude_origem, latitude_destino, longitude_destino)
dist_rumo = g['s12']
azi1 = (g['azi1']+ 360) % 360

# Gerar pontos ao longo da linha de rumo
for i in range(1, npts + 1):
    s = dist_rumo * i / (npts + 1)
    p = geod.Direct(latitude_origem, longitude_origem, azi1, s)
    points.append((p['lon2'], p['lat2']))

points.append((longitude_destino, latitude_destino))

# Criar DataFrame de segmentos da linha
data_segments = []
for i in range(len(points) - 1):
    data_segments.append({
        'start': points[i],
        'end': points[i+1],
        'dist_total': f"{dist_rumo:.2f} m",
        'azimute_inicial': f"{azi1:.2f}°"
    })
df_segments = pd.DataFrame(data_segments)

# Camada de linhas com tooltip
line_layer = pdk.Layer(
    type="LineLayer",
    data=df_segments,
    get_source_position="start",
    get_target_position="end",
    get_color=[255, 0, 0],
    get_width=5,
    pickable=True
)

# Pontos origem/destino
point_data = pd.DataFrame({
    'coordinates': [(longitude_origem, latitude_origem), (longitude_destino, latitude_destino)],
    'label': ['Origem', 'Destino']
})

point_layer = pdk.Layer(
    type="ScatterplotLayer",
    data=point_data,
    get_position='coordinates',
    get_radius=100000,
    get_color=[255, 0, 0], 
    pickable=True
)

# Visualização do mapa com estilo Light
view_state = pdk.ViewState(
    latitude=(latitude_origem + latitude_destino) / 2,
    longitude=(longitude_origem + longitude_destino) / 2,
    zoom=3,
    pitch=0
)

deck = pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    layers=[line_layer, point_layer],
    initial_view_state=view_state
)

# Renderizar o mapa no Streamlit
st.pydeck_chart(deck)

# Mostrar resultados
st.write(f"**Distância entre os pontos:** {dist_rumo / 1000:.2f} km")
st.write(f"**Azimute (BR-ARG):** {azi1:.2f}°")





#------------------------------------------------------------------------------
# Função para converter latitude/longitude para UTM
def latlon_to_utm(lat, lon):
    zone_number = int((lon + 180) / 6) + 1
    is_northern = lat >= 0
    utm_crs = f"+proj=utm +zone={zone_number} +datum=WGS84 +units=m +no_defs {'+north' if is_northern else '+south'}"
    transformer = Transformer.from_crs("epsg:4326", utm_crs, always_xy=True)
    easting, northing = transformer.transform(lon, lat)
    return easting, northing, zone_number

#st.title("Cálculo de Rotas sobre uma Linha de Rumo")
st.subheader("Demonstração")
st.write("Primeiro, insira os pontos de interesse. O sistema realizará a transformação para o sistema UTM. Depois que o usuário selecionar os pontos, a distância e o azimute entre eles serão calculados e exibidos.")

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
    df[["este", "norte", "fuso"]] = df.apply(lambda row: pd.Series(latlon_to_utm(row["latitude"], row["longitude"])), axis=1)
    st.write("Coordenadas Transformadas:")
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
        st.write(f"Azimute: {(g['azi1']+ 360) % 360:.2f}°")


#------------------------------------
