import streamlit as st
from PIL import Image

# Barra Lateral
barra_lateral = st.sidebar.empty()

st.title("Mapas")

with st.expander("🔥 Análise de Incêndio"):
    st.write(
        "Identificação do momento inicial de um incêndio usando imagens do Sentinel-2"
    )
    image = Image.open(r"Dados/INCENDIO_DIA_12.png")
    st.image(image)

with st.expander("🗺️ Uso e Classificação do Solo"):
    st.write("Uso e Classificação do Solo de um Bacia Hidrográfica")
    image = Image.open(r"Dados/MAPA USO DO SOLO.png")
    st.image(image)

    st.write("Uso e Classificação do Solo do Perímetro Urbano de um Rio")
    image = Image.open(r"Dados/MAPA USO DO SOLO - .png")
    st.image(image)

with st.expander("🛰️ Índices Espectrais"):
    st.write("Análise da Severidade de um Incêndio através do Índice dNBR")
    image = Image.open(r"Dados/dNBR.png")
    st.image(image)

    st.write(
        "Análise da Abosrção de CO2 pela vagetação em vegetação saudável e vegetação queimada"
    )
    image = Image.open(r"Dados/ANTES_DEPOIS_CO2.png")
    st.image(image)


# In[ ]:
