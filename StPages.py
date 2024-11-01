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
    title="Previsão de Total Pontos - NBA",
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

p13 = st.Page(
    "pages/tools.py",
    title="Tecnologias",
    icon=":material/construction:",
)

p14 = st.Page(
    "pages/artigos.py",
    title="Artigos e Cursos",
    icon=":material/article:",
)

p15 = st.Page(
    "pages/certificados.py",
    title="Certificados",
    icon=":material/task:",
)


pg = st.navigation(
    {
        "Sobre mim": [p1, p13, p14, p15],
        "Geoprocessamento": [p2, p3, p7, p12],
        "Visão Computacional": [p4, p5],
        "Análise de Dados": [p6, p8],
        "Inteligência Artificial": [p9],
        "Visualização de Dados": [p10, p11],
    }
)

pg.run()
