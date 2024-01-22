import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from nba_api.stats.endpoints import teamgamelog
from nba_api.stats.static import players, teams
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

st.set_page_config(
    page_title="NBA Analytics", layout="wide", initial_sidebar_state="expanded"
)


# Função para obter o ID do time
def get_team_id(team_name):
    nba_teams = teams.get_teams()
    for team in nba_teams:
        if team["full_name"] == team_name:
            return team["id"]
    return None


# Função para obter os últimos jogos de um time
def get_team_last_games(team_id):
    game_log = teamgamelog.TeamGameLog(
        team_id=team_id, season="2023-24", season_type_all_star="Regular Season"
    ).get_data_frames()[0]
    return game_log


# Carregar seus dados
df = pd.read_csv(r"Dados/jogos_ate_01_01_2027.csv")
nome_times = teams.get_teams()
nome_times = pd.DataFrame(nome_times)

df["Time"] = df["Team_ID"].map(dict(zip(nome_times["id"], nome_times["full_name"])))

# Selecionar as features e o alvo
features = [
    "FGM",
    "FGA",
    "FG3M",
    "FG3A",
    "FTM",
    "FTA",
    "OREB",
    "DREB",
    "AST",
    "STL",
    "BLK",
    "TOV",
    "PF",
]
target = "PTS"

# Dividir o conjunto de dados em treino e teste
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)

# Criar um pipeline para pré-processamento e treinamento do modelo
numeric_features = features
numeric_transformer = Pipeline(
    steps=[("imputer", SimpleImputer(strategy="mean")), ("scaler", StandardScaler())]
)

preprocessor = ColumnTransformer(
    transformers=[("num", numeric_transformer, numeric_features)]
)

model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(random_state=42)),
    ]
)

# Treinar o modelo
model.fit(train_df[features], train_df[target])

# Página Streamlit
st.title("Estatísticas dos Jogos da NBA 📊")

# Estilo CSS para posicionar a imagem
image_style = (
    "position: absolute; "
    "top: 00; "
    "right: 0; "
    "width: 100px; "
    "height: 50px; "
    "margin-top: -120px; "
    "margin-right: -60px;"
)

# Criar o código HTML para a imagem
image_url = "https://logosmarcas.net/wp-content/uploads/2020/11/National-Basketball-Association-Logo.png"
image_html = f'<img src="{image_url}" style="{image_style}">'

# Usar st.markdown para exibir a imagem
st.markdown(image_html, unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Informações do Relatório 📄",
        "Estatísticas de Times 🏅",
        "Previsão Total de Pontos 🏀",
        "Estatísticas de Jogadores ⛹️",
    ]
)

with tab1:
    # Obter informações sobre times
    info_times = teams.get_teams()
    dict_times = dict(
        zip(
            [team["id"] for team in info_times],
            [team["full_name"] for team in info_times],
        )
    )

    st.markdown(
        "Este relatório de exibição dos jogos da NBA tem como propósito apresentar rankings de times e métricas de jogadores, atendendo tanto aos fãs de basquete quanto àqueles interessados em utilizar dados para apostas esportivas na principal liga de basquete mundo. Utilizamos informações dos jogos para treinar um modelo de previsão de pontos totais em uma partida, considerando as métricas de ataque das equipes envolvidas. Além disso, oferecemos análises de desempenho individual de cada jogador ao longo da temporada."
    )

    # Aba 1: Jogos de Hoje


with tab2:
    col1, col2 = st.columns(2)
    # Calcular a média de pontos para cada time
    df_ranking_ataque = df.groupby("Time")["PTS"].mean().reset_index()

    # Ordenar o DataFrame de ranking pela média de pontos em ordem decrescente
    df_ranking_ataque = df_ranking_ataque.sort_values(
        by="PTS", ascending=False
    ).reset_index(drop=True)
    df_ranking_ataque.index = df_ranking_ataque.index + 1

    # Renomear as colunas se necessário
    df_ranking_ataque.columns = ["Time", "PTS Feitos"]

    col1.subheader("Líderes Ofensivos")
    col1.dataframe(df_ranking_ataque)

    # Calcular o total de pontos por Game_ID
    df_total_pontos_game = df.groupby("Game_ID")["PTS"].transform("sum")

    # Adicionar a coluna 'Pontos Tomados'
    df["Pontos Tomados"] = df_total_pontos_game - df["PTS"]

    # Calcular a média de 'Pontos Tomados' por 'Time'
    df_ranking_defesa = df.groupby("Time")["Pontos Tomados"].mean().reset_index()

    # Ordenar o DataFrame de ranking pela média de 'Pontos Tomados' em ordem decrescente
    df_ranking_defesa = df_ranking_defesa.sort_values(
        by="Pontos Tomados", ascending=True
    ).reset_index(drop=True)
    df_ranking_defesa.index = df_ranking_defesa.index + 1

    # Renomear as colunas se necessário
    df_ranking_defesa.columns = ["Time", "PTS Tomados"]

    col2.subheader("Líderes Defensivos")
    col2.dataframe(df_ranking_defesa)

    # Calcular a média de pontos para cada time
    df_ranking_rebotes = df.groupby("Time")["REB"].mean().reset_index()

    # Ordenar o DataFrame de ranking pela média de pontos em ordem decrescente
    df_ranking_rebotes = df_ranking_rebotes.sort_values(
        by="REB", ascending=False
    ).reset_index(drop=True)
    df_ranking_rebotes.index = df_ranking_rebotes.index + 1

    # Renomear as colunas se necessário
    df_ranking_rebotes.columns = ["Time", "Rebotes"]

    col1.subheader("Líderes de Rebotes")
    col1.dataframe(df_ranking_rebotes)

    # Calcular a média de pontos para cada time
    df_ranking_tocos = df.groupby("Time")["BLK"].mean().reset_index()

    # Ordenar o DataFrame de ranking pela média de pontos em ordem decrescente
    df_ranking_tocos = df_ranking_tocos.sort_values(
        by="BLK", ascending=False
    ).reset_index(drop=True)
    df_ranking_tocos.index = df_ranking_tocos.index + 1

    # Renomear as colunas se necessário
    df_ranking_tocos.columns = ["Time", "Tocos"]

    col2.subheader("Líderes de Tocos")
    col2.dataframe(df_ranking_tocos)

    # Calcular a média de pontos para cada time
    df_ranking_ast = df.groupby("Time")["AST"].mean().reset_index()

    # Ordenar o DataFrame de ranking pela média de pontos em ordem decrescente
    df_ranking_ast = df_ranking_ast.sort_values(by="AST", ascending=False).reset_index(
        drop=True
    )
    df_ranking_ast.index = df_ranking_ast.index + 1

    # Renomear as colunas se necessário
    df_ranking_ast.columns = ["Time", "Assistências"]

    col1.subheader("Líderes de Assistências")
    col1.dataframe(df_ranking_ast)

    # Calcular a média de pontos para cada time
    df_ranking_roubo = df.groupby("Time")["STL"].mean().reset_index()

    # Ordenar o DataFrame de ranking pela média de pontos em ordem decrescente
    df_ranking_roubo = df_ranking_roubo.sort_values(
        by="STL", ascending=False
    ).reset_index(drop=True)
    df_ranking_roubo.index = df_ranking_roubo.index + 1

    # Renomear as colunas se necessário
    df_ranking_roubo.columns = ["Time", "Roubos"]

    col2.subheader("Líderes de Roubos de Bola")
    col2.dataframe(df_ranking_roubo)

    # Calcular a média de pontos para cada time
    df_ranking_to = df.groupby("Time")["TOV"].mean().reset_index()

    # Ordenar o DataFrame de ranking pela média de pontos em ordem decrescente
    df_ranking_to = df_ranking_to.sort_values(by="TOV", ascending=False).reset_index(
        drop=True
    )
    df_ranking_to.index = df_ranking_to.index + 1

    # Renomear as colunas se necessário
    df_ranking_to.columns = ["Time", "Turnovers"]

    col1.subheader("Líderes de Turnovers")
    col1.dataframe(df_ranking_to)

    # Calcular a média de pontos para cada time
    df_ranking_faltas = df.groupby("Time")["PF"].mean().reset_index()

    # Ordenar o DataFrame de ranking pela média de pontos em ordem decrescente
    df_ranking_faltas = df_ranking_faltas.sort_values(
        by="PF", ascending=False
    ).reset_index(drop=True)
    df_ranking_faltas.index = df_ranking_faltas.index + 1

    # Renomear as colunas se necessário
    df_ranking_faltas.columns = ["Time", "Faltas"]

    col2.subheader("Líderes de Faltas")
    col2.dataframe(df_ranking_faltas)

with tab3:
    col1, col2 = st.columns(2)
    selected_team_1 = col1.selectbox(
        "Selecione o time da Casa:",
        teams.get_teams(),
        format_func=lambda x: x["full_name"],
    )
    selected_team_2 = col2.selectbox(
        "Selecione o time de Fora:",
        teams.get_teams(),
        format_func=lambda x: x["full_name"],
    )

    # Obter os IDs dos times selecionados
    team_id_1 = get_team_id(selected_team_1["full_name"])
    team_id_2 = get_team_id(selected_team_2["full_name"])

    # Obter os últimos jogos de todos os times para a temporada atual
    all_teams_games = pd.read_csv(r"Dados/jogos_ate_01_01_2027.csv")
    all_teams_games["Jogos"] = all_teams_games["WL"].replace(
        {"W": "Vitória", "L": "Derrota"}
    )

    # Filtrar os dados do DataFrame para os times selecionados
    df_1 = all_teams_games[all_teams_games["Team_ID"] == team_id_1]
    df_2 = all_teams_games[all_teams_games["Team_ID"] == team_id_2]

    # Calcular o total de pontos feitos e sofridos em um jogo (soma por GAME_ID)
    total_pontos = all_teams_games.groupby("Game_ID")["PTS"].sum().reset_index()

    # Adicionar a coluna 'total' aos DataFrames
    df_1 = pd.merge(
        df_1, total_pontos, on="Game_ID", how="left", suffixes=("", "_total")
    )
    df_2 = pd.merge(
        df_2, total_pontos, on="Game_ID", how="left", suffixes=("", "_total")
    )

    # Calcular a média de pontos
    media_pontos_1 = df_1["PTS"].mean()

    cor_map = {"Vitória": "green", "Derrota": "red"}

    # Adicionar a coluna "COLOR" ao DataFrame com base em "MATCHUP"
    df_1["COLOR"] = df_1["MATCHUP"].map(cor_map)

    # Converter a coluna 'GAME_DATE' para o tipo de data
    df_1["GAME_DATE"] = pd.to_datetime(df_2["GAME_DATE"])

    # Ordenar as datas
    ordered_dates = sorted(df_1["GAME_DATE"].unique())

    # Criar gráfico interativo para os dois times
    fig_1 = px.bar(
        df_1,
        x="GAME_DATE",
        y="PTS",
        labels={"PTS": "Pontos"},
        title=f'Pontuação nos Últimos Jogos - {selected_team_1["full_name"]}',
        hover_data=["PTS", "MATCHUP", "Jogos"],
        text="PTS",
        color="Jogos",
        color_discrete_map=cor_map,
        category_orders={"GAME_DATE": ordered_dates},
    )

    # Adicionar a linha da média de pontos ao gráfico do primeiro time
    fig_1.add_trace(
        go.Scatter(
            x=df_1["GAME_DATE"],
            y=[media_pontos_1] * len(df_1),  # Repetir a média para cada ponto no eixo x
            mode="lines",
            name="Média de Pontos",
            line=dict(color="Black", dash="dash"),
        )
    )

    col1.plotly_chart(fig_1)

    media_total_1 = round(df_1["PTS_total"].mean(), 0)
    col1.metric(
        f'Total Final Jogo - {selected_team_1["full_name"]}', value=media_total_1
    )

    index_selected_team_1 = df_ranking_ataque[
        df_ranking_ataque["Time"] == selected_team_1["full_name"]
    ].index[0]
    col1.metric(
        f'Ranking Ataque - {selected_team_1["full_name"]}', value=index_selected_team_1
    )

    index_selected_team_1 = df_ranking_defesa[
        df_ranking_defesa["Time"] == selected_team_1["full_name"]
    ].index[0]
    col1.metric(
        f'Ranking defesa - {selected_team_1["full_name"]}', value=index_selected_team_1
    )

    # Adicionar a linha da média de pontos ao gráfico do primeiro time
    # Criar gráfico interativo para o segundo time

    media_pontos_2 = df_2["PTS"].mean()

    # Adicionar a coluna "COLOR" ao DataFrame com base em "MATCHUP"
    df_2["COLOR"] = df_2["MATCHUP"].map(cor_map)

    # Converter a coluna 'GAME_DATE' para o tipo de data
    df_2["GAME_DATE"] = pd.to_datetime(df_2["GAME_DATE"])

    # Ordenar as datas
    ordered_dates = sorted(df_2["GAME_DATE"].unique())

    # Criar o gráfico de barras com cores adaptadas
    fig_2 = px.bar(
        df_2,
        x="GAME_DATE",
        y="PTS",
        labels={"PTS": "Pontos"},
        title=f'Pontuação nos Últimos Jogos - {selected_team_2["full_name"]}',
        hover_data=["PTS", "MATCHUP", "Jogos"],
        text="PTS",
        color="Jogos",
        color_discrete_map=cor_map,
        category_orders={"GAME_DATE": ordered_dates},
    )

    fig_2.add_trace(
        go.Scatter(
            x=df_2["GAME_DATE"],
            y=[media_pontos_2] * len(df_1),  # Repetir a média para cada ponto no eixo x
            mode="lines",
            name="Média de Pontos",
            line=dict(color="Black", dash="dash"),
        )
    )

    col2.plotly_chart(fig_2)

    media_total_2 = round(df_2["PTS_total"].mean(), 0)
    col2.metric(
        f'Total Final Jogo - {selected_team_2["full_name"]}', value=media_total_2
    )

    index_selected_team_2 = df_ranking_ataque[
        df_ranking_ataque["Time"] == selected_team_2["full_name"]
    ].index[0]
    col2.metric(
        f'Ranking Ataque - {selected_team_2["full_name"]}', value=index_selected_team_2
    )

    index_selected_team_2 = df_ranking_defesa[
        df_ranking_defesa["Time"] == selected_team_2["full_name"]
    ].index[0]
    col2.metric(
        f'Ranking Defesa - {selected_team_2["full_name"]}', value=index_selected_team_2
    )

    # Botão para fazer a previsão
    if st.button("Prever Total de Pontos"):
        # Filtrar dados para os times escolhidos
        selected_team_1_df = df[df["Team_ID"] == team_id_1]
        selected_team_2_df = df[df["Team_ID"] == team_id_2]

        # Fazer previsão para cada time
        prediction_team_1 = model.predict(selected_team_1_df[features]).mean()
        prediction_team_2 = model.predict(selected_team_2_df[features]).mean()

        # Exibir a previsão
        st.success(
            f'A previsão do total de pontos para o jogo entre {selected_team_1["full_name"]} e {selected_team_2["full_name"]} é: {prediction_team_1 + prediction_team_2:.2f}'
        )
with tab4:
    df_jogadores = pd.read_csv(r"Dados/todos_jogadores.csv")
    nome_jogadores = players.get_players()
    nome_jogadores = pd.DataFrame(nome_jogadores)

    df_jogadores["Nome"] = df_jogadores["Player_ID"].map(
        dict(zip(nome_jogadores["id"], nome_jogadores["full_name"]))
    )

    # filtro_jogador = st.selectbox("Selecione o Jogador:",df_jogadores['Nome'])
    # filtro1 = df_jogadores['Nome'] == filtro_jogador

    # df_jogadores = df_jogadores[filtro1]

    col1, col2 = st.columns(2)
    # Calcular a média de pontos para cada time
    df_jogadores_ataque = df_jogadores.groupby("Nome")["PTS"].mean().reset_index()

    # Ordenar o DataFrame de ranking pela média de pontos em ordem decrescente
    df_jogadores_ataque = df_jogadores_ataque.sort_values(
        by="PTS", ascending=False
    ).reset_index(drop=True)
    df_jogadores_ataque.index = df_jogadores_ataque.index + 1

    # Renomear as colunas se necessário
    df_jogadores_ataque.columns = ["Nome", "PTS"]

    col1.subheader("Líderes Ofensivos")
    col1.dataframe(df_jogadores_ataque)

    # Calcular a média de pontos para cada time
    df_jogadores_ast = df_jogadores.groupby("Nome")["AST"].mean().reset_index()

    # Ordenar o DataFrame de ranking pela média de pontos em ordem decrescente
    df_jogadores_ast = df_jogadores_ast.sort_values(
        by="AST", ascending=False
    ).reset_index(drop=True)
    df_jogadores_ast.index = df_jogadores_ast.index + 1

    # Renomear as colunas se necessário
    df_jogadores_ast.columns = ["Nome", "AST"]

    col2.subheader("Líderes Assistências")
    col2.dataframe(df_jogadores_ast)

    # Calcular a média de pontos para cada time
    df_jogadores_reb = df_jogadores.groupby("Nome")["REB"].mean().reset_index()

    # Ordenar o DataFrame de ranking pela média de pontos em ordem decrescente
    df_jogadores_reb = df_jogadores_reb.sort_values(
        by="REB", ascending=False
    ).reset_index(drop=True)
    df_jogadores_reb.index = df_jogadores_reb.index + 1

    # Renomear as colunas se necessário
    df_jogadores_reb.columns = ["Nome", "REB"]

    col1.subheader("Líderes Rebotes")
    col1.dataframe(df_jogadores_reb)

    # Calcular a média de pontos para cada time
    df_jogadores_blk = df_jogadores.groupby("Nome")["BLK"].mean().reset_index()

    # Ordenar o DataFrame de ranking pela média de pontos em ordem decrescente
    df_jogadores_blk = df_jogadores_blk.sort_values(
        by="BLK", ascending=False
    ).reset_index(drop=True)
    df_jogadores_blk.index = df_jogadores_blk.index + 1

    # Renomear as colunas se necessário
    df_jogadores_blk.columns = ["Nome", "BLK"]

    col2.subheader("Líderes Tocos")
    col2.dataframe(df_jogadores_blk)

    # Supondo que você tenha a coluna 'Game_ID' que representa o identificador único de cada jogo

    # Adicionando uma coluna 'Data' para poder ordenar os jogos por data
    df_jogadores["Data"] = pd.to_datetime(df_jogadores["GAME_DATE"])

    # Ordenando o DataFrame por jogador e data
    df_jogadores = df_jogadores.sort_values(by=["Nome", "Data"])

    # Calculando a média dos últimos 4 jogos para cada jogador
    df_jogadores_ultimos4 = (
        df_jogadores.groupby("Nome")
        .tail(4)
        .groupby("Nome")[["PTS", "AST", "REB", "BLK"]]
        .mean()
        .reset_index()
    )

    # Calculando a média geral da temporada para cada jogador
    df_jogadores_geral = (
        df_jogadores.groupby("Nome")[["PTS", "AST", "REB", "BLK"]].mean().reset_index()
    )

    # Juntando as médias dos últimos 4 jogos e a média geral da temporada
    df_comparacao = pd.merge(
        df_jogadores_ultimos4,
        df_jogadores_geral,
        on="Nome",
        suffixes=("_Ultimos4", "_Geral"),
    )

    # Adicionando uma coluna para a soma de PTS, AST, REB
    df_comparacao["Soma_PTS_AST_REB_Ultimos4"] = (
        df_comparacao["PTS_Ultimos4"]
        + df_comparacao["AST_Ultimos4"]
        + df_comparacao["REB_Ultimos4"]
    )
    df_comparacao["Soma_PTS_AST_REB_Geral"] = (
        df_comparacao["PTS_Geral"]
        + df_comparacao["AST_Geral"]
        + df_comparacao["REB_Geral"]
    )

    # Comparando as médias e somas
    df_comparacao["PTS_Acima_Media"] = (
        df_comparacao["PTS_Ultimos4"] - df_comparacao["PTS_Geral"]
    )
    df_comparacao["AST_Acima_Media"] = (
        df_comparacao["AST_Ultimos4"] - df_comparacao["AST_Geral"]
    )
    df_comparacao["REB_Acima_Media"] = (
        df_comparacao["REB_Ultimos4"] - df_comparacao["REB_Geral"]
    )
    df_comparacao["Soma_PTS_AST_REB_Acima_Media"] = (
        df_comparacao["Soma_PTS_AST_REB_Ultimos4"]
        - df_comparacao["Soma_PTS_AST_REB_Geral"]
    )

    # Função para aplicar estilos condicionais
    def highlight_col(val):
        color = "lightgreen" if val > 0 else "lightcoral"
        return f"background-color: {color}"

    # Renomeia Colunas
    novos_nomes = {
        "PTS_Ultimos4": "4_PTS",
        "AST_Ultimos4": "4_AST",
        "REB_Ultimos4": "4_REB",
        "BLK_Ultimos4": "4_BLK",
        "PTS_Geral": "PTS",
        "AST_Geral": "AST",
        "REB_Geral": "REB",
        "BLK_Geral": "BLK",
        "Soma_PTS_AST_REB_Ultimos4": "4_TOTAL",
        "Soma_PTS_AST_REB_Geral": "GERAL",
        "PTS_Acima_Media": "D_PTS",
        "AST_Acima_Media": "D_AST",
        "REB_Acima_Media": "D_REB",
        "Soma_PTS_AST_REB_Acima_Media": "D_TOTAL",
    }

    # Renomeia as colunas
    df = df_comparacao.rename(columns=novos_nomes)

    # Reordenar colunas
    ordem = [
        "Nome",
        "4_PTS",
        "PTS",
        "D_PTS",
        "4_AST",
        "AST",
        "D_AST",
        "4_REB",
        "REB",
        "D_REB",
        "4_BLK",
        "BLK",
        "4_TOTAL",
        "GERAL",
        "D_TOTAL",
    ]

    df = df[ordem]

    # Aplica estilos condicionais apenas nas colunas desejadas
    styled_df = df.style.applymap(
        highlight_col, subset=pd.IndexSlice[:, ["D_PTS", "D_AST", "D_REB", "D_TOTAL"]]
    )

    # Exibindo os resultados
    st.dataframe(styled_df)
