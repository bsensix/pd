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
    col1.link_button("🛰️ Geoprocessamento", "https://brenonunes.streamlit.app/Mapas")
    col1.link_button(
        "👁️ Visão computacional",
        "https://brenonunes.streamlit.app/Classificador_feijoes",
    )
    col1.link_button(
        "🎲 Análise de dados", "https://brenonunes.streamlit.app/Dados_NBA"
    )
    col1.link_button(
        "🤖 Inteligência Artificial", "https://brenonunes.streamlit.app/Resumo_camarada"
    )

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
