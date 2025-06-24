import streamlit as st

p1 = st.Page("pages/Sobre Mim.py", title="Breno Nunes", icon=":material/home:")
p2 = st.Page("pages/Mapas.py", title="Mapas", icon=":material/map:")
p3 = st.Page(
    "pages/Página - GEE - Download de Imagens.py",
    title="Download de Imagens no GEE",
    icon=":material/travel_explore:",
)
p4 = st.Page(
    "pages/Classificador_feijoes.py",
    title="Feijões Estragados - Tensor Flow",
    icon=":material/workspaces:",
)
p5 = st.Page(
    "pages/Identificação de Pivôs - Interface.py",
    title="Identificação de Círculos - Open CV",
    icon=":material/radio_button_unchecked:",
)

p6 = st.Page(
    "pages/Dados NBA.py",
    title="Análise jogadores NBA - PandasAI",
    icon=":material/sports_basketball:",
)

p7 = st.Page(
    "pages/Poluicao_ar.py",
    title="Poluição do Ar no Brasil",
    icon=":material/air:",
)

p8 = st.Page(
    "pages/Analise Descritiva de Dados.py",
    title="Análise Descritiva de Dados - FIFA 24",
    icon=":material/sports_and_outdoors:",
)

p9 = st.Page(
    "pages/Resumo_camarada.py",
    title="Assistente financeiro - LangChain",
    icon=":material/support_agent:",
)

p10 = st.Page(
    "pages/Incendios.py",
    title="Dados de Queimadas (Power BI)",
    icon=":material/local_fire_department:",
)

p11 = st.Page(
    "pages/Trafego Pago.py",
    title="Análise Dados Tráfego Pago (Looker)",
    icon=":material/smartphone:",
)

p12 = st.Page(
    "pages/VectorStats.py",
    title="Plugin QGIS - Vector Stats",
    icon=":material/extension:",
)

p16 = st.Page(
    "pages/lines.py",
    title="Identificação de Linhas - Ski Image",
    icon=":material/process_chart:",
)

p17 = st.Page(
    "pages/nba_database.py",
    title="Banco de Dados - NBA",
    icon=":material/database:",
)

p18 = st.Page(
    "pages/ml_arpu.py",
    title="Previsão de ofertas de cupons",
    icon=":material/local_activity:",
)

p19 = st.Page(
    "pages/ndvi_prediction_sentinel.py",
    title="Predição de NDVI - Sentinel 1 e 2 ",
    icon=":material/satellite:",
)

p20 = st.Page(
    "pages/billing_forecast.py",
    title="Potencial de Faturamento",
    icon=":material/location_city:",
)


pg = st.navigation(
    {
        "Sobre mim": [p1],
        "Geoprocessamento": [p2, p3, p7, p12],
        "Visão Computacional": [p4, p5, p16],
        "Machine Learning": [p18, p19, p20],
        "Análise de Dados": [p8, p10, p11],
        "Inteligência Artificial": [p9, p6],
        "Engenharia de Dados": [p17],
    },
    position="top",
)

pg.run()
