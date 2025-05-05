import streamlit as st
import pydeck as pdk

st.set_page_config(layout="wide", page_title="Aplicações Geoespaciais")  # Esta linha deve vir antes de qualquer st.write(), st.title(), etc.

# Sidebar
st.sidebar.title("Aplicações Geoespaciais")
#page = st.sidebar.radio("Aplicações", ["Geografico", "Magnetico"])
st.sidebar.image("Terra.png")
st.sidebar.title("Sobre")
st.sidebar.info("Este aplicativo serve como demonstração prática da aplicação de bibliotecas relevantes para a disciplina de Desenvolvimento de Aplicações Geoespaciais.")
#--------------------------------------------------------------------------------------
st.title("Aplicações Geoespaciais")
st.subheader("Ferramentas para cálculos geodésicos e modelos geomagnéticos")

st.write("🔹 Cálculo Geodésicos - Método Inverso, Direto e Transformação de Coordenadas")  
st.write("🔹 Cálculo Geodésicos - Cálculo de Área")
st.write("🔹 Cálculo da Intensidade e da Declinação do Campo Geomagnético")

#Mapa
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=0, 
        longitude=0,
        zoom=1.5,
        pitch=0,
    ),
    layers=[]  
))








st.markdown("🛈 Escolha uma das ferramentas e utilize a barra lateral para iniciar.")
