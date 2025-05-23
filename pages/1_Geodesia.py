import streamlit as st
import pandas as pd
import pydeck as pdk
from geographiclib.geodesic import Geodesic

st.title("Aplicações Geodésicas")
st.subheader("Cálculo Geodésico Inverso")
st.write("Ao definir coordenadas no Rio de Janeiro e em Buenos Aires, este exemplo calcula a distância e a linha de rumo entre elas. Esse cálculo é fundamental para o planejamento eficiente de rotas na navegação aérea e marítima. O sistema de referência utilizado é o WGS84.")
st.write("Para esse cálculo, foi utilizado o método geodésico inverso, que emprega as coordenadas geográficas para determinar a distância e o azimute entre dois pontos.")

# Pontos fixos: Rio de Janeiro e Buenos Aires
latitude_origem = -22.9068
longitude_origem = -43.1729
latitude_destino = -34.6037
longitude_destino = -58.3816

# Cálculo geodésico inverso
geod = Geodesic.WGS84
npts = 50
points = [(longitude_origem, latitude_origem)]

g = geod.Inverse(latitude_origem, longitude_origem, latitude_destino, longitude_destino)
dist_rumo = g['s12']
azi1 = (g['azi1'] + 360) % 360

# Gerar pontos intermediários na linha
for i in range(1, npts + 1):
    s = dist_rumo * i / (npts + 1)
    p = geod.Direct(latitude_origem, longitude_origem, azi1, s)
    points.append((p['lon2'], p['lat2']))

points.append((longitude_destino, latitude_destino))

# Criar DataFrame
data_segments = []
for i in range(len(points) - 1):
    data_segments.append({
        'start': points[i],
        'end': points[i+1],
        'dist_total': f"{dist_rumo:.2f} m",
        'azimute_inicial': f"{azi1:.2f}°"
    })
df_segments = pd.DataFrame(data_segments)

# Camadas
line_layer = pdk.Layer(
    "LineLayer",
    data=df_segments,
    get_source_position="start",
    get_target_position="end",
    get_color=[255, 0, 0],
    get_width=5,
    pickable=True
)

point_data = pd.DataFrame({
    'coordinates': [(longitude_origem, latitude_origem), (longitude_destino, latitude_destino)],
    'label': ['Origem', 'Destino']
})

point_layer = pdk.Layer(
    "ScatterplotLayer",
    data=point_data,
    get_position="coordinates",
    get_radius=100000,
    get_color=[255, 0, 0],
    pickable=True
)

# Mapa
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

st.pydeck_chart(deck)
st.write(f"**Distância entre os pontos:** {dist_rumo / 1000:.2f} km")
st.write(f"**Azimute (BR-ARG):** {azi1:.2f}°")



# --------------------------------------------------------
st.subheader("Calculadora")
st.write("Primeiro, insira os pontos de interesse. Depois que o usuário selecionar os pontos, a distância e o azimute entre eles serão calculados e exibidos.")

if "pontos" not in st.session_state:
    st.session_state["pontos"] = []

with st.form("entrada_pontos"):
    nome = st.text_input("Nome do ponto")
    lat = st.number_input("Latitude", format="%.6f")
    lon = st.number_input("Longitude", format="%.6f")
    submit = st.form_submit_button("Adicionar Ponto")

if submit and nome:
    st.session_state["pontos"].append({"nome": nome, "latitude": lat, "longitude": lon})

# Mostrar pontos
if st.session_state["pontos"]:
    df = pd.DataFrame(st.session_state["pontos"])
    st.write("Pontos inseridos:")
    st.dataframe(df)

    # Exibir pontos no mapa
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

    # Seleção de dois pontos
    pontos_nomes = df["nome"].tolist()
    ponto1 = st.selectbox("Escolha o ponto de origem", pontos_nomes)
    ponto2 = st.selectbox("Escolha o ponto de destino", pontos_nomes)

    if ponto1 != ponto2:
        coord1 = df[df["nome"] == ponto1].iloc[0]
        coord2 = df[df["nome"] == ponto2].iloc[0]

        # Calcular distância e azimute
        g = geod.Inverse(coord1["latitude"], coord1["longitude"], coord2["latitude"], coord2["longitude"])

        st.write(f"Distância entre {ponto1} e {ponto2}: {g['s12']:.2f} metros")
        st.write(f"Azimute: {(g['azi1'] + 360) % 360:.2f}°")

        # Linha no mapa
        linha_df = pd.DataFrame([{
            "origem_lon": coord1["longitude"],
            "origem_lat": coord1["latitude"],
            "destino_lon": coord2["longitude"],
            "destino_lat": coord2["latitude"],
        }])

        linha_layer = pdk.Layer(
            "LineLayer",
            data=linha_df,
            get_source_position=["origem_lon", "origem_lat"],
            get_target_position=["destino_lon", "destino_lat"],
            get_color=[0, 0, 255],
            get_width=5,
        )

        layers.append(linha_layer)

        map = pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(
                latitude=df["latitude"].mean(),
                longitude=df["longitude"].mean(),
                zoom=3,
                pitch=0,
            ),
            layers=layers,
            tooltip={"text": "{nome}"}
        )

        st.pydeck_chart(map)



# ------------------------------------
import streamlit as st
import pydeck as pdk
from geographiclib.geodesic import Geodesic
import pandas as pd

# Configuração da Página
st.subheader("Cálculo Geodésico Direto")

st.markdown("""
Esta aplicação utiliza o método geodésico direto, que calcula o ponto de chegada a partir das coordenadas de um ponto inicial, de uma distância e de um azimute (ângulo de direção). O ponto de partida fixo está localizado no Aeroporto Internacional do Rio de Janeiro.""")

# Entradas do Usuário
distance = st.number_input("Distância (em metros)", min_value=1, max_value=1_000_000, value=100_000)
azimuth = st.number_input("Azimute (graus)", min_value=0, max_value=360, value=90)

# Ponto Inicial Fixo RJ
lat1 = -22.8052698
lon1 = -43.2566277

# Cálculo Geodésico Direto
geod = Geodesic.WGS84
result = geod.Direct(lat1, lon1, azimuth, distance)
lat2 = result['lat2']
lon2 = result['lon2']

# Dados para o Mapa
df = pd.DataFrame([
    {"lat": lat1, "lon": lon1, "label": "Ponto Inicial (Brasília)"},
    {"lat": lat2, "lon": lon2, "label": f"Ponto Final ({distance/1000:.1f} km, {azimuth}°)"}
])

# Camada de pontos
point_layer = pdk.Layer(
    "ScatterplotLayer",
    df,
    get_position='[lon, lat]',
    get_fill_color='[200, 30, 0, 160]',
    get_radius=50,
    pickable=True
)

# Camada de linha
line_layer = pdk.Layer(
    "LineLayer",
    pd.DataFrame([{
        "source_position": [lon1, lat1],
        "target_position": [lon2, lat2]
    }]),
    get_source_position="source_position",
    get_target_position="target_position",
    get_width=4,
    get_color=[0, 100, 255],
    pickable=False
)

# View inicial
view_state = pdk.ViewState(
    latitude=(lat1 + lat2) / 2,
    longitude=(lon1 + lon2) / 2,
    zoom=7,
    pitch=0
)

# Renderizar o mapa
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v10",  # Tema claro
    layers=[point_layer, line_layer],
    initial_view_state=view_state,
    tooltip={"text": "{label}"}
))

# Mostrar resultado
st.write(f"**Latitude:** {lat2:.6f}")
st.write(f"**Longitude:** {lon2:.6f}")
