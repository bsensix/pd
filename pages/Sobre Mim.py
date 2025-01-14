import streamlit as st
from PIL import Image

# Configurações da página
st.set_page_config(
    page_title="Sobre Mim",
    page_icon="🧑‍💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Layout das colunas
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## Bem-vindo ao meu **portfólio**!")
    st.markdown(
        """
        Sou formado em Engenharia Ambiental pela (UFU) e atualmente trabalho como **Cientista de Dados**, especializado em análises de dados aplicados à **Agricultura e Meio Ambiente**. 
        Além disso, sou um entusiasta de esportes e aplico algumas análises em esportes como Futebol e Basquete. Na aba à esquerda, você encontrará alguns desses projetos e abaixo as áreas nas quais tenho experiência.
        """
    )

    st.markdown(
        """
        <style>
        .custom-button {
            width: 100%;
            padding: 10px;
            font-size: 14px;
            border-radius: 25px;
            box-shadow: 3px 5px 10px 0px rgba(128, 128, 128, 0.245);
            border: none;
            cursor: pointer;
        }
        .custom-button:hover {
            background-color: #F0F2F6;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Criando colunas para os botões
    btn_col1, btn_col2, btn_col3, btn_col4, btn_col5 = st.columns(5)

    with btn_col1:
        st.markdown(
            """
            <a href="https://brenonunes.streamlit.app/Mapas" target="_blank">
                <button class="custom-button">
                    🛰️ Geoprocessamento
                </button>
            </a>
            """,
            unsafe_allow_html=True,
        )
    with btn_col2:
        st.markdown(
            """
            <a href="https://brenonunes.streamlit.app/Classificador_feijoes" target="_blank">
                <button class="custom-button">
                    👁️ Visão computacional
                </button>
            </a>
            """,
            unsafe_allow_html=True,
        )
    with btn_col3:
        st.markdown(
            """
            <a href="https://brenonunes.streamlit.app/Dados_NBA" target="_blank">
                <button class="custom-button">
                    📊 Análise de dados
                </button>
            </a>
            """,
            unsafe_allow_html=True,
        )
    with btn_col4:
        st.markdown(
            """
            <a href="https://brenonunes.streamlit.app/Resumo_camarada" target="_blank">
                <button class="custom-button">
                    🤖 Inteligência Artificial
                </button>
            </a>
            """,
            unsafe_allow_html=True,
        )
    with btn_col5:
        st.markdown(
            """
            <a href="https://brenonunes.streamlit.app/nba_database" target="_blank">
                <button class="custom-button">
                    ⚙️ Engenharia de dados
                </button>
            </a>
            """,
            unsafe_allow_html=True,
        )

    col1.markdown("")
    col1.markdown("**Contatos**")
    col1.markdown("- [Github](https://github.com/bsensix)")
    col1.markdown("- [Linkedin](https://www.linkedin.com/in/breno-nunes-b595781ba/)")
    col1.markdown("- [E-mail](mailto:breno_1697@hotmail.com)")


with col2:
    image = Image.open(r"Dados/Perfil.png")
    st.image(image, use_column_width=True)

# Rodapé
st.markdown("---")
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: black;
        text-align: center;
        padding: 10px;
    }
    </style>
    <div class="footer">
        <p>Atenciosamente, Breno Nunes</p>
    </div>
    """,
    unsafe_allow_html=True,
)
