import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="ONI - El Niño Analysis",
    page_icon="🌊",
    layout="wide"
)

# ── Estilo ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #1e3a5f, #2d6a9f);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    color: white;
    margin: 5px;
}
.metric-card h2 { font-size: 2rem; margin: 0; }
.metric-card p  { font-size: 0.85rem; margin: 0; opacity: 0.8; }
.elnino   { background: linear-gradient(135deg, #b22222, #e74c3c); }
.lanina   { background: linear-gradient(135deg, #1a5276, #2980b9); }
.neutro   { background: linear-gradient(135deg, #1d6a40, #27ae60); }
.warning-box {
    background: #fff3cd; border-left: 4px solid #ffc107;
    padding: 12px 16px; border-radius: 6px; color: #856404;
}
</style>
""", unsafe_allow_html=True)

# ── Funções de dados ─────────────────────────────────────────────────────────
MESES = ["DJF","JFM","FMA","MAM","AMJ","MJJ","JJA","JAS","ASO","SON","OND","NDJ"]

@st.cache_data(ttl=3600)
def carregar_oni():
    """Scraping da tabela ONI do site NOAA/CPC."""
    url = "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Tenta encontrar tabela com dados numéricos
        tabela = None
        for t in soup.find_all("table"):
            texto = t.get_text()
            if "1950" in texto or "1951" in texto:
                tabela = t
                break

        if tabela is None:
            raise ValueError("Tabela ONI não encontrada na página.")

        rows = tabela.find_all("tr")
        dados = []

        for row in rows:
            cols = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
            # Linha válida: primeira coluna é ano numérico e tem ao menos 13 colunas
            if len(cols) >= 13 and cols[0].isdigit() and 1950 <= int(cols[0]) <= 2100:
                ano = int(cols[0])
                for i, mes in enumerate(MESES):
                    try:
                        val = cols[i + 1].replace("−", "-").replace("–", "-")
                        dados.append({"ano": ano, "mes_tri": mes, "oni": float(val)})
                    except (ValueError, IndexError):
                        pass

        if not dados:
            raise ValueError("Nenhum dado ONI extraído — estrutura da página pode ter mudado.")

        df = pd.DataFrame(dados)
        ordem = {m: i for i, m in enumerate(MESES)}
        df["mes_idx"] = df["mes_tri"].map(ordem)
        df = df.sort_values(["ano", "mes_idx"]).reset_index(drop=True)
        df["periodo"] = df["ano"].astype(str) + "-" + df["mes_tri"]
        df["idx"] = range(len(df))
        return df

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        st.info("Tentando carregar dados de fallback embutidos…")
        return pd.DataFrame()


def classificar(oni):
    if oni >= 1.5:  return "El Niño Forte/Muito Forte"
    if oni >= 1.0:  return "El Niño Moderado"
    if oni >= 0.5:  return "El Niño Fraco"
    if oni <= -1.5: return "La Niña Forte/Muito Forte"
    if oni <= -1.0: return "La Niña Moderado"
    if oni <= -0.5: return "La Niña Fraco"
    return "Neutro"

def cor_oni(oni):
    if oni >= 1.5:  return "#8B0000"
    if oni >= 1.0:  return "#cc2200"
    if oni >= 0.5:  return "#e67e22"
    if oni <= -1.5: return "#003580"
    if oni <= -1.0: return "#1a6fbf"
    if oni <= -0.5: return "#5dade2"
    return "#27ae60"

# ── Carregamento ─────────────────────────────────────────────────────────────
st.title("🌊 Análise ONI — El Niño / La Niña")
st.caption("Fonte: NOAA/CPC — Oceanic Niño Index (ONI) v5 · Região Niño 3.4")

with st.spinner("Carregando dados históricos do NOAA…"):
    df = carregar_oni()

if df.empty:
    st.stop()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Filtros")
    anos = sorted(df["ano"].unique())
    ano_ini, ano_fim = st.select_slider(
        "Período de análise",
        options=anos,
        value=(anos[0], anos[-1])
    )
    limiar = st.slider("Limiar El Niño / La Niña (°C)", 0.3, 1.0, 0.5, 0.1)
    st.markdown("---")
    st.markdown("**O que é o ONI?**")
    st.info(
        "O Oceanic Niño Index mede a anomalia de temperatura "
        "da superfície do mar na região Niño 3.4 (5°N–5°S, "
        "120°–170°W) usando médias de 3 meses consecutivos."
    )

df_filt = df[(df["ano"] >= ano_ini) & (df["ano"] <= ano_fim)].copy()
df_filt["fase"] = df_filt["oni"].apply(classificar)

# ── Métricas + Mapa ───────────────────────────────────────────────────────────
elninos = df_filt[df_filt["oni"] >= limiar]
laninas  = df_filt[df_filt["oni"] <= -limiar]
neutros  = df_filt[(df_filt["oni"] > -limiar) & (df_filt["oni"] < limiar)]
ultimo = df_filt.iloc[-1]
oni_max = df_filt["oni"].max()

col_mapa, col_cards = st.columns([2, 3])

with col_cards:
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.markdown(f"""
        <div class="metric-card">
            <p>Último ONI ({ultimo['periodo']})</p>
            <h2>{ultimo['oni']:+.2f}°C</h2>
            <p>{classificar(ultimo['oni'])}</p>
        </div>""", unsafe_allow_html=True)
    with r1c2:
        st.markdown(f"""
        <div class="metric-card elnino">
            <p>ONI Máximo Histórico</p>
            <h2>{oni_max:+.2f}°C</h2>
            <p>{df_filt.loc[df_filt['oni'].idxmax(),'periodo']}</p>
        </div>""", unsafe_allow_html=True)

    r2c1, r2c2, r2c3 = st.columns(3)
    with r2c1:
        st.markdown(f"""
        <div class="metric-card elnino">
            <p>Trimestres El Niño</p>
            <h2>{len(elninos)}</h2>
            <p>{len(elninos)/len(df_filt)*100:.1f}% do período</p>
        </div>""", unsafe_allow_html=True)
    with r2c2:
        st.markdown(f"""
        <div class="metric-card lanina">
            <p>Trimestres La Niña</p>
            <h2>{len(laninas)}</h2>
            <p>{len(laninas)/len(df_filt)*100:.1f}% do período</p>
        </div>""", unsafe_allow_html=True)
    with r2c3:
        st.markdown(f"""
        <div class="metric-card neutro">
            <p>Trimestres Neutros</p>
            <h2>{len(neutros)}</h2>
            <p>{len(neutros)/len(df_filt)*100:.1f}% do período</p>
        </div>""", unsafe_allow_html=True)

with col_mapa:
    st.caption("🗺️ Regiões de Monitoramento ENSO")
    fig_map = go.Figure()
    fig_map.add_trace(go.Scattergeo(
        lon=[-170, -120, -120, -170, -170],
        lat=[5, 5, -5, -5, 5],
        mode="lines", fill="toself",
        fillcolor="rgba(220,50,50,0.30)",
        line=dict(color="#c0392b", width=2),
        name="Niño 3.4 ⭐", hoverinfo="name"
    ))
    outras_regioes = [
        ("Niño 1+2", [-90,-80,-80,-90,-90],     [-10,-10,0,0,-10],   "rgba(231,76,60,0.12)",  "#e74c3c"),
        ("Niño 3",   [-150,-90,-90,-150,-150],   [-5,-5,5,5,-5],      "rgba(243,156,18,0.12)", "#f39c12"),
        ("Niño 4",   [-200,-150,-150,-200,-200], [-5,-5,5,5,-5],      "rgba(52,152,219,0.12)", "#3498db"),
    ]
    for nome, lons_r, lats_r, fill, cor in outras_regioes:
        fig_map.add_trace(go.Scattergeo(
            lon=lons_r, lat=lats_r, mode="lines",
            fill="toself", fillcolor=fill,
            line=dict(color=cor, width=1.2, dash="dot"),
            name=nome, hoverinfo="name"
        ))
    fig_map.add_trace(go.Scattergeo(
        lon=[-145], lat=[0], mode="markers+text",
        marker=dict(size=5, color="#c0392b"),
        text=["3.4"], textposition="top center",
        textfont=dict(size=11, color="#c0392b"),
        showlegend=False, hoverinfo="skip"
    ))
    fig_map.update_layout(
        height=320, margin=dict(t=0, b=40, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h", y=-0.12, x=0.5, xanchor="center",
            font=dict(size=10), bgcolor="rgba(0,0,0,0)",
        ),
        geo=dict(
            projection_type="natural earth",
            showland=True, landcolor="#f0f0e8",
            showocean=True, oceancolor="#d6eaf8",
            showcoastlines=True, coastlinecolor="#aaaaaa",
            showcountries=True, countrycolor="#cccccc",
            showframe=False,
            lonaxis=dict(range=[-220, -60]),
            lataxis=dict(range=[-25, 25]),
            bgcolor="rgba(0,0,0,0)"
        )
    )
    st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# ── Gráfico principal ─────────────────────────────────────────────────────────
st.subheader("📈 Série Histórica do ONI")

fig = go.Figure()

# Área vermelha — valores acima de 0 (El Niño)
fig.add_trace(go.Scatter(
    x=df_filt["periodo"],
    y=df_filt["oni"].clip(lower=0),
    fill="tozeroy",
    fillcolor="rgba(220,50,50,0.35)",
    line=dict(color="rgba(0,0,0,0)"),
    showlegend=False, hoverinfo="skip"
))

# Área azul — valores abaixo de 0 (La Niña)
fig.add_trace(go.Scatter(
    x=df_filt["periodo"],
    y=df_filt["oni"].clip(upper=0),
    fill="tozeroy",
    fillcolor="rgba(50,100,220,0.35)",
    line=dict(color="rgba(0,0,0,0)"),
    showlegend=False, hoverinfo="skip"
))

# Linha principal
fig.add_trace(go.Scatter(
    x=df_filt["periodo"], y=df_filt["oni"],
    mode="lines",
    line=dict(color="#2c3e50", width=1.5),
    name="ONI",
    hovertemplate="<b>%{x}</b><br>ONI: %{y:.2f}°C<extra></extra>"
))

# Limiares
for val, cor, label in [(limiar,"#c0392b",f"+{limiar}°C El Niño"),
                         (-limiar,"#2980b9",f"-{limiar}°C La Niña"),
                         (1.5,"#7b241c","El Niño Forte"),
                         (-1.5,"#1a5276","La Niña Forte")]:
    fig.add_hline(y=val, line=dict(color=cor, width=1.2, dash="dash"),
                  annotation_text=label,
                  annotation_position="bottom right",
                  annotation_font=dict(color=cor, size=12)) 
fig.update_layout(
    height=450, paper_bgcolor="#FFFFFF", plot_bgcolor="#f9f9f9",
    xaxis=dict(
        title="Período", tickangle=-45,
        tickmode="array",
        tickvals=df_filt["periodo"][::12].tolist(),
        tickfont=dict(color="#333333"),
        title_font=dict(color="#333333"),
        gridcolor="#e0e0e0",
        linecolor="#cccccc"
    ),
    yaxis=dict(
        title="Anomalia SST (°C)",
        zeroline=True,
        zerolinecolor="#888888",
        zerolinewidth=1.5,
        tickfont=dict(color="#333333"),
        title_font=dict(color="#333333"),
        gridcolor="#e0e0e0",
        linecolor="#cccccc"
    ),
    hovermode="x unified",
    margin=dict(t=20, b=80),
    font=dict(color="#333333"),
    legend=dict(orientation="h", y=-0.25, font=dict(color="#333333"))
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption(
    "Dados: [NOAA/CPC ONI v5](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php) · "
    "Análise exploratória — não use para decisões operacionais sem consultar o ENSO Outlook oficial."
)