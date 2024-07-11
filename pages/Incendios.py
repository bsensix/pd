import streamlit as st

st.title("Análise de Focos de Queimadas no Brasil 🔥")
st.markdown(
    "Ao analisar dados históricos de focos de incêndios por estado e região no Brasil, é possível identificar tendências, padrões sazonais e variações geográficas na incidência desses incêndios. Essa análise pode revelar quais regiões são mais vulneráveis e quais fatores, como desmatamento, clima ou atividades humanas, contribuem para o aumento dos incêndios em determinadas áreas. Com essas informações, medidas preventivas e estratégias de gestão de risco podem ser desenvolvidas para reduzir a frequência e impacto desses eventos em cada estado. Abaixo temos um relatório simplificado de análise desses dados no Power BI."
)
st.markdown(
    """
    <iframe title="Incendios_Brasil" width="600" height="373.5" src="https://app.powerbi.com/view?r=eyJrIjoiNjFjZGVjMDEtYThjOC00M2I2LTk5ZmUtYzg4ZTg3YjExMDQ3IiwidCI6ImNkNWU2ZDIzLWNiOTktNDE4OS04OGFiLTFhOTAyMWEwYzQ1MSJ9" frameborder="0" allowFullScreen="true"></iframe>
    """,
    unsafe_allow_html=True,
)
