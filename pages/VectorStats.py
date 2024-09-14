import streamlit as st
from PIL import Image

st.title("Vector Stats - Plugin QGIS")

st.write("Plugin para calcular estatísticas de uma camada vetorial, e gerar gráficos.")

imagem = Image.open(r"Dados/medidas_estatisticas.png")
st.image(imagem)

st.write("Link do repositório: https://github.com/bsensix/VectorStats")
