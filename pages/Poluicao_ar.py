import json
from datetime import datetime

import folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from streamlit_folium import folium_static

st.set_page_config(
    page_title="Qualidade do Ar", layout="wide", initial_sidebar_state="expanded"
)

# Carrega o arquivo JSON
list_city = r"Dados/city_coordinates.json"
with open(list_city, "r") as file:
    city_coordinates = json.load(file)

# Token da API OpenWeatherMap
token = "11f2871a588e33e781d6365014dba754"

# Lista para armazenar os dados de cada cidade
data_list = []

# Exibir mensagem de aviso
loading_message = st.warning(
    "Estamos carregando os dados de qualidade do ar para as principais cidades do Brasil utilizando a API da Open Weather. Em apenas alguns segundos, você terá acesso ao mapa atualizado da qualidade do ar!"
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


def add_categorical_legend(map_obj, title, colors, labels):
    legend_html = """
        <div style="position:fixed; bottom:50px; right:50px; z-index:9999; font-size:14px;">
          <p><strong>{}</strong></p>
          {}
        </div>
        """.format(
        title,
        "<br>".join(
            [
                '<i class="fa fa-circle fa-1x" style="color:{}"></i> {}'.format(
                    color, label
                )
                for color, label in zip(colors, labels)
            ]
        ),
    )
    map_obj.get_root().html.add_child(folium.Element(legend_html))


# Exibir o mapa
st.subheader(f"Mapa Qualidade do Ar: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.markdown(
    "O índice de Qualidade do ar (AQI) é gerado através da análise dos poluentes, Monóxido de Carbono (CO), Monóxido de Nitrogênio (NO), Dióxido de Nitrogênio (NO2), Ozônio (O3), Dióxido de Enxofre (SO2), Amônia (NH3), e partículas (PM2.5 e PM10)."
)
st.markdown(
    "Abaixo o mapa do AQI e o gráfico com os valores de cada poluente por cidade!"
)

col1, col2 = st.columns([3.5, 3])

# Exibir o mapa na primeira coluna
with col1:
    # Adiciona a legenda ao mapa
    add_categorical_legend(
        mapa,
        "Qualidade do Ar",
        colors=["#2b8318", "#abdda4", "#ffffbf", "#fdae61", "#d7191c"],
        labels=["Bom", "Razoável", "Moderado", "Ruim", "Muito Ruim"],
    )
    folium_static(mapa)


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

    # Adicionar uma legenda para a linha média
    fig.add_trace(
        go.Scatter(
            x=selected_data["City"],
            y=[average_value] * len(selected_data["City"]),
            mode="lines",
            name="Média",
            line=dict(color="red", width=1, dash="dash"),
        )
    )

    st.plotly_chart(fig)
