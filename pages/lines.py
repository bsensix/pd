import matplotlib.pyplot as plt
import numpy as np
import rasterio
import streamlit as st
from matplotlib import cm, gridspec
from skimage import feature
from skimage.morphology import closing, dilation, skeletonize, square
from skimage.transform import hough_line, hough_line_peaks

input_image_path = r"Dados/cana2.tif"
src = rasterio.open(input_image_path)
red_band = src.read(1)
green_band = src.read(2)
blue_band = src.read(3)

# Indice VARI
vari = (green_band - red_band) / (green_band + red_band - blue_band + 0.0001)
threshold = 0.1
condition = vari > threshold

# Matriz binária com base na condição
binary_result = np.zeros_like(red_band, dtype=np.uint8)
binary_result[condition] = 1

binary_result = closing(binary_result, square(1))
binary_result = dilation(binary_result, square(6))

skeleton = skeletonize(binary_result == 0)
contours = feature.canny(binary_result.astype(bool))


st.title("Detecção de Linhas")
st.markdown(
    """
    A Transformada de Hough é uma técnica de processamento de imagens usada para detectar formas, como linhas, em imagens digitais.
    Primeiro, segmentamos os pixels da cultura usando o índice VARI. Em seguida, aplicamos técnicas morfológicas para melhorar a segmentação e a indentificação das linhas.

    """
)
fig, (ax0, ax1, ax2) = plt.subplots(
    nrows=1, ncols=3, figsize=(18, 6), sharex=True, sharey=True
)
ax0.imshow(np.dstack((red_band, green_band, blue_band)))
ax0.axis("off")
ax0.set_title("Imagem Original", fontsize=20)

ax1.imshow(binary_result, cmap=plt.cm.gray)
ax1.axis("off")
ax1.set_title("Segmentação", fontsize=20)

ax2.imshow(skeleton, cmap=plt.cm.gray)
ax2.axis("off")
ax2.set_title("Esqueletização", fontsize=20)

fig.tight_layout()
st.pyplot(fig)

selImage = contours
precision = 2
tested_angles = np.linspace(-np.pi / 2, np.pi / 2, int(180 / precision), endpoint=False)
h, theta, d = hough_line(selImage, theta=tested_angles)

angle_range = st.slider(
    "Selecione o intervalo de ângulos:",
    min_value=-90.0,
    max_value=90.0,
    value=(54.0, 74.0),
    step=1.0,
)


# Função para exibir as linhas filtradas pelos ângulos
def plot_filtered_lines(angle_range):
    fig = plt.figure(figsize=(18, 8))
    gs = gridspec.GridSpec(1, 2)

    ax1 = plt.subplot(gs[0])
    angle_step = 0.5 * np.diff(theta).mean()
    d_step = 0.5 * np.diff(d).mean()
    bounds = [
        np.rad2deg(theta[0] - angle_step),
        np.rad2deg(theta[-1] + angle_step),
        d[-1] + d_step,
        d[0] - d_step,
    ]
    ax1.imshow(np.log(1 + h), extent=bounds, cmap=cm.YlGn, aspect=1 / 1.5)
    ax1.set_title("Hough Transform")
    ax1.set_xlabel("Angles (degrees)")
    ax1.set_ylabel("Distance (pixels)")
    ax1.axis("image")
    ax1.set_aspect(0.2)

    ax2 = plt.subplot(gs[1])
    ax2.imshow(np.dstack((red_band, green_band, blue_band)))
    ax2.set_ylim((selImage.shape[0], 0))
    ax2.set_xlim((0, selImage.shape[1]))
    ax2.set_axis_off()
    ax2.set_title("Linhas encontradas")

    for _, angle, dist in zip(*hough_line_peaks(h, theta, d)):
        angle_deg = np.rad2deg(angle)
        if angle_range[0] <= angle_deg <= angle_range[1]:
            (x0, y0) = dist * np.array([np.cos(angle), np.sin(angle)])
            ax2.axline((x0, y0), slope=np.tan(angle + np.pi / 2), color="blue")

    plt.tight_layout()
    st.pyplot(fig)


plot_filtered_lines(angle_range)
