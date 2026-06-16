import streamlit as st

st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg, #020B1B 0%, #071A2F 45%, #0B3A5A 100%);
        }

        [data-testid="stHeader"] {
            background: #020B1B !important;
            border-bottom: 1px solid rgba(255,255,255,0.08);
        }

        [data-testid="stNavigation"] {
            background: #020B1B !important;
        }

        [data-testid="stNavigation"] button,
        [data-testid="stNavigation"] a {
            color: #b0c8d4 !important;
        }

        [data-testid="stNavigation"] button:hover,
        [data-testid="stNavigation"] a:hover {
            color: #ffffff !important;
            background: rgba(255,255,255,0.05) !important;
        }

        /* Dropdown - todas as variações possíveis */
        ul[data-testid="stNavMenuList"],
        [data-testid="stNavMenuList"],
        div[data-testid="stPopover"] > div,
        div[role="menu"],
        div[role="listbox"],
        div[role="dialog"],
        [data-radix-popper-content-wrapper] > div,
        [data-radix-popper-content-wrapper],
        [data-testid="stPageLink"],
        section[data-testid="stSidebarContent"],
        div.st-emotion-cache-1gwvy71,
        div[class*="st-emotion-cache"] ul,
        div[class*="st-emotion-cache"] nav {
            background-color: #071A2F !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            border-radius: 12px !important;
        }

        /* Força fundo escuro em QUALQUER elemento dentro do dropdown */
        [data-radix-popper-content-wrapper] *,
        [data-testid="stNavMenuList"] *,
        div[role="menu"] *,
        div[role="listbox"] * {
            background-color: #071A2F !important;
            color: #b0c8d4 !important;
        }

        /* Links das páginas no dropdown */
        [data-testid="stPageLink"] a,
        [data-testid="stPageLink"] span,
        [data-testid="stNavigation"] [role="menuitem"],
        [data-testid="stNavigation"] [role="option"] {
            color: #b0c8d4 !important;
            background-color: #071A2F !important;
        }

        /* Hover nos itens */
        [data-radix-popper-content-wrapper] a:hover,
        div[role="menu"] a:hover,
        div[role="listbox"] li:hover,
        [data-testid="stNavigation"] [role="menuitem"]:hover {
            background-color: rgba(255,255,255,0.07) !important;
            color: #ffffff !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #020B1B 0%, #0B3A5A 100%);
            border-right: 1px solid rgba(255,255,255,0.08);
        }
    </style>
    """,
    unsafe_allow_html=True,
)


p1 = st.Page("pages/sobre_mim.py", title="Breno Nunes", icon=":material/home:")
p2 = st.Page("pages/mapas.py", title="Mapas", icon=":material/map:")
p3 = st.Page(
    "pages/pagina_gee_download_de_imagens.py",
    title="Download de Imagens no GEE",
    icon=":material/travel_explore:",
)
p4 = st.Page(
    "pages/classificador_feijoes.py",
    title="Feijões Estragados - Tensor Flow",
    icon=":material/workspaces:",
)
p5 = st.Page(
    "pages/identificacao_de_pivos_interface.py",
    title="Identificação de Círculos - Open CV",
    icon=":material/radio_button_unchecked:",
)

p9 = st.Page(
    "pages/resumo_camarada.py",
    title="Assistente financeiro - LangChain",
    icon=":material/support_agent:",
)


p11 = st.Page(
    "pages/trafego_pago.py",
    title="Análise Dados Tráfego Pago (Looker)",
    icon=":material/smartphone:",
)

p12 = st.Page(
    "pages/vector_stats.py",
    title="Plugin QGIS - Vector Stats",
    icon=":material/extension:",
)


p17 = st.Page(
    "pages/nba_database.py",
    title="Banco de Dados - NBA",
    icon=":material/database:",
)

p22 = st.Page(
    "pages/agro_gee_api.py",
    title="Agro GEE API",
    icon=":material/agriculture:",
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

p21 = st.Page(
    "pages/el_nino.py",
    title="Previsão de El Niño",
    icon=":material/waves:",
)

pg = st.navigation(
    {
        "🏠 Sobre mim": [p1],
        "🗺️ Geoprocessamento": [p2, p3, p12],
        "🖼️ Visão Computacional": [p4, p5],
        "🚀 Machine Learning": [p18, p19, p20],
        "📊 Análise de Dados": [p11, p21],
        "🧠 Inteligência Artificial": [p9],
        "🛠️ Engenharia de Dados": [p17, p22],
    },
    position="top",
)

pg.run()
