import json
from datetime import datetime

import folium
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from streamlit_folium import folium_static

st.set_page_config(
    page_title="Qualidade do Ar", layout="wide", initial_sidebar_state="expanded"
)

# Carrega o arquivo JSON
list_city = r"C:\Users\sensix\Desktop\PESSOAL\PESSOAL\PORTIFOLIO DATA SCIENCE\pd\pd\Dados\city_coordinates.json"
with open(list_city, "r") as file:
    city_coordinates = json.load(file)

# Token da API OpenWeatherMap
token = "11f2871a588e33e781d6365014dba754"

# Lista para armazenar os dados de cada cidade
data_list = []

# Exibir mensagem de aviso
loading_message = st.warning(
    "Estamos carregando os dados da qualidade do ar para as principais cidades do Brasil utilizando a API da Open Weather. Em apenas alguns segundos, você terá acesso ao mapa atualizado da qualidade do ar!"
)

# Inicia o loop sobre as chaves do dicionário city_coordinates
for city, coordinates in city_coordinates.items():
    lat = coordinates["latitude"]
    lon = coordinates["longitude"]

    # Faz a solicitação para a API do OpenWeatherMap
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={token}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        aqi = data["list"][0]["main"]
        components = data["list"][0]["components"]
        dt = datetime.fromtimestamp(data["list"][0]["dt"])

        # Adiciona os dados à lista
        data_list.append(
            {
                "City": city,
                "Latitude": lat,
                "Longitude": lon,
                "Timestamp": dt,
                "AQI": aqi.get("aqi", None),
                "CO": components.get("co", None),
                "NO": components.get("no", None),
                "NO2": components.get("no2", None),
                "O3": components.get("o3", None),
                "SO2": components.get("so2", None),
                "PM2.5": components.get("pm2_5", None),
                "PM10": components.get("pm10", None),
                "NH3": components.get("nh3", None),
            }
        )
    else:
        print(f"Falha na solicitação para {city}")

# Remover a mensagem de aviso após o mapa ser exibido
loading_message.empty()

# Cria o DataFrame
df_final = pd.DataFrame(data_list)

# Criar um mapa centrado no Brasil
mapa = folium.Map(location=[-14.235, -51.9253], zoom_start=4)

# Converter os dados de AQI para uma lista de tuplas (latitude, longitude, AQI)
dados_aqi = df_final[["Latitude", "Longitude", "AQI"]].dropna()
dados_aqi = dados_aqi.values.tolist()

# Adicionar o mapa de calor ao mapa
folium.plugins.HeatMap(
    dados_aqi,
    gradient={
        0.2: "#2b8318",
        0.4: "#abdda4",
        0.6: "#ffffbf",
        0.8: "#fdae61",
        0.1: "#d7191c",
    },
    radius=20,
    blur=15,
).add_to(mapa)

# Exibir o mapa
st.subheader(f"Mapa Qualidade do Ar: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.markdown(
    "O índice de Qualidade do ar (AQI) é gerado através da análise dos poluentes, Monóxido de Carbono (CO), Monóxido de Nitrogênio (NO), Dióxido de Nitrogênio (NO2), Ozônio (O3), Dióxido de Enxofre (SO2), Amônia (NH3), e partículas (PM2.5 e PM10)."
)

col1, col2 = st.columns([2, 3])

# Exibir o mapa na primeira coluna
with col1:
    folium_static(mapa)
    # Exibir a legenda
    st.markdown(
        """
        <div style="position: fixed; bottom: 210px; left: 100px; background-color: rgba(195, 195, 195,0.45);
        border-radius: 5px; padding: 10px; z-index: 1000; font-size: 14px;">
        <p><strong>Legenda:</strong></p>
        <p><span style="color: #2b8318;">Bom</span> </p>
        <p><span style="color: #abdda4;">Razóavel</span> </p>
        <p><span style="color: #ffffbf;">Moderado</span> </p>
        <p><span style="color: #fdae61;">Ruim</span> </p>
        <p><span style="color: #d7191c;">Muito Ruim</span> </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col2:
    df_final = df_final[
        ["City", "AQI", "CO", "NO", "NO2", "O3", "SO2", "PM2.5", "PM10", "NH3"]
    ]

    # Criar DataFrame longo e dicionário de DataFrames filtrados
    df_final_long = df_final.melt(
        id_vars="City", var_name="Poluente", value_name="Valor"
    )
    filtered_dfs = {
        poluente: df_final_long[df_final_long["Poluente"] == poluente]
        for poluente in df_final_long["Poluente"].unique()
    }

    # Adicionar um filtro para selecionar o poluente
    selected_poluente = st.selectbox(
        "Selecione um poluente", df_final_long["Poluente"].unique()
    )

    # Plotar o gráfico de barras
    selected_data = filtered_dfs[selected_poluente]
    fig = px.bar(
        selected_data,
        x="City",
        y="Valor",
        color="Poluente",
        barmode="group",
        labels={"City": "Cidade", "Valor": "Valor", "Poluente": "Poluente"},
        title=f"Dados de Poluição para {selected_poluente} por Cidade",
    )

    # Adicionar uma linha média para indicar a média dos valores desse poluente em todas as cidades
    average_value = selected_data["Valor"].mean()
    fig.add_hline(
        y=average_value,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Média: {average_value:.2f}",
        annotation_position="bottom right",
    )

    st.plotly_chart(fig)
