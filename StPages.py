import streamlit as st
from st_pages import Page, add_page_title, show_pages

page_bg_img = """
    <style>
    [data-testid="stAppViewContainer"] > .main {
    background-image: url("https://img.freepik.com/fotos-premium/papel-de-parede-criativo-de-graficos-de-big-data_670147-9071.jpg");
    background-size: cover;
    }

    [data-testid="stHeader"] {
    background: rgba(0,0,0,0);
    }

    </style>
    """
st.markdown(page_bg_img, unsafe_allow_html=True)

code = "Seja bem-vindo ao meu portfólio!\nUm espaço onde você pode explorar alguns dos projetos nos quais estive envolvido.\nSinta-se à vontade para entrar em contato caso tenha dúvidas.\nNa aba à esquerda, você encontrará alguns desses projetos e um pouco da\nminha experiência \n\nAss: Breno Nunes"

st.code(code, language="python")

show_pages(
    [
        Page("Sobre Mim.py", "Sobre Mim", "🏠"),
        Page("Mapas.py", "Mapas", "🗺️"),
        Page(
            "Página - GEE - Download de Imagens.py", "Download de Imagens no GEE", "🌎"
        ),
        Page(
            "Identificação de Pivôs - Interface.py", "Identificação de Círculos", "🔘"
        ),
        Page("Analise Descritiva de Dados.py", "Análise Descritiva de Dados", "📊"),
        Page("Dados NBA.py", "Previsão de Total Pontos NBA", "🏀"),
        Page("Trafego Pago.py", "Análise Dados Tráfego Pago", "ⓕ"),
    ]
)

add_page_title()  # Optional method to add title and icon to current page
