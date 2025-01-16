import os

import pandas as pd
import streamlit as st
from pandasai import SmartDataframe as SmartDataFrame
from sqlalchemy import create_engine

pandas_ai_key = st.secrets["general"]["PANDAS_AI_KEY"]
os.environ["PANDASAI_API_KEY"] = pandas_ai_key

usuario = st.secrets["database"]["USUARIO"]
senha = st.secrets["database"]["SENHA"]
host = st.secrets["database"]["HOST"]
port = st.secrets["database"]["PORT"]
database = st.secrets["database"]["DATABASE"]

# Conectar ao banco de dados
engine = create_engine(
    f"postgresql+psycopg2://{usuario}:{senha}@{host}:{port}/{database}"
)


# Função para buscar dados do banco de dados
def fetch_data(schema_name, table_name, engine):
    sql_query = f"""SELECT * FROM "{schema_name}"."{table_name}" """
    return pd.read_sql_query(sql_query, engine)


# Carregar dados
df_games_results = fetch_data("NBA", "GAMES_RESULTS", engine)
df_players = fetch_data("NBA", "PLAYERS", engine)
df_players_results = fetch_data("NBA", "PLAYER_RESULTS", engine)

# Combine df_players com df_players_results para incluir os nomes dos jogadores
df_players_results = df_players_results.merge(
    df_players, left_on="Player_ID", right_on="id", how="left"
)

# Combine df_players_results com df_games_results para incluir o time do jogador
df_players_results = df_players_results.merge(
    df_games_results[["Game_ID", "TEAM_1", "TEAM_2"]], on="Game_ID", how="left"
)


# Descrever o DataFrame para o agente
description = """
Este DataFrame contém informações sobre os resultados dos jogadores da NBA. 
As colunas são:
- SEASON_ID: Identificador da temporada.
- Player_ID: Identificador do jogador.
- Game_ID: Identificador do jogo.
- GAME_DATE: Data do jogo.
- MATCHUP: Confronto entre as equipes.
- WL: Resultado do jogo (Vitória/Derrota).
- MIN: Minutos jogados.
- FGM: Arremessos de campo convertidos.
- FGA: Arremessos de campo tentados.
- FG_PCT: Percentual de arremessos de campo convertidos.
- FG3M: Arremessos de três pontos convertidos.
- FG3A: Arremessos de três pontos tentados.
- FG3_PCT: Percentual de arremessos de três pontos convertidos.
- FTM: Lances livres convertidos.
- FTA: Lances livres tentados.
- FT_PCT: Percentual de lances livres convertidos.
- OREB: Rebotes ofensivos.
- DREB: Rebotes defensivos.
- REB: Total de rebotes.
- AST: Assistências.
- STL: Roubos de bola.
- BLK: Bloqueios.
- TOV: Turnovers.
- PF: Faltas pessoais.
- PTS: Pontos.
- PLUS_MINUS: Plus/Minus.
- VIDEO_AVAILABLE: Indica se o vídeo está disponível.
- full_name: Nome completo do jogador.

Os dados são provenientes da temporada regular 24/25 da NBA.

Este agente é configurado para analisar os dados dos jogadores da NBA, focando nas estatísticas de pontos (PTS), rebotes (REB) e assistências (AST). Ele pode responder a perguntas sobre o desempenho dos jogadores em termos dessas métricas, identificar tendências e padrões, e fornecer insights detalhados com base nos dados disponíveis
"""

# Configurar o SmartDataFrame com a descrição do DataFrame
sdf = SmartDataFrame(df_players_results, description=description)


# Função para analisar os dados usando SmartDataFrame
def analisar_dados(consulta):
    resultado = sdf.chat(consulta)
    return resultado


# Título da aplicação
st.title("Análise de Dados da NBA🏀🐼")

# Explicação sobre a aplicação
st.write("""
Esta aplicação usa o framework **PandasAI** para analisar dados dos **jogadores da NBA** da temporada regular 24/25.
""")

with st.expander("Dataframe preview 🔍"):
    st.write(df_players_results.head())

# Inicializar o estado da sessão para armazenar consultas e respostas
if "historico" not in st.session_state:
    st.session_state.historico = []

# Entrada de chat para a consulta do usuário
consulta = st.chat_input("Digite sua consulta sobre as estatísticas dos jogadores:")

if consulta:
    resultado_analise = analisar_dados(consulta)
    st.session_state.historico.append((consulta, resultado_analise))

# Exibir o histórico de consultas e respostas
for consulta, resposta in st.session_state.historico:
    st.write(f"**Consulta:** {consulta}")
    st.write(f"**Resposta:** {resposta}")
