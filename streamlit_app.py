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
