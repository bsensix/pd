import streamlit as st
from PIL import Image

# Barra Lateral
barra_lateral = st.sidebar.empty()

st.title("Mapas")

with st.expander("🔥 Análise de Incêndio"):
    st.write(
        "Identificação do momento inicial de um incêndio usando imagens do Sentinel-2"
    )
    image = Image.open(r"dados/incendio_dia_12.png")
    st.image(image)

with st.expander("🗺️ Uso e Classificação do Solo"):
    st.write("Uso e Classificação do Solo de um Bacia Hidrográfica")
    image = Image.open(r"dados/mapa_uso_do_solo.png")
    st.image(image)

    st.write("Uso e Classificação do Solo do Perímetro Urbano de um Rio")
    image = Image.open(r"dados/mapa_uso_do_solo_2.png")
    st.image(image)

with st.expander("🛰️ Índices Espectrais"):
    st.write("Análise da Severidade de um Incêndio através do Índice dNBR")
    image = Image.open(r"dados/dnbr.png")
    st.image(image)

    st.write(
        "Análise da Abosrção de CO2 pela vagetação em vegetação saudável e vegetação queimada"
    )
    image = Image.open(r"dados/antes_depois_co2.png")
    st.image(image)

with st.expander("🏙️ Mapas Cidades"):
    st.write("Capitólio - MG")
    image = Image.open(r"dados/mapa_capitolio.jpeg")
    st.image(image)

    st.write("Uberlândia - MG")
    image = Image.open(r"dados/udia.jpeg")
    st.image(image)

    st.write("Franca - SP")
    image = Image.open(r"dados/franca.jpeg")
    st.image(image)


# In[ ]:
