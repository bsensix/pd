import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Sobre Mim",
    page_icon="🧑‍💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS para fundo escuro na página inteira
st.markdown(
    """
    <style>
        /* Fundo geral */
        .stApp {
            background: linear-gradient(
                135deg,
                #020B1B 0%,
                #071A2F 45%,
                #0B3A5A 100%
            );
            color: white;
        }

        /* Header transparente */
        [data-testid="stHeader"] {
            background: rgba(0,0,0,0);
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(
                180deg,
                #020B1B 0%,
                #0B3A5A 100%
            );
            border-right: 1px solid rgba(255,255,255,0.08);
        }

        [data-testid="stSidebarContent"] {
            background: transparent;
        }

        /* Textos */
        h1, h2, h3, h4, h5, h6, p, span, label {
            color: #F5F7FA !important;
        }

        /* Cards / containers */
        div[data-testid="stVerticalBlock"] > div:has(div.stContainer) {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 18px;
            padding: 1rem;
            backdrop-filter: blur(8px);
        }

        /* Botões */
        .stButton > button {
            background: linear-gradient(
                135deg,
                #0B3A5A 0%,
                #1E5EFF 100%
            );
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            transition: 0.3s ease;
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(30, 94, 255, 0.35);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(
        """
        <div style="padding: 40px 36px;">
            <h1 style="font-size:3.5rem;font-weight:800;color:#ffffff;margin-bottom:0.2rem;">Breno Nunes</h1>
            <p style="font-size:1.4rem;color:#ffffff;font-weight:600;margin-bottom:0.2rem;">
               Cientista e Engenheiro de Dados
            </p>
            <p style="font-size:1.1rem;color:#b0c8d4;margin-bottom:1.5rem;">
                Engenheiro Ambiental formado pela UFU atuo como Cientista de Dados na Sensix.
            </p>
            <p style="font-size:1.1rem;color:#d0e4ed;margin-bottom:1.5rem;line-height:1.7;">
                Tenho experiência sólida em projetos de análise de dados, machine learning, geoprocessamento e inteligência artificial, com foco em soluções para setores como agricultura de precisão, meio ambiente e business analytics. 
            </p>
            <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:1rem;">
                <span style="background-color:#1c5570;color:#ffffff;padding:8px 20px;border-radius:20px;font-size:1rem;font-weight:600;">🐍 Python</span>
                <span style="background-color:#1c5570;color:#ffffff;padding:8px 20px;border-radius:20px;font-size:1rem;font-weight:600;">🤖 Sklearn</span>
                <span style="background-color:#1c5570;color:#ffffff;padding:8px 20px;border-radius:20px;font-size:1rem;font-weight:600;">🛰️ Sensoriamento remoto</span>
                <span style="background-color:#1c5570;color:#ffffff;padding:8px 20px;border-radius:20px;font-size:1rem;font-weight:600;">☁️ AWS e GCP</span>
                <span style="background-color:#1c5570;color:#ffffff;padding:8px 20px;border-radius:20px;font-size:1rem;font-weight:600;">🧠 Airflow</span>
                <span style="background-color:#1c5570;color:#ffffff;padding:8px 20px;border-radius:20px;font-size:1rem;font-weight:600;">📊 Power BI e Data Studio</span>
                <span style="background-color:#1c5570;color:#ffffff;padding:8px 20px;border-radius:20px;font-size:1rem;font-weight:600;">🛢 PostgreSQL e SQL server</span>
                <span style="background-color:#1c5570;color:#ffffff;padding:8px 20px;border-radius:20px;font-size:1rem;font-weight:600;">🛠️ BIG Query e Databricks</span>
                <span style="background-color:#1c5570;color:#ffffff;padding:8px 20px;border-radius:20px;font-size:1rem;font-weight:600;">🌍 QGIS</span>
                <span style="background-color:#1c5570;color:#ffffff;padding:8px 20px;border-radius:20px;font-size:1rem;font-weight:600;">🚀 Docker</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    image = Image.open(r"dados/imagem_perfil.png")
    st.image(image, width=335)
