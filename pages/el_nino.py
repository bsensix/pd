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
import re

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
        ee.Initialize(project="project-id-placeholder")

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
.metric-card-mini {
    border-radius: 10px;
    padding: 8px 8px;
    min-height: 74px;
    margin: 2px 1px;
}
.metric-card-mini h2 { font-size: 0.9rem; margin: 3px 0; line-height: 1.15; }
.metric-card-mini p  { font-size: 0.68rem; line-height: 1.2; }
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


SOI_MONTH_MAP = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def _parse_soi_html(html_text: str) -> pd.DataFrame:
    if not html_text:
        return pd.DataFrame(columns=["data", "ano", "mes", "soi"])

    month_map = globals().get("SOI_MONTH_MAP") or {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }

    soup = BeautifulSoup(html_text, "html.parser")
    dados = []

    for tabela in soup.find_all("table"):
        linhas = tabela.find_all("tr")
        if len(linhas) < 2:
            continue

        headers = [
            c.get_text(strip=True).lower() for c in linhas[0].find_all(["th", "td"])
        ]
        if not headers:
            continue

        year_idx = None
        month_cols = {}
        for i, h in enumerate(headers):
            h_clean = h[:3].lower()
            if h in {"year", "ano"}:
                year_idx = i
            elif h_clean in month_map:
                month_cols[i] = month_map[h_clean]

        if year_idx is None or not month_cols:
            continue

        for row in linhas[1:]:
            cols = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
            if len(cols) <= year_idx:
                continue
            ano_txt = cols[year_idx].strip()
            if not ano_txt.isdigit():
                continue
            ano = int(ano_txt)

            for col_idx, mes_num in month_cols.items():
                if col_idx >= len(cols):
                    continue
                val_txt = cols[col_idx].replace("−", "-").replace("–", "-").strip()
                if val_txt in {"", "--", "NaN", "nan", "N/A"}:
                    continue
                try:
                    soi_val = float(val_txt)
                except ValueError:
                    continue
                dados.append(
                    {
                        "data": pd.Timestamp(year=ano, month=mes_num, day=1),
                        "ano": ano,
                        "mes": mes_num,
                        "soi": soi_val,
                    }
                )

    if not dados:
        return pd.DataFrame(columns=["data", "ano", "mes", "soi"])

    df = pd.DataFrame(dados).sort_values("data").reset_index(drop=True)
    df["soi"] = pd.to_numeric(df["soi"], errors="coerce")
    df = df.dropna(subset=["soi"]).reset_index(drop=True)
    return df[["data", "ano", "mes", "soi"]]


def _parse_soi_chart_config(config_text: str) -> pd.DataFrame:
    if not config_text:
        return pd.DataFrame(columns=["data", "ano", "mes", "soi"])

    i_scale = config_text.find('"scaleX"')
    i_scroll = config_text.find('"scrollX"', i_scale if i_scale >= 0 else 0)
    scale_x_txt = (
        config_text[i_scale:i_scroll]
        if i_scale >= 0 and i_scroll > i_scale
        else config_text
    )

    labels_match = re.search(r'"labels"\s*:\s*\[(.*?)\]', scale_x_txt, re.S)
    values_match = re.search(
        r'"values"\s*:\s*\[(.*?)\]\s*,\s*"guideLabel"', config_text, re.S
    )
    if labels_match is None or values_match is None:
        return pd.DataFrame(columns=["data", "ano", "mes", "soi"])

    labels = re.findall(r'"([A-Za-z]{3}\s+\d{4})"', labels_match.group(1))
    values = [v.strip() for v in values_match.group(1).split(",")]
    n = min(len(labels), len(values))
    if n == 0:
        return pd.DataFrame(columns=["data", "ano", "mes", "soi"])

    dados = []
    for i in range(n):
        lbl = labels[i]
        val_txt = values[i].replace("−", "-").replace("–", "-").strip()
        if val_txt in {"", "null", "None", "nan", "NaN"}:
            continue
        try:
            dt = pd.to_datetime(lbl, format="%b %Y")
            soi_val = float(val_txt)
        except Exception:
            continue
        dados.append(
            {"data": dt, "ano": int(dt.year), "mes": int(dt.month), "soi": soi_val}
        )

    if not dados:
        return pd.DataFrame(columns=["data", "ano", "mes", "soi"])

    return pd.DataFrame(dados).sort_values("data").reset_index(drop=True)


def carregar_soi_de_html(html_text: str) -> pd.DataFrame:
    return _parse_soi_html(html_text)


@st.cache_data(ttl=3600)
def carregar_soi() -> pd.DataFrame:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        # Fonte NOAA/NCEI solicitada (rota da secao SOI)
        url_cfg = "https://www.ncei.noaa.gov/access/monitoring/enso/soi/zingchart-config.js?chartId=soiTs"
        resp_cfg = requests.get(url_cfg, headers=headers, timeout=20)
        resp_cfg.raise_for_status()
        df_cfg = _parse_soi_chart_config(resp_cfg.text)
        if not df_cfg.empty:
            return df_cfg

        url_page = "https://www.ncei.noaa.gov/access/monitoring/enso/soi"
        resp_page = requests.get(url_page, headers=headers, timeout=20)
        resp_page.raise_for_status()
        return carregar_soi_de_html(resp_page.text)
    except Exception:
        return pd.DataFrame(columns=["data", "ano", "mes", "soi"])


def metricas_soi_historicas(df_soi: pd.DataFrame) -> dict:
    base = {
        "ultimo_soi": np.nan,
        "media": np.nan,
        "desvio": np.nan,
        "percentil": np.nan,
        "zscore": np.nan,
        "ultima_data": "sem dado",
        "n": 0,
    }
    if df_soi.empty:
        return base

    d = df_soi.copy()
    d["soi"] = pd.to_numeric(d["soi"], errors="coerce")
    d = d.dropna(subset=["soi"]).sort_values("data").reset_index(drop=True)
    if d.empty:
        return base

    x = float(d.iloc[-1]["soi"])
    hist = d["soi"].astype(float)
    media = float(hist.mean())
    desvio = float(hist.std(ddof=1)) if len(hist) > 1 else np.nan

    h_sorted = hist.sort_values().reset_index(drop=True)
    eq = h_sorted[h_sorted == x]
    if len(eq) > 0:
        i0 = eq.index.min() + 1
        i1 = eq.index.max() + 1
        percentil = float(((i0 + i1) / 2.0) / len(h_sorted) * 100.0)
    else:
        percentil = float((h_sorted < x).sum() / len(h_sorted) * 100.0)

    if pd.notna(desvio) and desvio != 0:
        zscore = float((x - media) / desvio)
    elif pd.notna(desvio) and desvio == 0:
        zscore = 0.0
    else:
        zscore = np.nan

    return {
        "ultimo_soi": x,
        "media": media,
        "desvio": desvio,
        "percentil": percentil,
        "zscore": zscore,
        "ultima_data": d.iloc[-1]["data"].strftime("%Y-%m"),
        "n": int(len(d)),
    }


def build_soi_summary_text(metricas: dict) -> str:
    ultimo = metricas.get("ultimo_soi", np.nan)
    percentil = metricas.get("percentil", np.nan)
    zscore = metricas.get("zscore", np.nan)
    ultima_data = metricas.get("ultima_data", "sem dado")

    if pd.isna(ultimo):
        return "Sem dados suficientes de SOI para leitura historica."

    if ultimo < 0:
        fase_txt = "SOI negativo favorece fase quente (El Nino)"
    elif ultimo > 0:
        fase_txt = "SOI positivo favorece fase fria (La Nina)"
    else:
        fase_txt = "SOI neutro, sem viés forte de fase"

    p_txt = (
        f"percentil {percentil:.1f}"
        if pd.notna(percentil)
        else "percentil indisponivel"
    )
    z_txt = f"z-score {zscore:+.2f}" if pd.notna(zscore) else "z-score indisponivel"
    return (
        f"Leitura SOI ({ultima_data}): {ultimo:+.2f}. "
        f"Historico: {p_txt}, {z_txt}. {fase_txt}."
    )


def decidir_render_soi(df_soi: pd.DataFrame) -> dict:
    if df_soi.empty:
        return {"renderizar": False, "motivo": "serie vazia"}
    if "soi" not in df_soi.columns:
        return {"renderizar": False, "motivo": "coluna soi ausente"}
    n_validos = int(pd.to_numeric(df_soi["soi"], errors="coerce").notna().sum())
    return {
        "renderizar": n_validos > 0,
        "motivo": "ok" if n_validos > 0 else "sem valores validos",
    }


def build_soi_visual_context(df_soi: pd.DataFrame, metricas: dict) -> dict:
    decisao = decidir_render_soi(df_soi)
    return {
        "mostrar_warning": not decisao["renderizar"],
        "mensagem_warning": f"SOI indisponivel: {decisao['motivo']}.",
        "resumo": build_soi_summary_text(metricas) if decisao["renderizar"] else "",
    }


def build_indicadores_recentes(
    df_oni: pd.DataFrame,
    df_soi: pd.DataFrame,
    df_gee_extremos: pd.DataFrame,
    gee_ok: bool,
) -> dict:
    def classe_por_valor(v: float) -> str:
        if pd.isna(v):
            return "neutro"
        if v >= 0.5:
            return "elnino"
        if v <= -0.5:
            return "lanina"
        return "neutro"

    ultimo_oni = df_oni.iloc[-1]
    oni_val = float(ultimo_oni["oni"])
    if oni_val >= 0.5:
        oni_fase = "El Niño"
    elif oni_val <= -0.5:
        oni_fase = "La Niña"
    else:
        oni_fase = "Neutro"
    oni = {
        "titulo": f"Último ONI ({ultimo_oni['periodo']})",
        "valor": f"{oni_val:+.2f}°C",
        "sub": oni_fase,
        "classe": classe_por_valor(oni_val),
    }

    if df_soi.empty:
        soi = {
            "titulo": "Último SOI",
            "valor": "sem dado",
            "sub": "série indisponível",
            "classe": "neutro",
        }
    else:
        soi_valid = (
            df_soi.dropna(subset=["soi"]).sort_values("data").reset_index(drop=True)
        )
        if soi_valid.empty:
            soi = {
                "titulo": "Último SOI",
                "valor": "sem dado",
                "sub": "série indisponível",
                "classe": "neutro",
            }
        else:
            s = soi_valid.iloc[-1]
            s_val = float(s["soi"])
            s_data = s["data"].strftime("%Y-%m")
            soi = {
                "titulo": f"Último SOI ({s_data})",
                "valor": f"{s_val:+.2f}",
                "sub": "favorece El Niño"
                if s_val < 0
                else "favorece La Niña"
                if s_val > 0
                else "neutro",
                "classe": "elnino"
                if s_val < 0
                else "lanina"
                if s_val > 0
                else "neutro",
            }

    if (
        gee_ok
        and not df_gee_extremos.empty
        and "anomalia_gee" in df_gee_extremos.columns
    ):
        gee_valid = (
            df_gee_extremos.dropna(subset=["anomalia_gee"])
            .sort_values("data")
            .reset_index(drop=True)
        )
    else:
        gee_valid = pd.DataFrame()

    if gee_valid.empty:
        anomalia = {
            "titulo": "Última Anomalia de Temperatura",
            "valor": "sem dado",
            "sub": "NOAA CDR OISST",
            "classe": "neutro",
        }
    else:
        g = gee_valid.iloc[-1]
        g_val = float(g["anomalia_gee"])
        g_data = g["data"].strftime("%Y-%m")
        anomalia = {
            "titulo": f"Última Anomalia ({g_data})",
            "valor": f"{g_val:+.2f}°C",
            "sub": "NOAA CDR OISST",
            "classe": "elnino" if g_val > 0 else "lanina" if g_val < 0 else "neutro",
        }

    return {"oni": oni, "soi": soi, "anomalia": anomalia}


def build_resumo_analise_texto(
    ultimo_gee_txt: str, leitura_oni: str, indicadores_recentes: dict
) -> str:
    soi_info = indicadores_recentes.get("soi", {})
    soi_val = soi_info.get("valor", "sem dado")
    soi_sub = soi_info.get("sub", "série indisponível")
    return f"Anomalia °C: {ultimo_gee_txt} · {leitura_oni} · SOI: {soi_val} ({soi_sub})"


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

    # --- Garantir que sst_gee é float, aplicar escala correta (0.01) e tratar valores inválidos ---
    df_gee["sst_gee"] = pd.to_numeric(df_gee["sst_gee"], errors="coerce") * 0.01

    # --- Climatologia: média de TODO o histórico disponível ---
    clima = df_gee.groupby(df_gee["data"].dt.month)["sst_gee"].mean()

    # --- Checagem: climatologia não pode ter NaN ---
    if clima.isnull().any():
        st.warning(
            "Climatologia contém valores NaN para alguns meses. Verifique os dados históricos."
        )

    # --- Cálculo robusto da anomalia, evitando valores absurdos ---
    def calc_anomalia(row):
        clim = clima.get(row["data"].month, np.nan)
        if pd.notna(clim) and pd.notna(row["sst_gee"]):
            return row["sst_gee"] - clim
        return np.nan

    df_gee["anomalia_gee"] = df_gee.apply(calc_anomalia, axis=1)
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
As discussões ganharam força porque os principais modelos meteorológicos detectaram um <b>aquecimento rápido e incomum</b> das águas superficiais do Oceano Pacífico Equatorial.<br>

<i>Nesta análise, comparamos os dados atuais com os maiores eventos extremos do passado (segundo o ONI da NOAA, a série histórica do NOAA CDR OISST e o SOI) para entender o que fundamenta essa expectativa.</i>

""",
    unsafe_allow_html=True,
)

with st.spinner("Carregando dados históricos do NOAA…"):
    df = carregar_oni()

if df.empty:
    st.stop()

with st.spinner("Carregando série histórica do SOI…"):
    df_soi = carregar_soi()


# ── Sem filtros: análise automática dos eventos extremos ─────────────────────
col_oni, col_oisst, col_soi = st.columns(3)

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

with col_soi:
    st.markdown("**O que é o SOI?**")
    st.info(
        "O Southern Oscillation Index (SOI) mede a diferença padronizada de pressão "
        "ao nível do mar entre Taiti e Darwin, Austrália. Valores negativos tendem a favorecer "
        "El Niño, enquanto valores positivos tendem a favorecer La Niña."
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
indicadores_recentes = build_indicadores_recentes(
    df_filt, df_soi, df_gee_extremos, GEE_OK
)

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

resumo_analise = build_resumo_analise_texto(
    ultimo_gee_txt, leitura_oni, indicadores_recentes
)

col_mapa, col_cards = st.columns([2, 3])

with col_cards:
    r1c1, r1c2, r1c3 = st.columns(3)
    with r1c1:
        oni_card = indicadores_recentes["oni"]
        st.markdown(
            f"""
        <div class="metric-card {oni_card["classe"]}">
            <p>{oni_card["titulo"]}</p>
            <h2>{oni_card["valor"]}</h2>
            <p>{oni_card["sub"]}</p>
        </div>""",
            unsafe_allow_html=True,
        )
    with r1c2:
        soi_card = indicadores_recentes["soi"]
        st.markdown(
            f"""
        <div class="metric-card {soi_card["classe"]}">
            <p>{soi_card["titulo"]}</p>
            <h2>{soi_card["valor"]}</h2>
            <p>{soi_card["sub"]}</p>
        </div>""",
            unsafe_allow_html=True,
        )
    with r1c3:
        anom_card = indicadores_recentes["anomalia"]
        st.markdown(
            f"""
        <div class="metric-card {anom_card["classe"]}">
            <p>{anom_card["titulo"]}</p>
            <h2>{anom_card["valor"]}</h2>
            <p>{anom_card["sub"]}</p>
        </div>""",
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #1f4b7a, #2f6f9d); min-height: 150px; padding: 22px 24px; margin-top: 12px;">
        <p>O que os dados dizem ?</p>
        <h2 style="font-size:1.55rem; line-height:1.35; margin: 10px 0 12px 0;">Há aquecimento no mar, mas sem confirmação El Niño</h2>
        <p>{resumo_analise}</p>
        <p style="margin-top:8px; opacity:0.95;">El Niño não depende apenas da temperatura do mar: também envolve mudanças nos ventos alísios e na pressão atmosférica (Oscilação Sul).</p>
        <p style="margin-top:8px; opacity:0.95;">Analise os dados abaixo para entender melhor o fenômeno.</p>
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

st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
r2c1, r2c2, r2c3, r2c4 = st.columns(4)
with r2c1:
    st.markdown(
        f"""
    <div class="metric-card metric-card-mini elnino">
        <p>ONI Máximo Histórico</p>
        <h2>{oni_max:+.2f}°C</h2>
        <p>{df_filt.loc[df_filt["oni"].idxmax(), "periodo"]}</p>
    </div>""",
        unsafe_allow_html=True,
    )
with r2c2:
    st.markdown(
        f"""
    <div class="metric-card metric-card-mini elnino">
        <p>Trimestres El Niño</p>
        <h2>{len(elninos)}</h2>
        <p>{len(elninos) / len(df_filt) * 100:.1f}% do período</p>
    </div>""",
        unsafe_allow_html=True,
    )
with r2c3:
    st.markdown(
        f"""
    <div class="metric-card metric-card-mini lanina">
        <p>Trimestres La Niña</p>
        <h2>{len(laninas)}</h2>
        <p>{len(laninas) / len(df_filt) * 100:.1f}% do período</p>
    </div>""",
        unsafe_allow_html=True,
    )
with r2c4:
    st.markdown(
        f"""
    <div class="metric-card metric-card-mini neutro">
        <p>Trimestres Neutros</p>
        <h2>{len(neutros)}</h2>
        <p>{len(neutros) / len(df_filt) * 100:.1f}% do período</p>
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

fig_gee = None
gee_warning_msg = None

# --- Gráfico de valores originais de SST por mês, com climatologia ---
fig_sst = None
df_clima = None

if GEE_OK and not df_gee_extremos.empty:
    # Cálculo da climatologia (já garantido no carregamento, mas recalculado para exibir)
    df_gee_extremos["sst_gee"] = pd.to_numeric(
        df_gee_extremos["sst_gee"], errors="coerce"
    )
    clima = df_gee_extremos.groupby(df_gee_extremos["data"].dt.month)["sst_gee"].mean()
    # DataFrame da climatologia para exibição
    df_clima = pd.DataFrame({"Mês": clima.index, "Climatologia_SST": clima.values})
    # Adiciona coluna de mês para plot
    df_gee_extremos["mes_num"] = df_gee_extremos["data"].dt.month
    df_gee_extremos["ano"] = df_gee_extremos["data"].dt.year
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
    df_gee_extremos["mes_label"] = df_gee_extremos["mes_num"].map(mes_labels)
    # Gráfico
    fig_sst = go.Figure()
    # Linhas de cada ano
    max_ano = int(df_gee_extremos["ano"].max())
    for ano, bloco in df_gee_extremos.groupby("ano"):
        show_leg = bool(ano == max_ano)
        fig_sst.add_trace(
            go.Scatter(
                x=bloco["mes_label"],
                y=bloco["sst_gee"],
                mode="lines+markers",
                name=str(ano),
                line=dict(width=1.2),
                marker=dict(size=4),
                opacity=0.25 if ano != max_ano else 1.0,
                showlegend=show_leg,
                hovertemplate=f"<b>{ano}</b><br>%{{x}}: %{{y:.2f}}°C<extra></extra>",
            )
        )
    # Linha da climatologia
    fig_sst.add_trace(
        go.Scatter(
            x=[mes_labels[m] for m in clima.index],
            y=clima.values,
            mode="lines+markers",
            name="Climatologia",
            line=dict(color="#e67e22", width=3, dash="dash"),
            marker=dict(size=7, color="#e67e22"),
            hovertemplate="<b>Climatologia</b><br>%{x}: %{y:.2f}°C<extra></extra>",
        )
    )
    fig_sst.update_layout(
        title="SST Original por Mês (com Climatologia)",
        height=420,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#f8fafc",
        font=dict(color="#000000"),
        xaxis=dict(
            title="Mês",
            categoryorder="array",
            categoryarray=[mes_labels[m] for m in range(1, 13)],
            gridcolor="#e5e7eb",
            tickfont=dict(color="#000000"),
            title_font=dict(color="#000000"),
        ),
        yaxis=dict(
            title="SST (°C)",
            gridcolor="#e5e7eb",
            tickfont=dict(color="#000000"),
            title_font=dict(color="#000000"),
        ),
        margin=dict(t=20, b=70),
        legend=dict(orientation="h", y=-0.2, font=dict(color="#000000")),
        hovermode="x unified",
    )
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

## Removido gráfico de SST mensal original e dataframe de climatologia conforme solicitado
st.subheader("🔥Anomalias Mensais Temperatura")
st.caption(
    "Análise comparativa da anomalia mensal da  temperatura por ano, com destaque para picos de El Niño, com média geral histórica."
)
if fig_gee is not None:
    st.plotly_chart(fig_gee, use_container_width=True)
else:
    st.warning(gee_warning_msg or "Gráfico GEE indisponível nesta execução.")

st.markdown("---")
st.subheader("📉 Índice de Oscilação Sul (SOI) — Série Histórica")
st.caption("Fonte: NOAA/NCEI ENSO · SOI mensal")

soi_metricas = metricas_soi_historicas(df_soi)
soi_ctx = build_soi_visual_context(df_soi, soi_metricas)

if soi_ctx["mostrar_warning"]:
    st.warning(soi_ctx["mensagem_warning"])
else:
    df_soi_plot = df_soi.copy().sort_values("data").reset_index(drop=True)
    x_vals = df_soi_plot["data"].tolist()
    y_vals = pd.to_numeric(df_soi_plot["soi"], errors="coerce").tolist()

    x_pos, y_pos, x_neg, y_neg = [], [], [], []

    def _add_seg(xs, ys, xa, ya, xb, yb):
        xs.extend([xa, xb, None])
        ys.extend([ya, yb, None])

    for i in range(len(y_vals) - 1):
        y0, y1 = y_vals[i], y_vals[i + 1]
        x0, x1 = x_vals[i], x_vals[i + 1]

        if pd.isna(y0) or pd.isna(y1):
            continue

        if y0 >= 0 and y1 >= 0:
            _add_seg(x_pos, y_pos, x0, y0, x1, y1)
        elif y0 <= 0 and y1 <= 0:
            _add_seg(x_neg, y_neg, x0, y0, x1, y1)
        else:
            den = abs(y0) + abs(y1)
            frac = abs(y0) / den if den != 0 else 0.5
            x_cross = x0 + (x1 - x0) * frac

            if y0 > 0:
                _add_seg(x_pos, y_pos, x0, y0, x_cross, 0.0)
                _add_seg(x_neg, y_neg, x_cross, 0.0, x1, y1)
            else:
                _add_seg(x_neg, y_neg, x0, y0, x_cross, 0.0)
                _add_seg(x_pos, y_pos, x_cross, 0.0, x1, y1)

    fig_soi = go.Figure()
    fig_soi.add_trace(
        go.Scatter(
            x=x_pos,
            y=y_pos,
            mode="lines",
            line=dict(color="#1f77b4", width=1.8),
            name="SOI positivo",
            hovertemplate="<b>%{x|%Y-%m}</b><br>SOI: %{y:.2f}<extra></extra>",
        )
    )
    fig_soi.add_trace(
        go.Scatter(
            x=x_neg,
            y=y_neg,
            mode="lines",
            line=dict(color="#d62728", width=1.8),
            name="SOI negativo",
            hovertemplate="<b>%{x|%Y-%m}</b><br>SOI: %{y:.2f}<extra></extra>",
        )
    )
    fig_soi.add_hline(y=0, line=dict(color="#7f8c8d", width=1.1, dash="dash"))
    fig_soi.update_layout(
        height=360,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#f9f9f9",
        margin=dict(t=20, b=60),
        xaxis=dict(
            title="Período",
            gridcolor="#e0e0e0",
            tickfont=dict(color="#000000"),
            title_font=dict(color="#000000"),
            linecolor="#000000",
        ),
        yaxis=dict(
            title="SOI",
            gridcolor="#e0e0e0",
            tickfont=dict(color="#000000"),
            title_font=dict(color="#000000"),
            linecolor="#000000",
        ),
        hovermode="x unified",
        legend=dict(font=dict(color="#000000")),
    )
    st.plotly_chart(fig_soi, use_container_width=True)

    st.caption(
        "Interpretação ENSO: SOI negativo tende a favorecer fase quente (El Niño) e SOI positivo tende a favorecer fase fria (La Niña)."
    )

st.markdown("---")
st.subheader("📚 Referências")

referencias = [
    (
        "NOAA/CPC — Oceanic Niño Index (ONI)",
        "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php",
    ),
    (
        "NOAA/NCEI — ENSO Southern Oscillation Index (SOI)",
        "https://www.ncei.noaa.gov/access/monitoring/enso/soi",
    ),
    (
        "Google Earth Engine — NOAA/CDR/OISST/V2_1",
        "https://developers.google.com/earth-engine/datasets/catalog/NOAA_CDR_OISST_V2_1",
    ),
    (
        "Palestra professor Luis Carlos Molion sobre ENSO",
        "https://www.youtube.com/watch?v=lqgKil7VuU4",
    ),
]

for nome, link in referencias:
    st.markdown(f"- [{nome}]({link})")
