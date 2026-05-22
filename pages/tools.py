import streamlit as st
from PIL import Image

st.title("🛠️ Tecnologias e Ferramentas")

imagem1 = Image.open(r"dados/Processamento Armazenamento.jpg")
st.image(imagem1)
