import streamlit as st

st.markdown("# Previsão de Faturamento (Billing Forecast)")

st.markdown("""
Este projeto tem como objetivo estimar o potencial de faturamento em bairros de São Paulo para uma empresa alimentícia situada no Rio de Janeiro, que deseja expandir suas operações. A análise utiliza dados sociodemográficos e de faturamento dos bairros do Rio de Janeiro como base para prever o faturamento em São Paulo.""")

st.markdown("[Projeto no GitHub](https://github.com/bsensix/billing_forecast)")

st.markdown("## Metodologia")

st.markdown("""
**Análise exploratória e preparação dos dados:**
- Filtrar os dados para o público-alvo: adultos de 25 a 50 anos das classes A (rendas A1 e A2) e B (rendas B1 e B2).
- Tratar valores nulos e ajustar colunas relevantes.

**Treinamento de modelos preditivos:**
- Modelos utilizados:
    - Regressão Linear
    - Random Forest
    - Gradient Boosting
- Avaliação dos modelos com métricas como MSE (Erro Quadrático Médio) e R² (Coeficiente de Determinação).

**Validação e comparação dos modelos:**
- Comparar os resultados dos modelos para selecionar o mais adequado.
""")
