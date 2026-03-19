import calendar
import time
from datetime import date, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import yfinance as yf

from core.ui import COMO_FUNCIONA_ICON, CONTATO_ICON, GLOSSARIO_ICON

REQUESTS_CACHE_AVAILABLE = False
try:
    import requests_cache  # type: ignore
    REQUESTS_CACHE_AVAILABLE = True
except Exception:
    requests_cache = None
    REQUESTS_CACHE_AVAILABLE = False

_BCB_SESSION = requests.Session()


def _set_bcb_session(use_cache: bool) -> None:
    global _BCB_SESSION
    if use_cache and REQUESTS_CACHE_AVAILABLE:
        try:
            _BCB_SESSION = requests_cache.CachedSession(
                cache_name="bcb_sgs_cache",
                backend="sqlite",
                expire_after=timedelta(hours=12),
                stale_if_error=True,
            )
            return
        except Exception:
            _BCB_SESSION = requests.Session()
    else:
        _BCB_SESSION = requests.Session()


if REQUESTS_CACHE_AVAILABLE:
    _set_bcb_session(bool(st.session_state.get("usar_cache_local", True)))
else:
    _set_bcb_session(False)

st.markdown(
    """
<style>
[data-testid="stSidebarCollapsedControl"] {
    display: none !important;
}

.page-title{
    font-size: 2.2rem;
    font-weight: 900;
    color: #0f172a;
    margin: 0 0 0.25rem 0;
    line-height: 1.1;
    letter-spacing: -0.02em;
}
.module-subtitle{
    font-size: 1rem;
    color: #475569;
    margin-bottom: 0.4rem;
    line-height: 1.65;
}
.helper-text{
    font-size: 0.95rem;
    color: #64748b;
    margin-bottom: 1.3rem;
    line-height: 1.55;
}
.section-title{
    font-size: 1.4rem;
    font-weight: 900;
    color: #0f172a;
    margin: 22px 0 6px 0;
    letter-spacing: -0.01em;
}
.placeholder-box{
    background: #f8fafc;
    border: 1px dashed #cbd5e1;
    border-radius: 14px;
    padding: 28px 20px;
    text-align: center;
}
.placeholder-box .ttl{
    font-size: 1rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 6px;
}
.placeholder-box .txt{
    font-size: 0.95rem;
    color: #64748b;
    line-height: 1.6;
}

.total-card {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 15px;
    border-radius: 12px 12px 0 0;
    text-align: center;
}
.total-label { font-size: 0.75rem; font-weight: 800; color: #64748b; text-transform: uppercase; margin-bottom: 5px; }
.total-sub-label { font-size: 0.72rem; font-weight: 700; color: #475569; margin-top: 2px; margin-bottom: 4px; }
.total-amount { font-size: 1.6rem; font-weight: 800; color: #1f77b4; }

.badge-dinamico {
    display:inline-block;
    font-size:0.70rem;
    font-weight: 900;
    color:#0369a1;
    background:#e0f2fe;
    border:1px solid #7dd3fc;
    padding: 3px 8px;
    border-radius: 999px;
    margin: 0 auto 8px auto;
}
.badge-fixo {
    display:inline-block;
    font-size:0.70rem;
    font-weight: 900;
    color:#475569;
    background:#f1f5f9;
    border:1px solid #e2e8f0;
    padding: 3px 8px;
    border-radius: 999px;
    margin: 0 auto 8px auto;
}

.info-card { background-color: #ffffff; border: 1px solid #e2e8f0; border-top: none; padding: 18px; border-radius: 0 0 12px 12px; margin-bottom: 15px; }
.card-header { font-size: 0.75rem; font-weight: 800; color: #64748b; text-transform: uppercase; margin-bottom: 10px; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; }
.card-item { font-size: 0.9rem; margin-bottom: 6px; color: #1e293b; }

.sub-note{
    font-size: 0.78rem;
    color: #475569;
    margin: 2px 0 2px 0;
    line-height: 1.25;
}
.sub-note .v{
    color: #475569;
    font-weight: 600;
}

.warn-box {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    border-left: 5px solid #fb923c;
    padding: 12px 14px;
    border-radius: 10px;
    color: #7c2d12;
    margin: 10px 0 0 0;
    font-size: 0.9rem;
    line-height: 1.5;
}

.ticker-status {
    font-size: 0.82rem;
    padding: 10px 12px;
    border-radius: 12px;
    border: 1px solid;
    line-height: 1.35;
    color: #0f172a;
}
.ticker-ok { background: #dcfce7; border-color: #86efac; }
.ticker-bad { background: #fee2e2; border-color: #fca5a5; }
.ticker-neutral { background: #f8fafc; border-color: #e2e8f0; color: #475569; }
</style>
""",
    unsafe_allow_html=True,
)


def formata_br(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formata_int_br(n: int) -> str:
    return f"{int(n):,}".replace(",", ".")


DIAS_MES = 30
DIAS_ANO = 365
MIN_DATA_BANCO = date(1990, 1, 1)

COR_CDI = "#14532d"
COR_IPCA = "red"
COR_IBOV = "orange"


def decompor_periodo_anos_meses_dias(dt_ini: pd.Timestamp, dt_fim: pd.Timestamp) -> tuple[int, int, int]:
    dt_ini = pd.to_datetime(dt_ini).normalize()
    dt_fim = pd.to_datetime(dt_fim).normalize()
    total_days = int((dt_fim - dt_ini).days)
    if total_days < 0:
        total_days = 0
    anos = total_days // DIAS_ANO
    rem = total_days % DIAS_ANO
    meses = rem // DIAS_MES
    dias = rem % DIAS_MES
    return int(anos), int(meses), int(dias)


def formatar_meses_dias(meses: int, dias: int) -> str:
    m_txt = "mês" if meses == 1 else "meses"
    d_txt = "dia" if dias == 1 else "dias"
    return f"{meses} {m_txt} e {dias} {d_txt}"


def titulo_periodo_dinamico(anos: int, meses: int, dias: int) -> tuple[str, str | None]:
    if anos >= 1:
        titulo = "Total em 1 ano" if anos == 1 else f"Total em {anos} anos"
        sub = formatar_meses_dias(meses, dias)
        return titulo, sub
    if meses >= 1:
        titulo = "Total em 1 mês" if meses == 1 else f"Total em {meses} meses"
        sub = f"{dias} {'dia' if dias == 1 else 'dias'}"
        return titulo, sub
    titulo = "Total em 1 dia" if dias == 1 else f"Total em {dias} dias"
    return titulo, None


def _fetch_bcb_json(codigo: int, d_inicio: date, d_fim: date, timeout: int = 30) -> pd.DataFrame:
    s, e = d_inicio.strftime("%d/%m/%Y"), d_fim.strftime("%d/%m/%Y")
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
    params = {"formato": "json", "dataInicial": s, "dataFinal": e}
    headers = {"User-Agent": "Mozilla/5.0"}

    r = _BCB_SESSION.get(url, params=params, headers=headers, timeout=timeout)
    if r.status_code != 200:
        raise RuntimeError(f"BCB/SGS HTTP {r.status_code}")

    df = pd.DataFrame(r.json())
    if df.empty:
        return pd.DataFrame(columns=["data", "valor"])
    return df


@st.cache_data(ttl=60 * 60 * 6, show_spinner=False)
def busca_indice_bcb(codigo: int, d_inicio: date, d_fim: date) -> pd.Series:
    if d_inicio is None or d_fim is None or d_inicio > d_fim:
        return pd.Series(dtype="float64")

    start = pd.Timestamp(d_inicio)
    end = pd.Timestamp(d_fim)

    partes = []
    cur = start
    while cur <= end:
        chunk_end = min(end, (cur + pd.DateOffset(years=10)) - pd.Timedelta(days=1))
        d1 = cur.date()
        d2 = chunk_end.date()

        ok = False
        for i in range(5):
            try:
                df = _fetch_bcb_json(codigo, d1, d2, timeout=30)
                if not df.empty:
                    partes.append(df)
                ok = True
                break
            except Exception:
                time.sleep(i + 1)

        if not ok:
            return pd.Series(dtype="float64")
        cur = chunk_end + pd.Timedelta(days=1)

    if not partes:
        return pd.Series(dtype="float64")

    df_all = pd.concat(partes, ignore_index=True)
    if df_all.empty:
        return pd.Series(dtype="float64")

    df_all["data"] = pd.to_datetime(df_all["data"], dayfirst=True, errors="coerce")
    df_all["valor"] = df_all["valor"].astype(str).str.replace(",", ".", regex=False)
    df_all["valor"] = pd.to_numeric(df_all["valor"], errors="coerce") / 100.0

    df_all = df_all.dropna(subset=["data", "valor"]).set_index("data").sort_index()
    if df_all.empty:
        return pd.Series(dtype="float64")

    s = df_all["valor"].astype(float)
    s = s[~s.index.duplicated(keep="last")]
    return (1.0 + s).cumprod()


def _inicio_buffer_ipca(d_inicio: date) -> date:
    ts = pd.Timestamp(d_inicio).normalize()
    ts = ts.replace(day=1) - pd.DateOffset(months=2)
    return ts.date()


def _inicio_buffer_rf(d_inicio: date) -> date:
    ts = pd.Timestamp(d_inicio).normalize() - pd.Timedelta(days=35)
    return ts.date()


@st.cache_data(ttl=60 * 60 * 6, show_spinner=False)
def carregar_renda_fixa(d_inicio: date, d_fim: date) -> tuple[pd.Series, str]:
    d0 = _inicio_buffer_rf(d_inicio)
    s_cdi = busca_indice_bcb(12, d0, d_fim)
    if s_cdi is not None and not s_cdi.empty:
        return s_cdi, "CDI"

    s_selic = busca_indice_bcb(11, d0, d_fim)
    if s_selic is not None and not s_selic.empty:
        return s_selic, "Selic (proxy CDI)"

    return pd.Series(dtype="float64"), "Renda Fixa"


@st.cache_data(ttl=60 * 60 * 6, show_spinner=False)
def carregar_ipca(d_inicio: date, d_fim: date) -> pd.Series:
    d0 = _inicio_buffer_ipca(d_inicio)
    return busca_indice_bcb(433, d0, d_fim)


def projetar_indice_ate_fim(
    s: pd.Series,
    dt_fim: date,
    prefer_meses: tuple[int, int] = (6, 3),
    dias_mes: int = 30,
) -> pd.Series:
    if s is None or s.empty:
        return s

    s = pd.Series(s).dropna().sort_index()
    if s.empty:
        return s

    dt_fim_ts = pd.Timestamp(dt_fim).normalize()
    if getattr(s.index, "tz", None) is not None:
        dt_fim_ts = dt_fim_ts.tz_localize(s.index.tz)

    ultima_data = s.index[-1]
    if ultima_data >= dt_fim_ts:
        return s

    last_val = float(s.iloc[-1])
    chosen_daily_rate = None

    for m in prefer_meses:
        lookback_days = int(m * dias_mes)
        cutoff = ultima_data - pd.Timedelta(days=lookback_days)

        pos = s.index.get_indexer([cutoff], method="ffill")[0]
        if pos == -1:
            continue

        data_passada = s.index[pos]
        val_passado = float(s.iloc[pos])
        dias_decorridos = int((ultima_data - data_passada).days)

        if dias_decorridos >= 10 and val_passado > 0 and last_val > 0:
            chosen_daily_rate = (last_val / val_passado) ** (1 / dias_decorridos) - 1
            break

    if chosen_daily_rate is None:
        data_passada = s.index[0]
        val_passado = float(s.iloc[0])
        dias_decorridos = int((ultima_data - data_passada).days)
        if dias_decorridos <= 0 or val_passado <= 0 or last_val <= 0:
            return s
        chosen_daily_rate = (last_val / val_passado) ** (1 / dias_decorridos) - 1

    datas_faltantes = pd.date_range(start=ultima_data + pd.Timedelta(days=1), end=dt_fim_ts, freq="D")
    if len(datas_faltantes) == 0:
        return s

    vals = []
    v = last_val
    for _ in datas_faltantes:
        v *= (1 + chosen_daily_rate)
        vals.append(v)

    s_proj = pd.Series(vals, index=datas_faltantes)
    return pd.concat([s, s_proj])


def _split_efetivo_para_evitar_degrau(df: pd.DataFrame) -> pd.Series:
    close = df["Close"].astype(float)
    prev = close.shift(1)

    split_raw = df.get("Stock Splits", pd.Series(0.0, index=df.index)).fillna(0.0).astype(float)
    split_raw = split_raw.replace(0.0, 1.0)

    actual = close / prev
    expected_unadj = 1.0 / split_raw

    mask = (split_raw != 1.0) & (prev > 0) & (close > 0) & (expected_unadj > 0)

    eff = pd.Series(1.0, index=df.index, dtype=float)
    if mask.any():
        diff_unadj = (np.log(actual[mask]) - np.log(expected_unadj[mask])).abs()
        diff_adj = (np.log(actual[mask]) - np.log(1.0)).abs()
        eff.loc[mask] = np.where(diff_unadj < diff_adj, split_raw[mask], 1.0)

    return eff


@st.cache_data(ttl=60 * 30, show_spinner=False)
def carregar_dados_completos(t: str, d_inicio: date, d_fim: date) -> pd.DataFrame | None:
    if not t:
        return None
    t_sa = t if ".SA" in t else t + ".SA"

    start = (pd.Timestamp(d_inicio).normalize() - pd.Timedelta(days=10)).date()
    end = (pd.Timestamp(d_fim).normalize() + pd.Timedelta(days=2)).date()

    try:
        df = yf.download(
            t_sa,
            start=start,
            end=end,
            progress=False,
            auto_adjust=False,
            actions=True,
            interval="1d",
            threads=False,
        )
        if df is None or df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if getattr(df.index, "tz", None) is not None:
            df.index = df.index.tz_localize(None)

        for col in ["Close", "Dividends", "Stock Splits"]:
            if col not in df.columns:
                df[col] = 0.0

        df = df[["Close", "Dividends", "Stock Splits"]].copy()
        df = df.dropna(subset=["Close"]).sort_index()
        df["Dividends"] = df["Dividends"].fillna(0.0).astype(float)
        df["Stock Splits"] = df["Stock Splits"].fillna(0.0).astype(float)

        split_eff = _split_efetivo_para_evitar_degrau(df)
        df["Split_Eff"] = split_eff.fillna(1.0).astype(float)

        close = df["Close"].astype(float)
        prev_close = close.shift(1)

        price_factor = (close * df["Split_Eff"]) / prev_close
        total_factor = ((close + df["Dividends"]) * df["Split_Eff"]) / prev_close

        df["Price_Fact"] = price_factor.replace([np.inf, -np.inf], np.nan).fillna(1.0).cumprod()
        df["Total_Fact"] = total_factor.replace([np.inf, -np.inf], np.nan).fillna(1.0).cumprod()
        return df
    except Exception:
        return None


@st.cache_data(ttl=60 * 30, show_spinner=False)
def carregar_ibov(d_inicio: date, d_fim: date) -> pd.Series:
    start = max(pd.Timestamp(d_inicio).normalize() - pd.Timedelta(days=90), pd.Timestamp(MIN_DATA_BANCO))
    end = (pd.Timestamp(d_fim).normalize() + pd.Timedelta(days=2)).date()

    for i in range(3):
        try:
            df = yf.download(
                "^BVSP",
                start=start.date(),
                end=end,
                progress=False,
                auto_adjust=False,
                threads=False,
            )
            if df is None or df.empty:
                time.sleep(i + 1)
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            s = df["Close"].dropna().copy()
            if getattr(s.index, "tz", None) is not None:
                s.index = s.index.tz_localize(None)

            return s.sort_index()
        except Exception:
            time.sleep(i + 1)

    return pd.Series(dtype="float64")


def ultimo_pregao_ate(df_index: pd.Index, dt: pd.Timestamp) -> pd.Timestamp | None:
    pos = df_index.get_indexer([dt], method="ffill")[0]
    if pos == -1:
        return None
    return df_index[pos]


def proximo_pregao_a_partir(df_index: pd.Index, dt: pd.Timestamp) -> pd.Timestamp | None:
    pos = df_index.get_indexer([dt], method="bfill")[0]
    if pos == -1:
        return None
    return df_index[pos]


def gerar_datas_aporte_mensal(df_index: pd.Index, dt_inicio: pd.Timestamp, dt_fim_exclusivo: pd.Timestamp) -> pd.DatetimeIndex:
    if len(df_index) == 0:
        return pd.DatetimeIndex([])
    dt_inicio = pd.to_datetime(dt_inicio).normalize()
    dt_fim_exclusivo = pd.to_datetime(dt_fim_exclusivo).normalize()
    if dt_inicio >= dt_fim_exclusivo:
        return pd.DatetimeIndex([])

    anchor_day = dt_inicio.day
    year, month = dt_inicio.year, dt_inicio.month
    datas_teoricas = []
    cur = dt_inicio

    for _ in range(5000):
        if cur >= dt_fim_exclusivo:
            break
        datas_teoricas.append(cur)
        month += 1
        if month == 13:
            month = 1
            year += 1
        last_day = calendar.monthrange(year, month)[1]
        day = min(anchor_day, last_day)
        cur = pd.Timestamp(year=year, month=month, day=day)

    datas_exec = []
    for d in datas_teoricas:
        d_exec = proximo_pregao_a_partir(df_index, d)
        if d_exec is None:
            continue
        if d_exec < dt_fim_exclusivo:
            datas_exec.append(d_exec)

    if not datas_exec:
        return pd.DatetimeIndex([])
    return pd.DatetimeIndex(datas_exec)


def calc_valor_corrigido_por_indice(valor_mensal: float, datas_aporte: pd.DatetimeIndex, serie_indice: pd.Series, data_ref: pd.Timestamp) -> float | None:
    if serie_indice is None or serie_indice.empty:
        return None
    s = pd.Series(serie_indice).dropna().sort_index()
    end = s.asof(data_ref)
    if pd.isna(end):
        return None
    at = s.reindex(datas_aporte, method="ffill")
    if at.isna().any():
        return None
    return float((valor_mensal * (float(end) / at)).sum())


def _simular_acoes_inteiras(
    df_slice: pd.DataFrame,
    datas_aporte: pd.DatetimeIndex,
    valor_mensal: float,
    incluir_dividendos: bool,
) -> tuple[float, int, float]:
    aporte_set = set(pd.to_datetime(datas_aporte).tolist())

    shares = 0
    cash = 0.0

    for dt, row in df_slice.iterrows():
        close = float(row["Close"]) if pd.notna(row["Close"]) else np.nan
        if not np.isfinite(close) or close <= 0:
            continue

        split_ratio = float(row.get("Split_Eff", 1.0))
        if not np.isfinite(split_ratio) or split_ratio <= 0:
            split_ratio = 1.0

        frac_cash = 0.0
        if split_ratio != 1.0 and shares > 0:
            new_shares = shares * split_ratio
            shares_int = int(np.floor(new_shares + 1e-9))
            frac = new_shares - shares_int
            if frac > 1e-9:
                frac_cash = frac * close
                cash += frac_cash
            shares = shares_int

        div = float(row.get("Dividends", 0.0))
        if not np.isfinite(div) or div < 0:
            div = 0.0

        if incluir_dividendos and div > 0 and shares > 0:
            cash += shares * div

        aporte_today = dt in aporte_set
        if aporte_today:
            cash += valor_mensal

        should_buy = aporte_today or (incluir_dividendos and div > 0) or (frac_cash > 0)
        if should_buy and cash >= close:
            n_buy = int(cash // close)
            if n_buy > 0:
                shares += n_buy
                cash -= n_buy * close

    close_end = float(df_slice["Close"].iloc[-1])
    final_value = shares * close_end + cash
    return float(final_value), int(shares), float(cash)


def calcular_horizonte(
    df_full: pd.DataFrame,
    valor_mensal: float,
    dt_inicio_user: pd.Timestamp,
    dt_ref_target: pd.Timestamp,
    s_rf: pd.Series,
    s_ipca: pd.Series,
    s_ibov: pd.Series,
):
    if df_full is None or df_full.empty or valor_mensal <= 0:
        return None

    idx = df_full.index

    data_ref = ultimo_pregao_ate(idx, dt_ref_target)
    if data_ref is None:
        return None

    dt_inicio_eff = proximo_pregao_a_partir(idx, dt_inicio_user)
    if dt_inicio_eff is None or dt_inicio_eff >= data_ref:
        return None

    datas_aporte = gerar_datas_aporte_mensal(idx, dt_inicio_eff, data_ref)
    if len(datas_aporte) == 0:
        return None

    investido = float(len(datas_aporte) * valor_mensal)

    df_slice = df_full.loc[
        (df_full.index >= dt_inicio_eff) & (df_full.index <= data_ref),
        ["Close", "Dividends", "Split_Eff"],
    ].copy()
    if df_slice.empty:
        return None

    vf_total, shares_total, cash_total = _simular_acoes_inteiras(
        df_slice=df_slice,
        datas_aporte=datas_aporte,
        valor_mensal=valor_mensal,
        incluir_dividendos=True,
    )

    vf_preco, _, _ = _simular_acoes_inteiras(
        df_slice=df_slice,
        datas_aporte=datas_aporte,
        valor_mensal=valor_mensal,
        incluir_dividendos=False,
    )

    lucro_total = vf_total - investido
    lucro_preco = vf_preco - investido
    lucro_proventos = vf_total - vf_preco

    v_rf = calc_valor_corrigido_por_indice(valor_mensal, datas_aporte, s_rf, data_ref) if (s_rf is not None and not s_rf.empty) else None
    v_ipca = calc_valor_corrigido_por_indice(valor_mensal, datas_aporte, s_ipca, data_ref) if (s_ipca is not None and not s_ipca.empty) else None
    v_ibov = calc_valor_corrigido_por_indice(valor_mensal, datas_aporte, s_ibov, data_ref) if (s_ibov is not None and not s_ibov.empty) else None

    return {
        "data_ref": data_ref,
        "dt_inicio_eff": dt_inicio_eff,
        "vf": vf_total,
        "vf_preco": vf_preco,
        "vi": investido,
        "lucro": lucro_total,
        "lucro_proventos": lucro_proventos,
        "lucro_preco": lucro_preco,
        "qtd_acoes": shares_total,
        "caixa": cash_total,
        "v_rf": v_rf,
        "v_ipca": v_ipca,
        "v_ibov": v_ibov,
        "n_aportes": int(len(datas_aporte)),
    }


def serie_pct_desde_base(s: pd.Series, dt_base: pd.Timestamp, dt_end: pd.Timestamp) -> pd.Series:
    if s is None or s.empty:
        return pd.Series(dtype="float64")
    s = pd.Series(s).dropna().sort_index()
    base = s.asof(dt_base)
    if pd.isna(base):
        s2 = s.loc[(s.index >= dt_base) & (s.index <= dt_end)]
        if s2.empty:
            return pd.Series(dtype="float64")
        base = s2.iloc[0]
    s_plot = s.loc[(s.index >= dt_base) & (s.index <= dt_end)]
    if s_plot.empty:
        return pd.Series(dtype="float64")
    return (s_plot / float(base) - 1.0) * 100.0


def add_benchmark_com_estimativa(
    fig: go.Figure,
    s_level: pd.Series,
    nome: str,
    cor: str,
    dt_base: pd.Timestamp,
    dt_end: pd.Timestamp,
    last_official: pd.Timestamp | None,
    width: int = 2,
):
    if s_level is None or s_level.empty:
        return

    y = serie_pct_desde_base(s_level, dt_base, dt_end)
    if y.empty:
        return

    if last_official is None:
        fig.add_trace(go.Scatter(x=y.index, y=y, name=nome, line=dict(color=cor, width=width)))
        return

    cutoff = pd.to_datetime(last_official).normalize()
    if cutoff >= dt_end:
        fig.add_trace(go.Scatter(x=y.index, y=y, name=nome, line=dict(color=cor, width=width)))
        return

    y_off = y.loc[y.index <= cutoff]
    y_est = y.loc[y.index > cutoff]

    if not y_off.empty:
        fig.add_trace(go.Scatter(x=y_off.index, y=y_off, name=nome, line=dict(color=cor, width=width)))

    if not y_est.empty:
        fig.add_trace(go.Scatter(x=y_est.index, y=y_est, name=f"{nome} (estim.)", line=dict(color=cor, width=width, dash="dash")))


def normaliza_ticker_usuario(t: str) -> tuple[str, str]:
    t = (t or "").upper().strip()
    if not t:
        return "", ""
    base = t[:-3] if t.endswith(".SA") else t
    return base, base + ".SA"


TICKER_APELIDOS: dict[str, str] = {
    "BBAS3": "Banco do Brasil",
    "ITUB3": "Banco Itaú",
    "ITUB4": "Banco Itaú",
    "BBDC3": "Banco Bradesco",
    "BBDC4": "Banco Bradesco",
    "SANB3": "Banco Santander",
    "SANB4": "Banco Santander",
    "PETR3": "Petrobras",
    "PETR4": "Petrobras",
    "VALE3": "Vale",
}


def _limpa_nome_yahoo(nome_raw: str) -> str:
    if not nome_raw:
        return ""
    n = " ".join(str(nome_raw).strip().split())
    remove_tokens = {"ON", "PN", "PNA", "PNB", "PNC", "UNT", "UNIT", "NM", "N1", "N2", "MA", "MB"}
    parts = [p for p in n.replace("/", " ").split() if p.upper() not in remove_tokens]
    n2 = " ".join(parts).strip()
    for suf in [" S.A.", " SA"]:
        n2 = n2.replace(suf, " ").strip()
    n2 = " ".join(n2.split())
    title = n2.lower().title()
    for w in [" Da ", " De ", " Do ", " Das ", " Dos ", " E "]:
        title = title.replace(w, w.lower())
    return title.strip()


def nome_comercial_para_ticker(base: str, nome_yahoo: str) -> str:
    base = (base or "").upper().strip()
    if base in TICKER_APELIDOS:
        return TICKER_APELIDOS[base]
    cleaned = _limpa_nome_yahoo(nome_yahoo)
    return cleaned if cleaned else base


@st.cache_data(ttl=60 * 10, show_spinner=False)
def validar_ticker_yahoo(base: str) -> tuple[bool, str]:
    if not base:
        return False, ""
    _, t_sa = normaliza_ticker_usuario(base)
    try:
        tk = yf.Ticker(t_sa)
        h = tk.history(period="5d", auto_adjust=False)
        if h is None or h.empty:
            return False, ""
        nome = ""
        try:
            info = tk.info or {}
            nome = info.get("shortName") or info.get("longName") or ""
        except Exception:
            nome = ""
        return True, nome
    except Exception:
        return False, ""


def _last_date_or_none(s: pd.Series) -> pd.Timestamp | None:
    if s is None:
        return None
    s2 = pd.Series(s).dropna()
    if s2.empty:
        return None
    try:
        return pd.to_datetime(s2.index.max()).normalize()
    except Exception:
        return None


def render_card_html(
    titulo_col: str,
    vf: float | None,
    vi: float | None,
    lucro: float | None,
    lucro_proventos: float | None,
    lucro_preco: float | None,
    qtd_acoes: int | None,
    caixa: float | None,
    v_rf: float | None,
    v_ipca: float | None,
    v_ibov: float | None,
    nome_rf_local: str,
    inicio_eff: pd.Timestamp | None,
    data_ref: pd.Timestamp | None,
    n_aportes: int | None,
    sub_label: str | None = None,
    badge_html: str | None = None,
    mostrar_tudo_bench: bool = False,
    mostrar_rf: bool = True,
    mostrar_ipca: bool = True,
    mostrar_ibov: bool = True,
) -> str:
    if vf is None or vi is None or lucro is None or inicio_eff is None or data_ref is None or n_aportes is None:
        return "\n".join([
            '<div class="total-card">',
            f'  <div class="total-label">{titulo_col}</div>',
            '  <div class="total-amount">—</div>',
            '</div>',
            '<div class="info-card" style="border-top: 1px solid #e2e8f0;">',
            '  <div class="card-header">Aviso</div>',
            '  <div class="card-item">Dados insuficientes para o cálculo neste período.</div>',
            '</div>',
        ])

    rendimento_pct = (lucro / vi) * 100 if vi > 0 else 0.0

    prov_val = float(lucro_proventos) if lucro_proventos is not None else None
    prov_pct = (prov_val / vi) * 100 if (prov_val is not None and vi > 0) else None

    preco_val = float(lucro_preco) if lucro_preco is not None else None
    preco_pct = (preco_val / vi) * 100 if (preco_val is not None and vi > 0) else None

    cor_rendimento = "#166534" if lucro >= 0 else "#b91c1c"

    bench_lines = []

    def line_or_dash(icon: str, label: str, val: float | None) -> str:
        if val is None:
            return f'<div class="card-item">{icon} <b>{label}:</b> —</div>'
        return f'<div class="card-item">{icon} <b>{label}:</b> {formata_br(val)}</div>'

    if mostrar_tudo_bench:
        bench_lines.append(line_or_dash("🎯", nome_rf_local, v_rf))
        bench_lines.append(line_or_dash("📈", "Ibovespa", v_ibov))
        bench_lines.append(line_or_dash("🛡️", "Correção IPCA", v_ipca))
    else:
        if mostrar_rf:
            bench_lines.append(line_or_dash("🎯", nome_rf_local, v_rf))
        if mostrar_ibov:
            bench_lines.append(line_or_dash("📈", "Ibovespa", v_ibov))
        if mostrar_ipca:
            bench_lines.append(line_or_dash("🛡️", "Correção IPCA", v_ipca))
        if not bench_lines:
            bench_lines.append('<div class="card-item">—</div>')

    inicio_eff_str = inicio_eff.date().strftime("%d/%m/%Y")
    data_ref_str = data_ref.date().strftime("%d/%m/%Y")

    qtd_txt = "—" if qtd_acoes is None else formata_int_br(int(qtd_acoes))
    caixa_txt = "—" if (caixa is None or not np.isfinite(float(caixa))) else formata_br(float(caixa))

    parts = []
    parts.append('<div class="total-card">')

    if badge_html:
        parts.append(f'  {badge_html}')

    parts.append(f'  <div class="total-label">{titulo_col}</div>')

    if sub_label:
        parts.append(f'  <div class="total-sub-label">{sub_label}</div>')

    parts.append(f'  <div class="total-amount">{formata_br(vf)}</div>')
    parts.append('</div>')

    parts.append('<div class="info-card">')
    parts.append(f'  <div class="card-item" style="font-size: 1.00rem; margin-bottom: 8px;">💵 <b>Investimento:</b> <span style="color: #475569; font-weight: 600;">{formata_br(vi)}</span></div>')
    parts.append(
        f'  <div class="card-item" style="font-size: 1.00rem; color: {cor_rendimento}; font-weight: 800; margin-bottom: 6px;">'
        f'📈 <b>Rendimento nominal:</b> {formata_br(lucro)} ({rendimento_pct:.2f}%)</div>'
    )

    if prov_val is not None:
        parts.append(f'  <div class="sub-note">Proventos: <span class="v">{formata_br(prov_val)}</span> ({prov_pct:.2f}%)</div>')
    else:
        parts.append('  <div class="sub-note">Proventos: <span class="v">—</span></div>')

    if preco_val is not None:
        parts.append(f'  <div class="sub-note">Preço: <span class="v">{formata_br(preco_val)}</span> ({preco_pct:.2f}%)</div>')
    else:
        parts.append('  <div class="sub-note" style="margin-bottom: 10px;">Preço: <span class="v">—</span></div>')

    parts.append('  <hr style="margin: 10px 0; border: 0; border-top: 1px solid #e2e8f0;">')
    parts.append('  <div class="card-header">Benchmarks (Valor Corrigido)</div>')
    parts.extend([f'  {ln}' for ln in bench_lines])

    parts.append('  <hr style="margin: 10px 0; border: 0; border-top: 1px solid #e2e8f0;">')
    parts.append('  <div class="card-header">Detalhes</div>')
    parts.append(f'  <div class="card-item">📅 <b>Início efetivo:</b> {inicio_eff_str}</div>')
    parts.append(f'  <div class="card-item">📍 <b>Data final usada no cálculo:</b> {data_ref_str}</div>')
    parts.append(f'  <div class="card-item">🗓️ <b>Nº de aportes:</b> {n_aportes}</div>')
    parts.append(f'  <div class="card-item">📦 <b>Qtd. de ações:</b> {qtd_txt}</div>')
    parts.append(f'  <div class="card-item">💰 <b>Caixa (troco):</b> {caixa_txt}</div>')
    parts.append('</div>')

    return "\n".join(parts)


def render_small_links() -> None:
    c1, c2, c3 = st.columns(3, gap="large", vertical_alignment="center")
    with c1:
        st.page_link(
            "app_pages/como_funciona.py",
            label="Metodologia",
            icon=COMO_FUNCIONA_ICON,
            width="content",
        )
    with c2:
        st.page_link(
            "app_pages/glossario.py",
            label="Glossário",
            icon=GLOSSARIO_ICON,
            width="content",
        )
    with c3:
        st.page_link(
            "app_pages/contato.py",
            label="Contato",
            icon=CONTATO_ICON,
            width="content",
        )


st.markdown('<div class="page-title">Simulador de Ações</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="module-subtitle">Avalie o retorno total real de uma ação ao longo do tempo, com preço, proventos reinvestidos, desdobramentos, formação de caixa e comparação com benchmarks.</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="helper-text">Preencha ticker, aporte e período. Depois clique em <b>Analisar patrimônio</b> para gerar o gráfico e os cards da análise.</div>',
    unsafe_allow_html=True,
)

hoje = date.today()
max_inicio = hoje - timedelta(days=1)

d_fim_padrao = hoje - timedelta(days=1)
if d_fim_padrao < MIN_DATA_BANCO:
    d_fim_padrao = MIN_DATA_BANCO + timedelta(days=1)

d_ini_padrao = (pd.Timestamp(d_fim_padrao) - pd.DateOffset(years=10) - pd.Timedelta(days=1)).date()
if d_ini_padrao < MIN_DATA_BANCO:
    d_ini_padrao = MIN_DATA_BANCO

params_prev = st.session_state.get("params", {})
default_ticker = params_prev.get("ticker", "")
default_aporte = float(params_prev.get("aporte", 1000.0))
default_data_inicio = params_prev.get("data_inicio", d_ini_padrao)
default_data_fim = params_prev.get("data_fim", d_fim_padrao)

if default_data_inicio < MIN_DATA_BANCO:
    default_data_inicio = MIN_DATA_BANCO
if default_data_inicio > max_inicio:
    default_data_inicio = max_inicio

if default_data_fim < MIN_DATA_BANCO:
    default_data_fim = MIN_DATA_BANCO
if default_data_fim > hoje:
    default_data_fim = hoje

with st.container(border=True):
    head_left, head_right = st.columns([1.2, 1.0], gap="large", vertical_alignment="top")

    with head_left:
        st.subheader("Configurar simulação", anchor=False)

    status_placeholder = head_right.empty()

    ticker_input_raw = st.text_input(
        "Ticker",
        value=default_ticker,
        placeholder="PETR4, VALE3, BBAS3",
        key="ticker_input_main",
    )

    preview_raw = st.session_state.get("ticker_input_main", default_ticker)
    preview_base, _ = normaliza_ticker_usuario(preview_raw)

    if preview_base:
        if len(preview_base) >= 4:
            ok, nome_raw = validar_ticker_yahoo(preview_base)
            if ok:
                nome_comercial = nome_comercial_para_ticker(preview_base, nome_raw)
                status_placeholder.markdown(
                    f'<div class="ticker-status ticker-ok">Ticker reconhecido: <b>{nome_comercial}</b> ({preview_base})</div>',
                    unsafe_allow_html=True,
                )
            else:
                status_placeholder.markdown(
                    '<div class="ticker-status ticker-bad">Ticker não encontrado. Exemplos: <b>PETR4</b>, <b>VALE3</b>, <b>BBAS3</b></div>',
                    unsafe_allow_html=True,
                )
        else:
            status_placeholder.markdown(
                '<div class="ticker-status ticker-neutral">Exemplos de ticker: <b>PETR4</b>, <b>VALE3</b>, <b>BBAS3</b></div>',
                unsafe_allow_html=True,
            )
    else:
        status_placeholder.markdown(
            '<div class="ticker-status ticker-neutral">Exemplos de ticker: <b>PETR4</b>, <b>VALE3</b>, <b>BBAS3</b></div>',
            unsafe_allow_html=True,
        )

    with st.form("form_simulador_principal", border=False):
        c1, c2, c3 = st.columns([1.0, 1.0, 1.0], gap="medium", vertical_alignment="bottom")

        with c1:
            valor_aporte = st.number_input(
                "Aporte mensal (R$)",
                min_value=0.0,
                value=default_aporte,
                step=100.0,
                key="aporte_input_main",
            )

        with c2:
            data_inicio = st.date_input(
                "Início",
                default_data_inicio,
                min_value=MIN_DATA_BANCO,
                max_value=max_inicio,
                format="DD/MM/YYYY",
                key="data_inicio_input_main",
            )

        with c3:
            data_fim = st.date_input(
                "Fim",
                default_data_fim,
                min_value=MIN_DATA_BANCO,
                max_value=hoje,
                format="DD/MM/YYYY",
                key="data_fim_input_main",
            )

        st.markdown("##### Comparações")
        b1, b2, b3, b4 = st.columns([1.0, 1.0, 1.0, 1.1], gap="medium", vertical_alignment="center")
        with b1:
            mostrar_rf = st.checkbox("CDI / Selic", value=st.session_state.get("mostrar_rf", True), key="mostrar_rf")
        with b2:
            mostrar_ipca = st.checkbox("IPCA", value=st.session_state.get("mostrar_ipca", True), key="mostrar_ipca")
        with b3:
            mostrar_ibov = st.checkbox("Ibovespa", value=st.session_state.get("mostrar_ibov", True), key="mostrar_ibov")
        with b4:
            btn_analisar = st.form_submit_button(
                "Analisar patrimônio",
                type="primary",
                use_container_width=True,
            )

    with st.expander("Performance e cache avançado", expanded=False):
        if REQUESTS_CACHE_AVAILABLE:
            st.checkbox(
                "Ativar cache local para consultas ao BCB",
                value=st.session_state.get("usar_cache_local", True),
                key="usar_cache_local",
            )
            st.caption(
                "Acelera consultas ao BCB e reduz instabilidade de rede. O ajuste vale nas próximas execuções."
            )
        else:
            st.caption("Cache local não disponível porque o pacote requests-cache não está instalado.")

if btn_analisar:
    ticker_base, _ = normaliza_ticker_usuario(st.session_state.get("ticker_input_main", ""))
    ticker_input = ticker_base

    if not ticker_input:
        st.error("Digite um ticker válido para analisar.")
        st.stop()

    if data_inicio >= data_fim:
        st.error("A data de fim deve ser posterior à data de início.")
        st.stop()

    with st.status("Preparando simulação...", expanded=True) as status:
        st.write("Sincronizando dados do ativo no Yahoo Finance...")
        df_acao = carregar_dados_completos(ticker_input, data_inicio, data_fim)
        if df_acao is None or df_acao.empty:
            status.update(label="Falha: ticker não encontrado ou sem dados suficientes.", state="error")
            st.stop()

        st.write("Carregando CDI / Selic...")
        s_rf_raw, nome_rf = carregar_renda_fixa(data_inicio, data_fim)
        rf_last_official = _last_date_or_none(s_rf_raw)
        s_rf = projetar_indice_ate_fim(s_rf_raw, data_fim, prefer_meses=(6, 3), dias_mes=DIAS_MES)

        st.write("Carregando IPCA...")
        s_ipca_raw = carregar_ipca(data_inicio, data_fim)
        ipca_last_official = _last_date_or_none(s_ipca_raw)
        s_ipca = projetar_indice_ate_fim(s_ipca_raw, data_fim, prefer_meses=(6, 3), dias_mes=DIAS_MES)

        st.write("Carregando Ibovespa...")
        s_ibov_raw = carregar_ibov(data_inicio, data_fim)
        ibov_last_official = _last_date_or_none(s_ibov_raw)
        s_ibov = projetar_indice_ate_fim(s_ibov_raw, data_fim, prefer_meses=(6, 3), dias_mes=DIAS_MES)

        status.update(label="Simulação montada com sucesso.", state="complete", expanded=False)

    st.session_state["analysis_ready"] = True
    st.session_state["params"] = {
        "ticker": ticker_input,
        "aporte": float(valor_aporte),
        "data_inicio": data_inicio,
        "data_fim": data_fim,
    }
    st.session_state["df_acao"] = df_acao
    st.session_state["s_rf"] = s_rf
    st.session_state["nome_rf"] = nome_rf
    st.session_state["s_ipca"] = s_ipca
    st.session_state["s_ibov"] = s_ibov
    st.session_state["rf_last_official"] = rf_last_official
    st.session_state["ipca_last_official"] = ipca_last_official
    st.session_state["ibov_last_official"] = ibov_last_official

st.markdown('<div class="section-title">Evolução do retorno total</div>', unsafe_allow_html=True)

if not st.session_state.get("analysis_ready", False):
    st.markdown(
        """
<div class="placeholder-box">
  <div class="ttl">Aqui virá a sua análise</div>
  <div class="txt">
    Depois de preencher ticker, aporte e período, o gráfico de evolução e os cards patrimoniais aparecerão aqui.
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown("")
    render_small_links()
    st.stop()

params = st.session_state["params"]
ticker_exec = params["ticker"]
valor_aporte_exec = float(params["aporte"])
data_inicio_exec = params["data_inicio"]
data_fim_exec = params["data_fim"]

df_acao = st.session_state["df_acao"]
s_rf = st.session_state.get("s_rf", pd.Series(dtype="float64"))
nome_rf = st.session_state.get("nome_rf", "Renda Fixa")
s_ipca = st.session_state.get("s_ipca", pd.Series(dtype="float64"))
s_ibov = st.session_state.get("s_ibov", pd.Series(dtype="float64"))

rf_last_official = st.session_state.get("rf_last_official", None)
ipca_last_official = st.session_state.get("ipca_last_official", None)
ibov_last_official = st.session_state.get("ibov_last_official", None)

dt_ini_user = pd.to_datetime(data_inicio_exec).normalize()
dt_fim_user = pd.to_datetime(data_fim_exec).normalize()

st.caption(
    f"Simulação carregada: **{ticker_exec}** | Aporte mensal: **{formata_br(valor_aporte_exec)}** | "
    f"Período: **{data_inicio_exec.strftime('%d/%m/%Y')} → {data_fim_exec.strftime('%d/%m/%Y')}**"
)

df_v = df_acao.loc[(df_acao.index >= dt_ini_user) & (df_acao.index <= dt_fim_user)].copy()
if df_v.empty:
    st.error("Não há dados do ativo no período selecionado. Tente ampliar ou alterar o intervalo.")
    st.stop()

df_v["Total_Fact_Chart"] = df_v["Total_Fact"] / df_v["Total_Fact"].iloc[0]
df_v["Price_Fact_Chart"] = df_v["Price_Fact"] / df_v["Price_Fact"].iloc[0]

dt_base_chart = df_v.index[0]
dt_end_chart = df_v.index[-1]

primeiro_dado_ativo = df_acao.index.min()
if dt_ini_user < primeiro_dado_ativo:
    st.markdown(
        f"""
<div class="warn-box">
Você escolheu <b>Início</b> em {dt_ini_user.date().strftime('%d/%m/%Y')}, mas o ativo só tem dados a partir de
<b>{primeiro_dado_ativo.date().strftime('%d/%m/%Y')}</b>.<br>
Nos cálculos, os aportes passam a contar a partir do <b>primeiro pregão disponível</b>.
</div>
""",
        unsafe_allow_html=True,
    )

fig = go.Figure()

if mostrar_rf and (s_rf is not None) and (not s_rf.empty):
    add_benchmark_com_estimativa(fig, s_rf, nome_rf, COR_CDI, dt_base_chart, dt_end_chart, rf_last_official, width=2)

if mostrar_ipca and (s_ipca is not None) and (not s_ipca.empty):
    add_benchmark_com_estimativa(fig, s_ipca, "IPCA", COR_IPCA, dt_base_chart, dt_end_chart, ipca_last_official, width=2)

if mostrar_ibov and (s_ibov is not None) and (not s_ibov.empty):
    y_ibov = serie_pct_desde_base(s_ibov, dt_base_chart, dt_end_chart)
    if not y_ibov.empty:
        fig.add_trace(go.Scatter(x=y_ibov.index, y=y_ibov, name="Ibovespa", line=dict(color=COR_IBOV, width=2)))

fig.add_trace(
    go.Scatter(
        x=df_v.index,
        y=(df_v["Price_Fact_Chart"] - 1) * 100,
        stackgroup="one",
        name="Valorização",
        fillcolor="rgba(31, 119, 180, 0.4)",
        line=dict(width=0),
    )
)
fig.add_trace(
    go.Scatter(
        x=df_v.index,
        y=(df_v["Total_Fact_Chart"] - df_v["Price_Fact_Chart"]) * 100,
        stackgroup="one",
        name="Proventos (reinvestidos)",
        fillcolor="rgba(218, 165, 32, 0.4)",
        line=dict(width=0),
    )
)
fig.add_trace(
    go.Scatter(
        x=df_v.index,
        y=(df_v["Total_Fact_Chart"] - 1) * 100,
        name="RETORNO TOTAL",
        line=dict(color="black", width=3),
    )
)

fig.update_layout(
    template="plotly_white",
    hovermode="x unified",
    yaxis=dict(side="right", ticksuffix="%", tickformat=".0f"),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
)
fig.update_xaxes(range=[dt_ini_user, dt_fim_user])

st.plotly_chart(fig, use_container_width=True)

st.markdown('<div class="section-title">Patrimônio acumulado</div>', unsafe_allow_html=True)
st.caption("1º card = período selecionado. Os demais mantêm horizontes fixos para comparação.")

cols = st.columns(3)

dt_ini_eff = proximo_pregao_a_partir(df_acao.index, dt_ini_user)
if dt_ini_eff is None:
    st.error("Não foi possível determinar o primeiro pregão disponível para o ativo.")
    st.stop()

with cols[0]:
    res_periodo = calcular_horizonte(
        df_full=df_acao,
        valor_mensal=float(valor_aporte_exec),
        dt_inicio_user=dt_ini_user,
        dt_ref_target=dt_fim_user,
        s_rf=s_rf,
        s_ipca=s_ipca,
        s_ibov=s_ibov,
    )

    if res_periodo is None:
        st.markdown(
            render_card_html(
                titulo_col="Total no período",
                vf=None, vi=None, lucro=None,
                lucro_proventos=None, lucro_preco=None,
                qtd_acoes=None, caixa=None,
                v_rf=None, v_ipca=None, v_ibov=None,
                nome_rf_local=nome_rf,
                inicio_eff=None, data_ref=None,
                n_aportes=None,
                sub_label=None,
                badge_html=None,
                mostrar_tudo_bench=True,
            ),
            unsafe_allow_html=True,
        )
    else:
        anos, meses, dias = decompor_periodo_anos_meses_dias(res_periodo["dt_inicio_eff"], res_periodo["data_ref"])
        titulo_main, sub = titulo_periodo_dinamico(anos, meses, dias)

        st.markdown(
            render_card_html(
                titulo_col=titulo_main,
                vf=res_periodo["vf"],
                vi=res_periodo["vi"],
                lucro=res_periodo["lucro"],
                lucro_proventos=res_periodo["lucro_proventos"],
                lucro_preco=res_periodo["lucro_preco"],
                qtd_acoes=int(res_periodo["qtd_acoes"]),
                caixa=float(res_periodo["caixa"]),
                v_rf=res_periodo["v_rf"],
                v_ipca=res_periodo["v_ipca"],
                v_ibov=res_periodo["v_ibov"],
                nome_rf_local=nome_rf,
                inicio_eff=res_periodo["dt_inicio_eff"],
                data_ref=res_periodo["data_ref"],
                n_aportes=res_periodo["n_aportes"],
                sub_label=sub,
                badge_html='<div class="badge-dinamico">Período selecionado</div>',
                mostrar_tudo_bench=True,
            ),
            unsafe_allow_html=True,
        )

horizontes = [10, 5]
for anos_h, col in zip(horizontes, cols[1:]):
    with col:
        titulo_col = f"Total em {anos_h} anos"
        dt_target = dt_ini_eff + pd.DateOffset(years=anos_h)

        if dt_target > dt_fim_user:
            st.markdown(
                "\n".join([
                    '<div class="total-card">',
                    '  <div class="badge-fixo">Horizonte fixo</div>',
                    f'  <div class="total-label">{titulo_col}</div>',
                    '  <div class="total-amount">—</div>',
                    '</div>',
                    '<div class="info-card" style="border-top: 1px solid #e2e8f0;">',
                    '  <div class="card-header">Período insuficiente</div>',
                    f'  <div class="card-item">Para calcular <b>{anos_h} anos</b>, aumente a data final para <b>≥ {dt_target.date().strftime("%d/%m/%Y")}</b>.</div>',
                    '</div>',
                ]),
                unsafe_allow_html=True,
            )
            continue

        res = calcular_horizonte(
            df_full=df_acao,
            valor_mensal=float(valor_aporte_exec),
            dt_inicio_user=dt_ini_user,
            dt_ref_target=dt_target,
            s_rf=s_rf if mostrar_rf else pd.Series(dtype="float64"),
            s_ipca=s_ipca if mostrar_ipca else pd.Series(dtype="float64"),
            s_ibov=s_ibov if mostrar_ibov else pd.Series(dtype="float64"),
        )

        st.markdown(
            render_card_html(
                titulo_col=titulo_col,
                vf=res["vf"] if res else None,
                vi=res["vi"] if res else None,
                lucro=res["lucro"] if res else None,
                lucro_proventos=res["lucro_proventos"] if res else None,
                lucro_preco=res["lucro_preco"] if res else None,
                qtd_acoes=int(res["qtd_acoes"]) if res else None,
                caixa=float(res["caixa"]) if res else None,
                v_rf=res["v_rf"] if res else None,
                v_ipca=res["v_ipca"] if res else None,
                v_ibov=res["v_ibov"] if res else None,
                nome_rf_local=nome_rf,
                inicio_eff=res["dt_inicio_eff"] if res else None,
                data_ref=res["data_ref"] if res else None,
                n_aportes=res["n_aportes"] if res else None,
                sub_label=None,
                badge_html='<div class="badge-fixo">Horizonte fixo</div>',
                mostrar_tudo_bench=False,
                mostrar_rf=mostrar_rf,
                mostrar_ipca=mostrar_ipca,
                mostrar_ibov=mostrar_ibov,
            ),
            unsafe_allow_html=True,
        )

st.divider()
render_small_links()