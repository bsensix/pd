import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

st.title("Análise Descritiva de Dados 📊")
st.markdown(
    "A análise descritiva de dados é uma etapa inicial de exploração, resumo e compreensão de um conjunto de dados. Envolve o cálculo de estatísticas resumidas e a criação de gráficos para identificar tendências, padrões e valores atípicos."
)
st.markdown(
    "Nesse tipo de estudo a análise dos dados se concentra na distribuição, tendência central e dispersão dos dados, além de explorar correlações entre variáveis. Essa abordagem fornece insights iniciais, estabelecendo uma base para análises estatísticas mais avançadas."
)
st.markdown(
    "Para ilustar a análise descritiva, vamos usar as informações dos jogadores jogo **EA Sports FC** ⚽"
)

# Ler o DataFrame de exemplo
df = pd.read_csv(
    r"dados/all_players.csv",
    index_col=0,
)

# imagem EA Sports
# Estilo CSS para posicionar a imagem
image_style = (
    "position: absolute; "
    "top: 00; "
    "right: 0; "
    "width: 100px; "
    "height: 50px; "
    "margin-top: -340px; "
    "margin-right: -160px;"
)

# Criar o código HTML para a imagem
image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/EA_Sports_FC_24_logo.svg/2560px-EA_Sports_FC_24_logo.svg.png"
image_html = f'<img src="{image_url}" style="{image_style}">'

# Usar st.markdown para exibir a imagem
st.markdown(image_html, unsafe_allow_html=True)

# Filtros
st.title("Filtros:")
col1, col2, col3 = st.columns(3)

list_countries = df["Nation"].unique()
filter_country = col1.multiselect("Selecione o País:", list_countries)

list_positions = df["Position"].unique()
filter_position = col2.multiselect("Selecione a posição do Jogador:", list_positions)

list_clubs = df["Club"].unique()
filter_club = col3.multiselect("Selecione o Clube:", list_clubs)

# Aplicar os filtros ao DataFrame
if not filter_country and not filter_position and not filter_club:
    filtered_df = df  # Se nenhum filtro estiver selecionado, mostrar todos os dados
else:
    filtered_df = df[
        (df["Nation"].isin(filter_country))
        | (df["Position"].isin(filter_position))
        | (df["Club"].isin(filter_club))
    ]

# Dados estatísticos clássicos
df_info = filtered_df.describe()

st.subheader("Estatística Básica")
st.markdown(
    "Calcular medidas estatísticas básicas, como média, desvio padrão, mínimo, máximo e quartis (25º, 50º e 75º percentis), é essencial em análises de dados. Elas resumem a distribuição, destacam a tendência central, indicam a dispersão, revelam valores extremos e auxiliam na tomada de decisões"
)
st.markdown(
    "Podemos ter esses dados de forma rápida usando a função describe() do Pandas"
)
st.dataframe(df_info)

# Distribuição e Frequência dos Dados

st.subheader("Histograma")
st.markdown(
    "Um histograma é um tipo de gráfico usado na análise estatística para representar a distribuição de um conjunto de dados numéricos. Ele é particularmente útil para entender como os valores estão agrupados em intervalos, mostrando a frequência com que os valores caem em cada intervalo."
)
st.markdown(
    "No seguinte estudo de caso podemos annalisar qual a idade de jogadores e mais frequente, quais notas do jogadores são mais comuns, entre outras análises sobre os parâmetros"
)

# Lista de nomes das colunas a serem excluídas
colunas_para_excluir = [
    "Name",
    "Nation",
    "Club",
    "Position",
    "Att work rate",
    "Def work rate",
    "Preferred foot",
    "Weak foot",
    "Skill moves",
    "URL",
    "Gender",
    "GK",
]

# Use a função drop com a lista de colunas para excluir
df_hist = df.drop(colunas_para_excluir, axis=1)

# Adicione um seletor para escolher a coluna
coluna_selecionada = st.selectbox("Selecione o parâmetro:", df_hist.columns)

# Crie o histograma com base na coluna selecionada
plt.figure(figsize=(8, 6))
plt.hist(df[coluna_selecionada], bins=20, edgecolor="k")
plt.title(f"Histograma de {coluna_selecionada}")
plt.xlabel(coluna_selecionada)
plt.ylabel("Frequência")
st.pyplot(plt)

# Correlação de Dados

st.subheader("Correlação de Dados")
st.markdown(
    "A correlação de dados é uma ferramenta valiosa para avaliar como duas variáveis estão relacionadas. Ela pode ajudar na identificação de padrões, na tomada de decisões e na formulação de hipóteses em várias disciplinas, fornecendo insights importantes sobre a interação entre variáveis e auxiliando na compreensão de fenômenos complexos."
)

# Select the relevant columns for correlation analysis
attributes = df[
    ["Pace", "Shooting", "Passing", "Dribbling", "Defending", "Acceleration", "Sprint"]
]

# Calculate the correlation matrix
correlation_matrix = attributes.corr()

# Plot a heatmap to visualize the correlation matrix
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", fmt=".2f", square=True)
plt.title("Correlação entre os Atributos dos Jogadores")
plt.show()
st.pyplot(plt)

st.subheader("Gráfico de Box Plot")
st.markdown(
    'O box plot é um gráfico que fornece uma visão resumida da distribuição estatística de um conjunto de dados. Ele destaca a mediana, quartis e a presença de outliers. A caixa central representa o intervalo interquartil (IQR), enquanto os "whiskers" se estendem até os limites dentro de 1,5 vezes o IQR. Outliers, pontos fora desse intervalo, podem indicar observações incomuns. É uma ferramenta eficaz para visualizar a variabilidade e a tendência central dos dados de forma concisa.'
)
# Adicione um seletor para escolher a coluna para o Box Plot
coluna_box_plot = st.selectbox("Selecione a coluna para o Box Plot:", df_hist.columns)

# Crie o Box Plot com base na coluna selecionada
plt.figure(figsize=(10, 6))
sns.boxplot(x=coluna_box_plot, data=df)
plt.title(f"Box Plot de {coluna_box_plot}")
plt.xlabel(coluna_box_plot)
st.pyplot(plt)
