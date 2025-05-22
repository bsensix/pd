import streamlit as st

st.markdown("# Predição de NDVI com Sentinel 1, 2")

st.markdown("""
Este projeto reúne scripts e notebooks para previsão do NDVI (Índice de Vegetação por Diferença Normalizada) utilizando dados dos satélites Sentinel-1, Sentinel-2. O objetivo é integrar diferentes fontes de dados para melhorar a acurácia da predição do NDVI em áreas agrícolas.
""")

st.markdown(
    "[Projeto no GitHub](https://github.com/bsensix/ndvi_prediction_sentinel_123)"
)


st.markdown("## Etapas do Projeto")

st.markdown("""
**Step One: Carregamento e Download de Dados**  
- Carregar Pontos no Banco de Dados: Os pontos de interesse são carregados no banco de dados PostgreSQL.  
- Download de Dados Sentinel: Utiliza a API do Google Earth Engine (GEE) para baixar dados do Sentinel-1 e Sentinel-2.

**Step Two: Treinamento do Modelo**  
- Análise Exploratória: Identificação de outliers e análise de distribuição dos dados.  
- Treinamento do Modelo: Um modelo de regressão polinomial é treinado para prever o NDVI com base em variáveis como cr_s1, ndvi_s2_moving_avg e o julian_day.

**Step Three: Previsão e Geração de Rasters**  
- Geração de Previsões: O modelo treinado é usado para prever valores de NDVI para cada ponto e data.  
- Criação de Rasters: As previsões são interpoladas espacialmente (IDW) para gerar arquivos raster .tif.

**Step Four: Relatórios**  
- Relatório final: Analisando os dados finais, identificando os pontos forte e desafios da ideia.
""")
