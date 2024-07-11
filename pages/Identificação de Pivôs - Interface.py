import cv2
import matplotlib.pyplot as plt
import numpy as np
import rasterio
import streamlit as st
from matplotlib import cm

st.title("Identificação de Pivôs")
st.markdown(
    "Esse script utiliza de uma imagem de NDVI (Indice de Vegetação por Diferença Normalizada), para identificar Pivôs de Irrigação, através da Transformada de Hough da biblioteca OpenCV."
)
st.markdown(
    "Um dos parâmetros e as escolhas dos raios dos Pivôes, abaixo você pode definir o intervalo dos círculos que vão ser selecionados:"
)
imagem_selecionada = r"Dados/NDVI.tif"

col1, col2 = st.columns(2)

raio_min = col1.number_input("Raio Menor", value=20, step=1, format="%d")
raio_max = col2.number_input("Raio Maior", value=40, step=1, format="%d")

imagem = rasterio.open(imagem_selecionada)
im1 = imagem.read(1) * 255

# Filtro Gaussiano
im = cv2.GaussianBlur(im1, (3, 3), 0)

# Transformar para int8
im = im.astype("uint8")

# Filtro de canny
bordas = cv2.Canny(im, 100, 200)

# Transformada de Hough
pivos = cv2.HoughCircles(
    bordas,
    cv2.HOUGH_GRADIENT,
    1,
    20,
    param1=300,
    param2=20,
    minRadius=raio_min,
    maxRadius=raio_max,
)

# Plotar Figura
cm = plt.get_cmap("RdYlGn")
saida = cm(im)
saida = saida[:, :, 0:3] * 255
ndvi3 = saida.astype(np.uint8)

if pivos is not None:
    pivos = np.round(pivos[0, :]).astype("int")
    for x, y, r in pivos:
        cv2.circle(ndvi3, (x, y), r, (0, 0, 0), 4)

fig2 = plt.figure(figsize=(12, 12))
plt.imshow(ndvi3, cmap="RdYlGn")
plt.axis("off")
st.pyplot(fig2)
