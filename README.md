# Portfolio de Data Science (Streamlit)

Este repositório é o meu portfólio de Data Science desenvolvido com Streamlit, reunindo projetos práticos de geoprocessamento, visão computacional, machine learning, análise de dados, IA e engenharia de dados.

## Visão geral

O app organiza diferentes estudos e projetos em uma interface única, com navegação por categorias. Cada página apresenta um caso aplicado, com foco em resolução de problema, análise exploratória, modelagem e visualização.

## Stack principal

- Python
- Streamlit
- Pandas e NumPy
- Scikit-learn
- Plotly e Matplotlib
- Folium e Rasterio
- OpenCV e scikit-image
- Earth Engine API

## Como executar localmente

1. Clone o repositório:

```bash
git clone <url-do-repositorio>
```

2. Acesse a pasta do projeto:

```bash
cd pd
```

3. Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

No Windows (PowerShell):

```bash
.venv\Scripts\Activate.ps1
```

4. Instale as dependências:

```bash
pip install -r requirements.txt
```

5. Rode a aplicação:

```bash
streamlit run st_pages.py
```

## Estrutura do repositório

- `st_pages.py`: ponto de entrada e configuração da navegação do app.
- `pages/`: páginas dos projetos e aplicações.
- `dados/`: imagens e arquivos de apoio usados nas páginas.
- `requirements.txt`: dependências Python do projeto.

## Destaques das páginas

- **Sobre mim**: apresentação do perfil profissional.
- **Geoprocessamento**: mapas, download de imagens no GEE e plugin QGIS (Vector Stats).
- **Visão computacional**: classificação de feijões e identificação de círculos com OpenCV.
- **Machine learning**: previsão de cupons, predição de NDVI e potencial de faturamento.
- **Análise de dados**: tráfego pago e previsão de El Niño.
- **Inteligência artificial**: assistente financeiro com LangChain.
- **Engenharia de dados**: projeto de banco de dados NBA.

## Contato

- LinkedIn: `<seu-linkedin-aqui>`
- E-mail: `<seu-email-aqui>`
