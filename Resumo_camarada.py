import streamlit as st
from PIL import Image

# Barra Lateral
barra_lateral = st.sidebar.empty()

st.title("Assistente financeiro com IA")

st.write("""   

O mercado de inteligência artificial está em alta, com novas versões de IAs transformando nossa interação com a tecnologia. Interessado pelo GPT-4, investiguei o potencial das IAs e encontrei o framework LangChain, que integra vários modelos LLMs. Com isso, desenvolvi o "Resumo Camarada" para analisar notícias do mercado financeiro. Usando Web Scraping e dados do yfinance, o modelo resume as principais informações do dia, ajudando a tomar decisões de investimento mais precisas.
         """)

st.write("Abaixo temos alguns resultados do assisente:")

col1, col2, col3 = st.columns(3)
image1 = Image.open(r"Dados/noticias.png")
col1.image(image1)

image2 = Image.open(r"Dados/ações.png")
col2.image(image2)


st.write("Link da aplicação: https://resumocamaradafinanceiro.streamlit.app/")
