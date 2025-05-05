import streamlit as st
import pandas as pd
from pyproj import Transformer
from geographiclib.geodesic import Geodesic
from geographiclib.polygonarea import PolygonArea
import pydeck as pdk

# Função para converter latitude/longitude para UTM
def latlon_to_utm(lat, lon):
    zone_number = int((lon + 180) / 6) + 1
    is_northern = lat >= 0
    utm_crs = f"+proj=utm +zone={zone_number} +datum=WGS84 +units=m +no_defs {'+north' if is_northern else '+south'}"
    transformer = Transformer.from_crs("epsg:4326", utm_crs, always_xy=True)
    easting, northing = transformer.transform(lon, lat)
    return easting, northing, zone_number

# Título
st.title("Cálculo da Área")
st.subheader("Coordenadas Geodésicas")
st.write("Adicione as coordenadas de pelo menos 3 pontos para que a área seja calculada. O sistema de refência utilizado é o WGS84.")

# Inicializar lista de pontos
if "pontos" not in st.session_state:
    st.session_state["pontos"] = []

# Formulário de entrada
with st.form("entrada_pontos"):
    nome = st.text_input("Nome do ponto")
    lat = st.number_input("Latitude", format="%.6f")
    lon = st.number_input("Longitude", format="%.6f")
    submit = st.form_submit_button("Adicionar Ponto")

if submit and nome:
    st.session_state["pontos"].append({"nome": nome, "latitude": lat, "longitude": lon})

# Processar pontos se existirem
if st.session_state["pontos"]:
    df = pd.DataFrame(st.session_state["pontos"])
    df[["easting", "northing", "fuso"]] = df.apply(
        lambda row: pd.Series(latlon_to_utm(row["latitude"], row["longitude"])), axis=1
    )

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

    # Criar lista de coordenadas do polígono (fechando com o 1º ponto no final)
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

    # Cálculo da área geodésica
    if len(df) >= 3:
        #st.subheader("Cálculo de Área")

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


#------------------------------------------------------
import streamlit as st
import pandas as pd
import pydeck as pdk
from pyproj import Transformer
from geographiclib.geodesic import Geodesic

st.title("Cálculo de Área")
st.subheader("Coordenadas UTM")

# Inicializar session_state
if "pontos_utm" not in st.session_state:
    st.session_state["pontos_utm"] = []

# Função para converter UTM para Lat/Lon
def utm_to_latlon(easting, northing, zone_number, hemisphere):
    utm_crs = f"+proj=utm +zone={zone_number} +datum=WGS84 +units=m +no_defs +{'north' if hemisphere == 'N' else 'south'}"
    transformer = Transformer.from_crs(utm_crs, "epsg:4326", always_xy=True)
    lon, lat = transformer.transform(easting, northing)
    return lat, lon

# Formulário para entrada UTM
with st.form("entrada_pontos_utm"):
    nome = st.text_input("Nome do ponto")
    easting = st.number_input("Easting (m)", format="%.2f")
    northing = st.number_input("Northing (m)", format="%.2f")
    zone = st.number_input("Fuso UTM", min_value=1, max_value=60, step=1)
    hemisphere = st.radio("Hemisfério", ["N", "S"])
    submit = st.form_submit_button("Adicionar Ponto")

if submit and nome:
    lat, lon = utm_to_latlon(easting, northing, zone, hemisphere)
    st.session_state["pontos_utm"].append({
        "nome": nome,
        "easting": easting,
        "northing": northing,
        "fuso": zone,
        "hemisfério": hemisphere,
        "latitude": lat,
        "longitude": lon
    })

# Mostrar os pontos inseridos e convertidos
if st.session_state["pontos_utm"]:
    df = pd.DataFrame(st.session_state["pontos_utm"])
    st.subheader("Coordenadas UTM Convertidas para Geodésicas")
    st.dataframe(df)

    # Visualização no mapa com polígono
    st.subheader("Visualização no Mapa")

    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_color=[0, 100, 200, 160],
        get_radius=50000,
        pickable=True
    )

    layers = [scatter_layer]
    if len(df) >= 3:
        polygon_coords = [[row["longitude"], row["latitude"]] for _, row in df.iterrows()]
        polygon_coords.append(polygon_coords[0])  # Fechar o polígono

        polygon_layer = pdk.Layer(
            "PolygonLayer",
            data=[{"polygon": polygon_coords}],
            get_polygon="polygon",
            get_fill_color=[0, 150, 100, 80],
            get_line_color=[0, 150, 100],
            line_width_min_pixels=2
        )
        layers.append(polygon_layer)

    view_state = pdk.ViewState(
        latitude=df["latitude"].mean(),
        longitude=df["longitude"].mean(),
        zoom=4
    )

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=view_state,
        layers=layers
    ))

    # Cálculo da área geodésica
   if len(df) >= 3:
       st.subheader("Cálculo da Área Geodésica do Polígono")

    # Obter pontos (lat, lon) e fechar o polígono
    polygon_points = [(row["latitude"], row["longitude"]) for _, row in df.iterrows()]
    if polygon_points[0] != polygon_points[-1]:
        polygon_points.append(polygon_points[0])  # Fecha o polígono

    geod = Geodesic.WGS84
    poly = geod.Polygon()

    for lat, lon in polygon_points:
        poly.AddPoint(lat, lon)

    area_result = poly.Compute()
    
    # Verificar se o resultado contém 'area'
    if 'area' in area_result:
        area_m2 = abs(area_result['area'])
        area_km2 = area_m2 / 1e6
        st.write(f"Área geodésica: {area_m2:.2f} m² ({area_km2:.4f} km²)")
    else:
        st.warning("Não foi possível calcular a área. Verifique os pontos do polígono.")
