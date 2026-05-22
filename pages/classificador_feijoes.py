import streamlit as st
from PIL import Image

# Barra Lateral
barra_lateral = st.sidebar.empty()

st.title("Classificação de Imagens de Grãos de Feijão 🫘")

st.write(
    "Recentemente, enquanto escolhia feijões para cozinhar, fiquei surpreso com a quantidade de grãos estragados que encontrei no pacote. Essa experiência despertou em mim a curiosidade sobre como a tecnologia poderia otimizar esse processo de seleção de grãos, dessa forma desenvolvi um script de classificação de imagens de grãos de feijão usando o tensor flow. "
)

st.write("Abaixo temos os resultados da classificação:")

col1, col2, col3 = st.columns(3)
image1 = Image.open(r"dados/feijoes_classificados1.png")
col1.image(image1)

image2 = Image.open(r"dados/feijoes_classificados2.png")
col2.image(image2)

image3 = Image.open(r"dados/feijoes_classificados3.png")
col3.image(image3)

st.write("Link do repositório: https://github.com/bsensix/classificacao_feijoes")
