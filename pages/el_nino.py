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

# ── Google Earth Engine ───────────────────────────────────────────────────────
import json

try:
    import ee

    if "gee" in st.secrets:
        # ── Streamlit Cloud: autenticação via Service Account (st.secrets)
        _creds = dict(st.secrets["gee"])
        _credentials = ee.ServiceAccountCredentials(
            email=_creds["client_email"], key_data=json.dumps(_creds)
        )
        ee.Initialize(_credentials, project=_creds["project_id"])
    else:
        # ── Local: autenticação via earthengine authenticate
        ee.Initialize(project="agriphenoscan")

    GEE_OK = True
    _GEE_ERR_MSG = ""
except Exception as _gee_err:
    GEE_OK = False
    _GEE_ERR_MSG = str(_gee_err)

st.set_page_config(page_title="ONI - El Niño Analysis", page_icon="🌊", layout="wide")

# ── Estilo ──────────────────────────────────────────────────────────────────
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

# ── Funções de dados ─────────────────────────────────────────────────────────
MESES = [
    "DJF",
    "JFM",
    "FMA",
    "MAM",
    "AMJ",
    "MJJ",
    "JJA",
    "JAS",
    "ASO",
    "SON",
    "OND",
    "NDJ",
]


@st.cache_data(ttl=3600)
def carregar_oni():
    """Scraping da tabela ONI do site NOAA/CPC."""
    url = "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
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
            # Linha válida: primeira coluna é ano numérico; aceita linhas parciais
            if len(cols) >= 2 and cols[0].isdigit() and 1950 <= int(cols[0]) <= 2100:
                ano = int(cols[0])
                n_cols_meses = min(len(MESES), len(cols) - 1)
                for i in range(n_cols_meses):
                    mes = MESES[i]
                    try:
                        val = cols[i + 1].replace("−", "-").replace("–", "-")
                        dados.append({"ano": ano, "mes_tri": mes, "oni": float(val)})
                    except (ValueError, IndexError):
                        pass

        if not dados:
            raise ValueError(
                "Nenhum dado ONI extraído — estrutura da página pode ter mudado."
            )

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
    if oni >= 1.5:
        return "El Niño Forte/Muito Forte"
    if oni >= 1.0:
        return "El Niño Moderado"
    if oni >= 0.5:
        return "El Niño Fraco"
    if oni <= -1.5:
        return "La Niña Forte/Muito Forte"
    if oni <= -1.0:
        return "La Niña Moderado"
    if oni <= -0.5:
        return "La Niña Fraco"
    return "Neutro"


def cor_oni(oni):
    if oni >= 1.5:
        return "#8B0000"
    if oni >= 1.0:
        return "#cc2200"
    if oni >= 0.5:
        return "#e67e22"
    if oni <= -1.5:
        return "#003580"
    if oni <= -1.0:
        return "#1a6fbf"
    if oni <= -0.5:
        return "#5dade2"
    return "#27ae60"


# ── GEE — SST Niño 3.4 ───────────────────────────────────────────────────────
NINO34_GEOM = [-170, -5, -120, 5]  # lon_min, lat_min, lon_max, lat_max


@st.cache_data(ttl=86400)
def carregar_sst_gee(ano_ini: int, ano_fim: int) -> pd.DataFrame:
    """
    Busca SST mensal média na região Niño 3.4 via GEE.
    Agrega mensalmente NO SERVIDOR GEE para evitar o limite de 5000 elementos.
    Dataset: NOAA/CDR/OISST/V2_1 — banda 'sst' em °C.
    Calcula anomalia em relação à climatologia 1991-2020.
    """
    regiao = ee.Geometry.Rectangle(NINO34_GEOM)
    data_inicio = ee.Date(f"{ano_ini}-01-01")
    n_meses = int((ano_fim - ano_ini) * 12 + 12)  # Ensure int, not numpy.int64
    meses = ee.List.sequence(0, n_meses - 1)

    def _media_mensal(n):
        inicio = data_inicio.advance(ee.Number(n), "month")
        fim = inicio.advance(1, "month")
        img_m = (
            ee.ImageCollection("NOAA/CDR/OISST/V2_1")
            .select("sst")
            .filterDate(inicio, fim)
            .filterBounds(regiao)
            .mean()
        )
        stats = img_m.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=regiao,
            scale=25000,
            maxPixels=1e9,
            bestEffort=True,
        )
        # Só retorna se a chave 'sst' existir
        sst_val = ee.Algorithms.If(stats.contains("sst"), stats.get("sst"), None)
        return ee.Feature(None, {"data": inicio.format("YYYY-MM"), "sst": sst_val})

    feats = ee.FeatureCollection(meses.map(_media_mensal)).getInfo()["features"]

    registros = []
    for f in feats:
        props = f.get("properties", {}) if isinstance(f, dict) else {}
        sst_val = props.get("sst")
        data_val = props.get("data")
        if sst_val is not None and data_val is not None:
            registros.append({"data": data_val, "sst_gee": sst_val})
    if not registros:
        return pd.DataFrame()

    df_gee = pd.DataFrame(registros)
    df_gee["data"] = pd.to_datetime(df_gee["data"])
    df_gee = df_gee.sort_values("data").reset_index(drop=True)

    # Climatologia 1991-2020
    clima = (
        df_gee[(df_gee["data"].dt.year >= 1991) & (df_gee["data"].dt.year <= 2020)]
        .groupby(df_gee["data"].dt.month)["sst_gee"]
        .mean()
    )
    df_gee["anomalia_gee"] = df_gee.apply(
        lambda r: r["sst_gee"] - clima.get(r["data"].month, np.nan), axis=1
    )
    df_gee["periodo_label"] = df_gee["data"].dt.strftime("%Y-%m")
    return df_gee


TRI_FROM_END_MONTH = {
    1: "NDJ",
    2: "DJF",
    3: "JFM",
    4: "FMA",
    5: "MAM",
    6: "AMJ",
    7: "MJJ",
    8: "JJA",
    9: "JAS",
    10: "ASO",
    11: "SON",
    12: "OND",
}


def agregar_gee_trimestral(df_gee_mensal: pd.DataFrame) -> pd.DataFrame:
    if df_gee_mensal.empty:
        return pd.DataFrame()
    d = df_gee_mensal.sort_values("data").copy()
    d["anomalia_trim"] = d["anomalia_gee"].rolling(3, min_periods=3).mean()
    d = d.dropna(subset=["anomalia_trim"]).copy()
    d["mes_tri"] = d["data"].dt.month.map(TRI_FROM_END_MONTH)
    d["ano"] = d["data"].dt.year
    d["mes_idx"] = d["mes_tri"].map({m: i for i, m in enumerate(MESES)})
    return d[["data", "ano", "mes_tri", "mes_idx", "anomalia_trim"]].reset_index(
        drop=True
    )


def extrair_eventos_extremos_oni(df_oni: pd.DataFrame):
    d = df_oni.sort_values(["ano", "mes_idx"]).reset_index(drop=True)
    eventos, corrente = [], []

    def _finalizar(bloco):
        if not bloco:
            return
        b = pd.DataFrame(bloco)
        pico = float(b["oni"].max())
        if pico >= 1.5:
            pico_row = b.loc[b["oni"].idxmax()]
            eventos.append(
                {
                    "start_ano": int(b.iloc[0]["ano"]),
                    "peak_ano": int(pico_row["ano"]),
                    "peak_oni": pico,
                    "rows": b.copy(),
                }
            )

    for _, row in d.iterrows():
        if row["oni"] >= 0.5:
            corrente.append(row.to_dict())
        else:
            _finalizar(corrente)
            corrente = []
    _finalizar(corrente)
    return eventos


def percentile_tie_avg(x: float, hist: pd.Series):
    h = hist.dropna().sort_values().reset_index(drop=True)
    if len(h) == 0:
        return np.nan
    eq = h[h == x]
    if len(eq) > 0:
        i0 = eq.index.min() + 1
        i1 = eq.index.max() + 1
        return ((i0 + i1) / 2.0) / len(h) * 100.0
    return (h < x).sum() / len(h) * 100.0


def zscore_amostral(x: float, hist: pd.Series):
    h = hist.dropna()
    if len(h) < 2:
        return np.nan
    std = h.std(ddof=1)
    if std == 0:
        return 0.0
    return (x - h.mean()) / std


def metricas_por_trimestre(
    df_hist: pd.DataFrame, df_atual: pd.DataFrame, col_valor: str
):
    if df_atual.empty:
        return pd.DataFrame()
    linhas = []
    atual = df_atual.sort_values(["ano", "mes_idx"]).copy()
    atual["delta_atual"] = atual[col_valor].diff()
    for _, r in atual.iterrows():
        hist = df_hist[df_hist["mes_tri"] == r["mes_tri"]][col_valor].dropna()
        linhas.append(
            {
                "ano": int(r["ano"]),
                "mes_tri": r["mes_tri"],
                "valor_atual": float(r[col_valor]),
                "delta_atual": float(r["delta_atual"])
                if pd.notna(r["delta_atual"])
                else np.nan,
                "n_hist": int(len(hist)),
                "percentil": percentile_tie_avg(float(r[col_valor]), hist),
                "zscore": zscore_amostral(float(r[col_valor]), hist),
            }
        )
    return pd.DataFrame(linhas)


def mediana_delta_historica(df_hist: pd.DataFrame, col_valor: str):
    if df_hist.empty or "event_id" not in df_hist.columns:
        return np.nan
    h = df_hist.sort_values(["event_id", "ano", "mes_idx"]).copy()
    h["delta"] = h.groupby("event_id")[col_valor].diff()
    return h["delta"].median()


def diagnostico_potencial(
    m_oni: pd.DataFrame, m_gee: pd.DataFrame, n_eventos: int, ultimo_periodo: str
):
    banner = "Analise comparativa historica; nao substitui previsao oficial NOAA."
    if n_eventos < 8 or m_oni.empty:
        return {
            "titulo": "Diagnostico parcial",
            "bullets": [
                "Evidencia limitada pela cobertura atual ou amostra historica insuficiente."
            ],
            "banner": banner,
        }

    u_oni = m_oni.iloc[-1]
    p_vals = [u_oni["percentil"]]
    d_oni_ok = bool(
        pd.notna(u_oni["delta_atual"])
        and pd.notna(u_oni.get("mediana_delta_hist", np.nan))
        and (u_oni["delta_atual"] > u_oni["mediana_delta_hist"])
    )
    d_gee_ok = False

    if not m_gee.empty:
        u_gee = m_gee.iloc[-1]
        p_vals.append(u_gee["percentil"])
        d_gee_ok = bool(
            pd.notna(u_gee["delta_atual"])
            and pd.notna(u_gee.get("mediana_delta_hist", np.nan))
            and (u_gee["delta_atual"] > u_gee["mediana_delta_hist"])
        )

    p_media = (
        float(np.nanmean([v for v in p_vals if pd.notna(v)])) if len(p_vals) else np.nan
    )
    acelerando = d_oni_ok or d_gee_ok

    if pd.notna(p_media) and p_media >= 80 and acelerando:
        titulo = "Potencial elevado"
        leitura = "sinal de aquecimento em faixa alta vs eventos extremos historicos"
    elif pd.notna(p_media) and p_media >= 60:
        titulo = "Sinal relevante"
        leitura = "aquecimento relevante, ainda sem caracterizacao excepcional robusta"
    else:
        titulo = "Sinal moderado"
        leitura = "aquecimento presente, mas abaixo do patamar historico mais extremo"

    bullets = [
        f"Periodo mais recente avaliado: {ultimo_periodo}.",
        f"Percentil composto (ONI/GEE): {p_media:.1f}.",
        f"Leitura: {leitura}.",
    ]
    return {"titulo": titulo, "bullets": bullets, "banner": banner}


# ── Carregamento ─────────────────────────────────────────────────────────────

st.title("🌊 Análise ONI — El Niño / La Niña")
st.caption("Fonte: NOAA/CPC — Oceanic Niño Index (ONI) v5 · Região Niño 3.4")

# ── Explicação Super El Niño 2026 ──
st.markdown(
    """
<div style='background: linear-gradient(90deg, #fff4ef 0%, #fffdf5 100%); border-left: 6px solid #e74c3c; padding: 18px 20px 10px 20px; border-radius: 8px; margin-bottom: 18px; color:#1f2937; line-height:1.6;'>
<b>Por que se fala em um <span style='color:#c0392b;'>Super El Niño</span> em 2026?</b><br>
As discussões sobre ganharam força porque os principais modelos meteorológicos detectaram um <b>aquecimento rápido e incomum</b> das águas superficiais do Oceano Pacífico Equatorial.<br>

<i>Nesta análise, comparamos os dados atuais com os maiores eventos extremos do passado (segundo o ONI da NOAA e a série histórica do NOAA CDR OISST) para entender o que fundamenta essa expectativa.</i>

""",
    unsafe_allow_html=True,
)

with st.spinner("Carregando dados históricos do NOAA…"):
    df = carregar_oni()

if df.empty:
    st.stop()


# ── Sem filtros: análise automática dos eventos extremos ─────────────────────
col_oni, col_oisst = st.columns(2)

with col_oni:
    st.markdown("**O que é o ONI?**")
    st.info(
        "O Oceanic Niño Index mede a anomalia de temperatura "
        "da superfície do mar na região Niño 3.4 (5°N–5°S, "
        "120°–170°W) usando médias de 3 meses consecutivos."
    )

with col_oisst:
    st.markdown("**O que é  NOAA CDR OISST?**")
    st.info(
        "Conjuntos de dados de temperatura da superfície do mar (SST) "
        "fornecidos pela NOAA. Usamos a versão "
        "NOAA/CDR/OISST/V2_1 via a API GEE para calcular médias e anomalias na região Niño 3.4. "
    )

# Seleciona os anos dos maiores eventos (top 3 do ranking)
df_sorted = df.sort_values(["ano", "mes_idx"]).copy()
df_sorted["elnino"] = df_sorted["oni"] >= 0.5
eventos = []
em_evento = False
pico = -999
ano_pico = None
mes_pico = None
inicio_ano = None
for _, row in df_sorted.iterrows():
    if row["elnino"]:
        if not em_evento:
            em_evento = True
            inicio_ano = row["ano"]
            pico = row["oni"]
            ano_pico = row["ano"]
            mes_pico = row["mes_tri"]
        elif row["oni"] > pico:
            pico = row["oni"]
            ano_pico = row["ano"]
            mes_pico = row["mes_tri"]
    else:
        if em_evento and pico >= 1.0:
            eventos.append(
                {
                    "Evento": f"{inicio_ano}–{str(ano_pico)[-2:]}",
                    "Pico ONI (°C)": round(pico, 2),
                    "Trimestre Pico": mes_pico,
                    "Intensidade": classificar(pico),
                }
            )
        em_evento = False
        pico = -999
df_rank = (
    pd.DataFrame(eventos)
    .sort_values("Pico ONI (°C)", ascending=False)
    .reset_index(drop=True)
)
df_rank.index += 1
ano_gee_fim = int(df["ano"].max())
ano_gee_ini = int(df["ano"].min())

# Baixa dados do GEE para janela anual recente (sem filtro por pico ONI)
if GEE_OK:
    with st.spinner("Baixando dados do GEE para série mensal (histórico completo)…"):
        df_gee_extremos = carregar_sst_gee(ano_gee_ini, ano_gee_fim)
else:
    st.error(f"GEE não autenticado: {_GEE_ERR_MSG}")
    df_gee_extremos = pd.DataFrame()

# Para manter compatibilidade com o restante do código, define df_filt como todos os dados
df_filt = df.copy()
df_filt["fase"] = df_filt["oni"].apply(classificar)

limiar = 0.5  # Limiar fixo para El Niño/La Niña
elninos = df_filt[df_filt["oni"] >= limiar]
laninas = df_filt[df_filt["oni"] <= -limiar]
neutros = df_filt[(df_filt["oni"] > -limiar) & (df_filt["oni"] < limiar)]
ultimo = df_filt.iloc[-1]
oni_max = df_filt["oni"].max()

ultimo_gee_txt = "sem dado recente"
if GEE_OK and not df_gee_extremos.empty and "anomalia_gee" in df_gee_extremos.columns:
    gee_valid = df_gee_extremos.dropna(subset=["anomalia_gee"]).sort_values("data")
    if not gee_valid.empty:
        ultimo_gee = gee_valid.iloc[-1]
        ultimo_gee_txt = f"{float(ultimo_gee['anomalia_gee']):+.2f}°C ({ultimo_gee['data'].strftime('%Y-%m')})"

if float(ultimo["oni"]) >= 0.5:
    leitura_oni = "ONI já em faixa de El Niño"
else:
    leitura_oni = "ONI ainda não indica El Niño"

col_mapa, col_cards = st.columns([2, 3])

with col_cards:
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.markdown(
            f"""
        <div class="metric-card">
            <p>Último ONI ({ultimo["periodo"]})</p>
            <h2>{ultimo["oni"]:+.2f}°C</h2>
            <p>{classificar(ultimo["oni"])}</p>
        </div>""",
            unsafe_allow_html=True,
        )
    with r1c2:
        st.markdown(
            f"""
        <div class="metric-card elnino">
            <p>ONI Máximo Histórico</p>
            <h2>{oni_max:+.2f}°C</h2>
            <p>{df_filt.loc[df_filt["oni"].idxmax(), "periodo"]}</p>
        </div>""",
            unsafe_allow_html=True,
        )

    r2c1, r2c2, r2c3 = st.columns(3)
    with r2c1:
        st.markdown(
            f"""
        <div class="metric-card elnino">
            <p>Trimestres El Niño</p>
            <h2>{len(elninos)}</h2>
            <p>{len(elninos) / len(df_filt) * 100:.1f}% do período</p>
        </div>""",
            unsafe_allow_html=True,
        )
    with r2c2:
        st.markdown(
            f"""
        <div class="metric-card lanina">
            <p>Trimestres La Niña</p>
            <h2>{len(laninas)}</h2>
            <p>{len(laninas) / len(df_filt) * 100:.1f}% do período</p>
        </div>""",
            unsafe_allow_html=True,
        )
    with r2c3:
        st.markdown(
            f"""
        <div class="metric-card neutro">
            <p>Trimestres Neutros</p>
            <h2>{len(neutros)}</h2>
            <p>{len(neutros) / len(df_filt) * 100:.1f}% do período</p>
        </div>""",
            unsafe_allow_html=True,
        )

with col_mapa:
    st.caption("🗺️ Regiões de Monitoramento ENSO")
    fig_map = go.Figure()
    fig_map.add_trace(
        go.Scattergeo(
            lon=[-170, -120, -120, -170, -170],
            lat=[5, 5, -5, -5, 5],
            mode="lines",
            fill="toself",
            fillcolor="rgba(220,50,50,0.30)",
            line=dict(color="#c0392b", width=2),
            name="Niño 3.4 ⭐",
            hoverinfo="name",
        )
    )
    outras_regioes = [
        (
            "Niño 1+2",
            [-90, -80, -80, -90, -90],
            [-10, -10, 0, 0, -10],
            "rgba(231,76,60,0.12)",
            "#e74c3c",
        ),
        (
            "Niño 3",
            [-150, -90, -90, -150, -150],
            [-5, -5, 5, 5, -5],
            "rgba(243,156,18,0.12)",
            "#f39c12",
        ),
        (
            "Niño 4",
            [-200, -150, -150, -200, -200],
            [-5, -5, 5, 5, -5],
            "rgba(52,152,219,0.12)",
            "#3498db",
        ),
    ]
    for nome, lons_r, lats_r, fill, cor in outras_regioes:
        fig_map.add_trace(
            go.Scattergeo(
                lon=lons_r,
                lat=lats_r,
                mode="lines",
                fill="toself",
                fillcolor=fill,
                line=dict(color=cor, width=1.2, dash="dot"),
                name=nome,
                hoverinfo="name",
            )
        )
    fig_map.add_trace(
        go.Scattergeo(
            lon=[-145],
            lat=[0],
            mode="markers+text",
            marker=dict(size=5, color="#c0392b"),
            text=["3.4"],
            textposition="top center",
            textfont=dict(size=11, color="#c0392b"),
            showlegend=False,
            hoverinfo="skip",
        )
    )
    fig_map.update_layout(
        height=320,
        margin=dict(t=0, b=40, l=0, r=0),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h",
            y=-0.12,
            x=0.5,
            xanchor="center",
            font=dict(size=10),
            bgcolor="rgba(0,0,0,0)",
        ),
        geo=dict(
            projection_type="natural earth",
            showland=True,
            landcolor="#f0f0e8",
            showocean=True,
            oceancolor="#d6eaf8",
            showcoastlines=True,
            coastlinecolor="#aaaaaa",
            showcountries=True,
            countrycolor="#cccccc",
            showframe=False,
            lonaxis=dict(range=[-220, -60]),
            lataxis=dict(range=[-25, 25]),
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    st.plotly_chart(fig_map, use_container_width=True)

st.markdown(
    f"""
<div class="metric-card" style="background: linear-gradient(135deg, #1f4b7a, #2f6f9d); min-height: 150px; padding: 22px 24px;">
    <p>O que os dados dizem ?</p>
    <h2 style="font-size:1.55rem; line-height:1.35; margin: 10px 0 12px 0;">Há aquecimento no mar, mas sem confirmação El Niño</h2>
    <p>Anomalia °C: {ultimo_gee_txt} · {leitura_oni}</p>
    <p style="margin-top:8px; opacity:0.95;">El Niño não depende apenas da temperatura do mar: também envolve mudanças nos ventos alísios e na pressão atmosférica (Oscilação Sul).</p>
    <p style="margin-top:8px; opacity:0.95;">Analise os dados abaixo para entender melhor o fenômeno.</p>
</div>""",
    unsafe_allow_html=True,
)

st.markdown("---")

# ── Gráfico principal ─────────────────────────────────────────────────────────
st.subheader("📈 Série Histórica do ONI")
st.caption("Dados trimestrais do ONI (1950–presente) para a região Niño 3.4. ")

fig = go.Figure()

# Área vermelha — valores acima de 0 (El Niño)
fig.add_trace(
    go.Scatter(
        x=df_filt["periodo"],
        y=df_filt["oni"].clip(lower=0),
        fill="tozeroy",
        fillcolor="rgba(220,50,50,0.35)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False,
        hoverinfo="skip",
    )
)

# Área azul — valores abaixo de 0 (La Niña)
fig.add_trace(
    go.Scatter(
        x=df_filt["periodo"],
        y=df_filt["oni"].clip(upper=0),
        fill="tozeroy",
        fillcolor="rgba(50,100,220,0.35)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False,
        hoverinfo="skip",
    )
)

# Linha principal
fig.add_trace(
    go.Scatter(
        x=df_filt["periodo"],
        y=df_filt["oni"],
        mode="lines",
        line=dict(color="#2c3e50", width=1.5),
        name="ONI",
        hovertemplate="<b>%{x}</b><br>ONI: %{y:.2f}°C<extra></extra>",
    )
)

# Limiares
for val, cor, label in [
    (limiar, "#c0392b", f"+{limiar}°C El Niño"),
    (-limiar, "#2980b9", f"-{limiar}°C La Niña"),
    (1.5, "#7b241c", "El Niño Forte"),
    (-1.5, "#1a5276", "La Niña Forte"),
]:
    fig.add_hline(
        y=val,
        line=dict(color=cor, width=1.2, dash="dash"),
        annotation_text=label,
        annotation_position="bottom right",
        annotation_font=dict(color=cor, size=12),
    )
fig.update_layout(
    height=450,
    paper_bgcolor="#FFFFFF",
    plot_bgcolor="#f9f9f9",
    xaxis=dict(
        title="Período",
        tickangle=-45,
        tickmode="array",
        tickvals=list(
            dict.fromkeys(
                df_filt["periodo"][::12].tolist() + [df_filt.iloc[-1]["periodo"]]
            )
        ),
        tickfont=dict(color="#333333"),
        title_font=dict(color="#333333"),
        gridcolor="#e0e0e0",
        linecolor="#cccccc",
    ),
    yaxis=dict(
        title="Anomalia SST (°C)",
        zeroline=True,
        zerolinecolor="#888888",
        zerolinewidth=1.5,
        tickfont=dict(color="#333333"),
        title_font=dict(color="#333333"),
        gridcolor="#e0e0e0",
        linecolor="#cccccc",
    ),
    hovermode="x unified",
    margin=dict(t=20, b=80),
    font=dict(color="#333333"),
    legend=dict(orientation="h", y=-0.25, font=dict(color="#333333")),
)
fig_oni = fig

# ── Potencial 2026: anomalia mensal por ano (sem filtro por pico ONI) ───────
fig_gee = None
gee_warning_msg = None

if GEE_OK and not df_gee_extremos.empty:
    mes_labels = {
        1: "Jan",
        2: "Fev",
        3: "Mar",
        4: "Abr",
        5: "Mai",
        6: "Jun",
        7: "Jul",
        8: "Ago",
        9: "Set",
        10: "Out",
        11: "Nov",
        12: "Dez",
    }

    gee_anual = df_gee_extremos.copy()
    gee_anual["ano"] = gee_anual["data"].dt.year
    gee_anual["mes_num"] = gee_anual["data"].dt.month
    gee_anual["mes_label"] = gee_anual["mes_num"].map(mes_labels)

    ano_max = int(gee_anual["ano"].max())
    gee_anual = (
        gee_anual.groupby(["ano", "mes_num", "mes_label"], as_index=False)[
            "anomalia_gee"
        ]
        .mean()
        .sort_values(["ano", "mes_num"])
    )

    tri_para_mes_central = {
        "DJF": 1,
        "JFM": 2,
        "FMA": 3,
        "MAM": 4,
        "AMJ": 5,
        "MJJ": 6,
        "JJA": 7,
        "JAS": 8,
        "ASO": 9,
        "SON": 10,
        "OND": 11,
        "NDJ": 12,
    }
    picos_oni = []
    for ev in extrair_eventos_extremos_oni(df):
        bloco = ev["rows"]
        if bloco.empty:
            continue
        pico_row = bloco.loc[bloco["oni"].idxmax()]
        mes_num = tri_para_mes_central.get(str(pico_row["mes_tri"]))
        if mes_num is None:
            continue
        picos_oni.append(
            {
                "ano": int(pico_row["ano"]),
                "mes_num": int(mes_num),
                "oni_pico": float(pico_row["oni"]),
            }
        )
    df_picos_oni = pd.DataFrame(picos_oni)
    if not df_picos_oni.empty:
        df_picos_oni = (
            df_picos_oni.sort_values("oni_pico", ascending=False)
            .drop_duplicates(["ano", "mes_num"])
            .head(3)
        )

    if gee_anual.empty:
        gee_warning_msg = "Dados GEE insuficientes para o gráfico anual mensal."
    else:
        fig_gee = go.Figure()
        ano_foco = 2026 if (gee_anual["ano"] == 2026).any() else ano_max
        top5_anos = []
        if not df_picos_oni.empty:
            top5_anos = df_picos_oni["ano"].astype(int).tolist()

        paleta_top5 = ["#d35400", "#0ea5e9", "#16a34a", "#7c3aed", "#dc2626"]
        cor_top5 = {
            ano: paleta_top5[i % len(paleta_top5)] for i, ano in enumerate(top5_anos)
        }

        hist = gee_anual[
            (~gee_anual["ano"].isin(top5_anos)) & (gee_anual["ano"] != ano_foco)
        ]
        for ano, bloco in hist.groupby("ano"):
            fig_gee.add_trace(
                go.Scatter(
                    x=bloco["mes_label"],
                    y=bloco["anomalia_gee"],
                    mode="lines",
                    line=dict(color="rgba(148,163,184,0.35)", width=1.2),
                    showlegend=False,
                    hovertemplate=f"<b>{ano}</b><br>%{{x}}: %{{y:.2f}}°C<extra></extra>",
                )
            )

        fig_gee.add_trace(
            go.Scatter(
                x=[
                    "Jan",
                    "Fev",
                    "Mar",
                    "Abr",
                    "Mai",
                    "Jun",
                    "Jul",
                    "Ago",
                    "Set",
                    "Out",
                    "Nov",
                    "Dez",
                ],
                y=[None] * 12,
                mode="lines",
                line=dict(color="rgba(148,163,184,0.35)", width=2),
                name="Histórico (demais anos)",
                hoverinfo="skip",
            )
        )

        media_geral = (
            gee_anual.groupby(["mes_num", "mes_label"], as_index=False)["anomalia_gee"]
            .mean()
            .sort_values("mes_num")
        )
        fig_gee.add_trace(
            go.Scatter(
                x=media_geral["mes_label"],
                y=media_geral["anomalia_gee"],
                mode="lines+markers",
                line=dict(color="#0ea5e9", width=2.8, dash="dash"),
                marker=dict(size=6),
                name="Média histórica",
                hovertemplate="<b>Média histórica</b><br>%{x}: %{y:.2f}°C<extra></extra>",
            )
        )

        for ano in top5_anos:
            if ano == ano_foco:
                continue
            cor = cor_top5.get(ano, "#d35400")
            bloco = gee_anual[gee_anual["ano"] == ano]
            if bloco.empty:
                continue
            fig_gee.add_trace(
                go.Scatter(
                    x=bloco["mes_label"],
                    y=bloco["anomalia_gee"],
                    mode="lines+markers",
                    line=dict(color=cor, width=3.0),
                    marker=dict(size=7),
                    name=f"{ano} (Top El Niño)",
                    hovertemplate=f"<b>{ano}</b><br>%{{x}}: %{{y:.2f}}°C<extra></extra>",
                )
            )

        bloco_foco = gee_anual[gee_anual["ano"] == ano_foco]
        if not bloco_foco.empty:
            bloco_foco = bloco_foco.sort_values("mes_num")
            fig_gee.add_trace(
                go.Scatter(
                    x=bloco_foco["mes_label"],
                    y=bloco_foco["anomalia_gee"],
                    mode="lines+markers",
                    line=dict(color="#000000", width=4.5),
                    marker=dict(size=9, color="#000000"),
                    name=f"{ano_foco} (Destaque)",
                    hovertemplate=f"<b>{ano_foco}</b><br>%{{x}}: %{{y:.2f}}°C<extra></extra>",
                )
            )

            if len(bloco_foco) >= 1:
                x_ini = bloco_foco.iloc[0]["mes_label"]
                y_ini = float(bloco_foco.iloc[0]["anomalia_gee"])
                x_fim = bloco_foco.iloc[-1]["mes_label"]
                y_fim = float(bloco_foco.iloc[-1]["anomalia_gee"])
                mes_fim = int(bloco_foco.iloc[-1]["mes_num"])
                ay_offset = -60

                if len(bloco_foco) >= 2:
                    delta_foco = y_fim - y_ini
                    ay_offset = -60 if delta_foco >= 0 else 60

                    fig_gee.add_shape(
                        type="line",
                        x0=x_ini,
                        y0=y_ini,
                        x1=x_fim,
                        y1=y_fim,
                        line=dict(color="#000000", width=2, dash="dot"),
                    )
                fig_gee.add_annotation(
                    x=x_fim,
                    y=y_fim,
                    text=f"{ano_foco}-{mes_fim:02d}: {y_fim:+.2f}°C",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=1.5,
                    arrowcolor="#000000",
                    ax=-80,
                    ay=ay_offset,
                    font=dict(color="#000000", size=12),
                    bgcolor="rgba(255,255,255,0.85)",
                )

        if not df_picos_oni.empty:
            for _, pico in df_picos_oni.iterrows():
                ano_pico = int(pico["ano"])
                picos_plot = gee_anual[
                    (gee_anual["ano"] == ano_pico)
                    & (gee_anual["mes_num"] == int(pico["mes_num"]))
                ]
                if picos_plot.empty:
                    continue
                cor = cor_top5.get(ano_pico, "#111827")
                fig_gee.add_trace(
                    go.Scatter(
                        x=picos_plot["mes_label"],
                        y=picos_plot["anomalia_gee"],
                        mode="markers+text",
                        text=[str(ano_pico)],
                        textposition="top center",
                        textfont=dict(color=cor, size=11),
                        marker=dict(
                            symbol="diamond",
                            size=11,
                            color=cor,
                            line=dict(color="#ffffff", width=1.2),
                        ),
                        name=f"Pico ONI {ano_pico}",
                        customdata=np.array(
                            [[ano_pico, float(pico["oni_pico"])]], dtype=object
                        ),
                        hovertemplate="<b>Ano %{customdata[0]}</b><br>%{x}: %{y:.2f}°C<br>Pico ONI: %{customdata[1]:.2f}°C<extra></extra>",
                    )
                )

        fig_gee.add_hline(y=0, line=dict(color="#334155", width=1.4))
        fig_gee.update_layout(
            height=460,
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#f8fafc",
            font=dict(color="#000000"),
            xaxis=dict(
                title="Mês",
                categoryorder="array",
                categoryarray=[
                    "Jan",
                    "Fev",
                    "Mar",
                    "Abr",
                    "Mai",
                    "Jun",
                    "Jul",
                    "Ago",
                    "Set",
                    "Out",
                    "Nov",
                    "Dez",
                ],
                gridcolor="#e5e7eb",
                tickfont=dict(color="#000000"),
                title_font=dict(color="#000000"),
            ),
            yaxis=dict(
                title="Anomalia GEE (°C)",
                gridcolor="#e5e7eb",
                tickfont=dict(color="#000000"),
                title_font=dict(color="#000000"),
            ),
            margin=dict(t=20, b=70),
            legend=dict(orientation="h", y=-0.2, font=dict(color="#000000")),
            hovermode="x unified",
        )
else:
    gee_warning_msg = "Módulo GEE indisponível nesta execução."


st.plotly_chart(fig_oni, use_container_width=True)

st.markdown("---")
st.subheader("🔥 Potencial 2026: anomalia mensal por ano")
st.caption(
    "Análise comparativa da anomalia mensal da  temperatura por ano, com destaque para picos de El Niño, com média geral histórica."
)
if fig_gee is not None:
    st.plotly_chart(fig_gee, use_container_width=True)
else:
    st.warning(gee_warning_msg or "Gráfico GEE indisponível nesta execução.")
