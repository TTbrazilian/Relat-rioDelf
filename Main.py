import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io, base64, requests

# ── Página ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Balsa Delfinópolis 2026",
    page_icon="⛴️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state inicial ─────────────────────────────────────────────────────
if "dark_mode"  not in st.session_state: st.session_state.dark_mode  = False
if "mes_ativo"  not in st.session_state: st.session_state.mes_ativo  = None

# ── Paletas claro / escuro ────────────────────────────────────────────────────
DARK = st.session_state.dark_mode

T = {
    "bg"            : "#0F172A" if DARK else "#F0F4F8",
    "card_bg"       : "#1E293B" if DARK else "#FFFFFF",
    "card_border"   : "#334155" if DARK else "#E2E8F0",
    "text_primary"  : "#F1F5F9" if DARK else "#1E293B",
    "text_secondary": "#94A3B8" if DARK else "#64748B",
    "text_muted"    : "#64748B" if DARK else "#94A3B8",
    "chart_bg"      : "#1E293B" if DARK else "#FFFFFF",
    "chart_grid"    : "#334155" if DARK else "#F1F5F9",
    "sidebar_bg"    : "#0D1F35" if DARK else "#1F4E79",
    "input_bg"      : "#1E293B" if DARK else "#FFFFFF",
    "input_border"  : "#475569" if DARK else "#CBD5E1",
    "btn_bg"        : "#1E293B" if DARK else "#FFFFFF",
    "btn_text"      : "#94A3B8" if DARK else "#475569",
    "btn_border"    : "#334155" if DARK else "#CBD5E1",
    "table_bg"      : "#1E293B" if DARK else "#FFFFFF",
    "table_header"  : "#0F172A" if DARK else "#F8FAFC",
    "table_text"    : "#F1F5F9" if DARK else "#1E293B",
    "table_border"  : "#334155" if DARK else "#E2E8F0",
    "zero_bar"      : "#334155" if DARK else "#E2E8F0",
    "toggle_icon"   : "🌙" if not DARK else "☀️",
    "toggle_label"  : "Modo Escuro" if not DARK else "Modo Claro",
}

COR_VISITANTE = "#3B82F6" if DARK else "#2E75B6"
COR_LOCAL     = "#4ADE80" if DARK else "#16A34A"

# ── CSS global dinâmico ───────────────────────────────────────────────────────
st.markdown(f"""
<style>
/* ── reset & fundo ── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="block-container"] {{
    background-color: {T['bg']} !important;
}}
[data-testid="stMain"] {{ background: {T['bg']} !important; }}

/* ── sidebar ── */
[data-testid="stSidebar"] {{
    background: {T['sidebar_bg']} !important;
}}
[data-testid="stSidebar"] * {{ color: #FFFFFF !important; }}
[data-testid="stSidebar"] .stRadio label {{ color: #FFFFFF !important; }}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
    color: rgba(255,255,255,.7) !important;
}}

/* ── textos gerais ── */
p, span, div, label, li {{
    color: {T['text_primary']};
}}
h1, h2, h3, h4 {{ color: {T['text_primary']} !important; }}

/* ── Streamlit markdown ── */
[data-testid="stMarkdownContainer"] * {{ color: {T['text_primary']}; }}

/* ── Cards KPI ── */
.metric-card {{
    background: {T['card_bg']};
    border: 1px solid {T['card_border']};
    border-radius: 14px; padding: 18px 22px;
    box-shadow: 0 2px 8px rgba(0,0,0,{".25" if DARK else ".06"});
    text-align: center;
}}
.metric-val {{ font-size: 1.9rem; font-weight: 700; color: {T['text_primary']}; }}
.metric-lab {{ font-size: .8rem; color: {T['text_secondary']}; margin-top: 5px; }}

/* ── Badge seção ── */
.section-badge {{
    display: inline-block; padding: 4px 16px; border-radius: 20px;
    font-weight: 600; font-size: .88rem; margin-bottom: 14px;
}}

/* ── Container gráfico ── */
.chart-card {{
    background: {T['card_bg']};
    border: 1px solid {T['card_border']};
    border-radius: 14px; padding: 24px 20px 12px;
    box-shadow: 0 2px 10px rgba(0,0,0,{".3" if DARK else ".07"});
}}

/* ── Botões pill dos meses ── */
div[data-testid="stHorizontalBlock"] button {{
    border-radius: 999px !important;
    border: 1.5px solid {T['input_border']} !important;
    background: {T['btn_bg']} !important;
    color: {T['btn_text']} !important;
    font-size: .75rem !important;
    font-weight: 500 !important;
    padding: 4px 6px !important;
    transition: all .15s !important;
}}
div[data-testid="stHorizontalBlock"] button:hover {{
    border-color: #94A3B8 !important;
    background: {"#334155" if DARK else "#F1F5F9"} !important;
}}

/* ── Dataframe / tabela ── */
[data-testid="stDataFrame"] {{
    background: {T['table_bg']} !important;
    border-radius: 10px;
    border: 1px solid {T['table_border']};
}}
[data-testid="stDataFrame"] * {{ color: {T['table_text']} !important; }}
.dvn-scroller {{ background: {T['table_bg']} !important; }}

/* ── Botão download ── */
[data-testid="stDownloadButton"] button {{
    background: {T['card_bg']} !important;
    border: 1px solid {T['input_border']} !important;
    color: {T['text_primary']} !important;
    border-radius: 8px !important;
}}

/* ── Divisor ── */
hr {{ border-color: {T['card_border']} !important; }}

/* ── Subtítulo mês ── */
.subtitle-mes {{
    color: {T['text_secondary']};
    font-size: .85rem;
    margin-top: -10px;
    margin-bottom: 4px;
}}
</style>
""", unsafe_allow_html=True)

# ── Bandeira (base64 via requests, SVG embutido como fallback) ────────────────
@st.cache_data(show_spinner=False)
def get_flag_b64() -> str:
    """Tenta baixar a bandeira; retorna SVG embutido se falhar."""
    svg_fallback = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 360 240'>"
        "<rect width='360' height='240' fill='#1a3a6e'/>"
        "<rect x='0' y='80' width='360' height='80' fill='white'/>"
        "<text x='180' y='132' font-family='Georgia,serif' font-size='22' "
        "font-weight='bold' fill='#1a3a6e' text-anchor='middle'>DELFINÓPOLIS</text>"
        "<polygon points='180,14 193,52 234,52 201,74 213,112 180,90 147,112 "
        "159,74 126,52 167,52' fill='#f5c518'/>"
        "</svg>"
    )
    try:
        url = (
            "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/"
            "Bandeira_de_Delfin%C3%B3polis.png/200px-Bandeira_de_Delfin%C3%B3polis.png"
        )
        r = requests.get(url, timeout=6,
                         headers={"User-Agent": "StreamlitApp/1.0 (educational project)"})
        if r.status_code == 200 and len(r.content) > 500:
            b64 = base64.b64encode(r.content).decode()
            return f"data:image/png;base64,{b64}"
    except Exception:
        pass
    b64 = base64.b64encode(svg_fallback.encode()).decode()
    return f"data:image/svg+xml;base64,{b64}"

flag_src = get_flag_b64()

# ── Carrega dados ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data(path: str):
    raw = pd.read_csv(path, sep=";", header=None, encoding="utf-8-sig", dtype=str)
    month_row = raw.iloc[0].fillna("").tolist()
    sub_row   = raw.iloc[1].fillna("").tolist()

    current_month = ""
    col_map = {}
    for i, (m, s) in enumerate(zip(month_row, sub_row)):
        if m.strip(): current_month = m.strip()
        if s.strip() and i > 0: col_map[i] = (current_month, s.strip())

    data_rows = raw.iloc[2:].reset_index(drop=True)
    records, current_section = [], ""
    for _, row in data_rows.iterrows():
        desc = str(row.iloc[0]).strip()
        if not desc or desc == "nan":            continue
        if "VEÍCULOS VISITANTES" in desc:        current_section = "VISITANTE"; continue
        if "VEÍCULOS LOCAIS"     in desc:        current_section = "LOCAL";     continue
        if desc.startswith("TOTAL"):             continue

        record = {"DESCRIÇÃO": desc, "SEÇÃO": current_section}
        for ci, (month, sub) in col_map.items():
            vs = str(row.iloc[ci]).replace(".", "").replace(",", ".").strip()
            try:    record[(month, sub)] = float(vs)
            except: record[(month, sub)] = 0.0
        records.append(record)

    df = pd.DataFrame(records)
    df["DESC_CURTA"] = (
        df["DESCRIÇÃO"]
        .str.replace(r"\s+VISITANTE$", "", regex=True)
        .str.replace(r"\s+LOCAL$",     "", regex=True)
        .str.strip()
    )
    mes_ordem = [
        "Janeiro 2026","Fevereiro 2026","Março 2026","Abril 2026",
        "Maio 2026","Junho 2026","Julho 2026","Agosto 2026",
        "Setembro 2026","Outubro 2026","Novembro 2026","Dezembro 2026",
        "Feriados Abril 2026","Feriados Maio 2026",
    ]
    meses_ok = [m for m in mes_ordem if m in {k[0] for k in col_map.values()}]
    return df, meses_ok

CSV_PATH = "Relatório_Balsa_Delfs_2026.csv"
df_all, MESES = load_data(CSV_PATH)

ABREV = {
    "Janeiro 2026":"Jan","Fevereiro 2026":"Fev","Março 2026":"Mar",
    "Abril 2026":"Abr","Maio 2026":"Mai","Junho 2026":"Jun",
    "Julho 2026":"Jul","Agosto 2026":"Ago","Setembro 2026":"Set",
    "Outubro 2026":"Out","Novembro 2026":"Nov","Dezembro 2026":"Dez",
    "Feriados Abril 2026":"Fer.Abr","Feriados Maio 2026":"Fer.Mai",
}

if st.session_state.mes_ativo not in MESES:
    st.session_state.mes_ativo = MESES[0]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;margin-bottom:14px">
      <img src="{flag_src}"
           style="width:88%;border-radius:10px;border:2px solid rgba(255,255,255,.3);
                  box-shadow:0 4px 12px rgba(0,0,0,.4)"
           alt="Bandeira de Delfinópolis">
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## ⛴️ Balsa Delfinópolis")
    st.markdown("**Relatório de Tráfego — 2026**")
    st.markdown("---")

    secao = st.radio(
        "**Tipo de veículo**",
        ["VISITANTE", "LOCAL"],
        format_func=lambda x: "🔵 Visitante" if x == "VISITANTE" else "🟢 Local",
    )
    st.markdown("---")
    metrica = st.radio(
        "**Métrica exibida**",
        ["QTD", "EST PASSAGEIROS"],
        format_func=lambda x: "🚗 Quantidade de veículos" if x == "QTD" else "👥 Est. passageiros",
    )
    st.markdown("---")

    # ── Toggle modo escuro ────────────────────────────────────────────────────
    if st.button(f"{T['toggle_icon']}  {T['toggle_label']}", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.markdown("---")
    st.markdown(
        f"<small style='opacity:.6'>Dados: Relatório Balsa Delfs 2026</small>",
        unsafe_allow_html=True,
    )

# ── Cor da seção ──────────────────────────────────────────────────────────────
COR_SECAO   = COR_VISITANTE if secao == "VISITANTE" else COR_LOCAL
LABEL_SECAO = "Visitante"   if secao == "VISITANTE" else "Local"
metrica_label = "Quantidade de Veículos" if metrica == "QTD" else "Estimativa de Passageiros"

# ── Dados ─────────────────────────────────────────────────────────────────────
df_sec = df_all[df_all["SEÇÃO"] == secao].copy()

long_rows = []
for mes in MESES:
    col = (mes, metrica)
    if col in df_sec.columns:
        tmp = df_sec[["DESC_CURTA", col]].copy()
        tmp.columns = ["Descrição","Valor"]
        tmp["Mês"] = mes
        long_rows.append(tmp)
df_long = pd.concat(long_rows, ignore_index=True) if long_rows else pd.DataFrame(
    columns=["Descrição","Valor","Mês"])

def get_mes_df(mes):
    col = (mes, metrica)
    if col not in df_sec.columns:
        return pd.DataFrame(columns=["Descrição","Valor"])
    tmp = df_sec[["DESC_CURTA", col]].copy()
    tmp.columns = ["Descrição","Valor"]
    return tmp.sort_values("Valor", ascending=True)

# ── Cabeçalho ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<h1 style='margin-bottom:0;color:{T["text_primary"]}'>
  ⛴️ Balsa Delfinópolis — 2026
</h1>
<p style='color:{T["text_secondary"]};margin-top:4px;font-size:.95rem'>
  Tráfego de veículos e estimativa de passageiros
</p>
""", unsafe_allow_html=True)

st.markdown(f"""
<span class='section-badge'
  style='background:{COR_SECAO}22;color:{COR_SECAO};border:1.5px solid {COR_SECAO}'>
  {'🔵' if secao=='VISITANTE' else '🟢'}&nbsp; Veículos {LABEL_SECAO}s &nbsp;·&nbsp; {metrica}
</span>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
total_geral   = df_long["Valor"].sum()
por_mes       = df_long.groupby("Mês")["Valor"].sum()
mes_destaque  = por_mes.idxmax() if not por_mes.empty else "—"
val_destaque  = por_mes.max()    if not por_mes.empty else 0
n_tipos       = df_sec["DESC_CURTA"].nunique()
val_mes_ativo = df_long[df_long["Mês"] == st.session_state.mes_ativo]["Valor"].sum()

c1, c2, c3, c4 = st.columns(4)
for col, val, lab in [
    (c1, f"{total_geral:,.0f}".replace(",","."),   f"Total acumulado — {metrica}"),
    (c2, ABREV.get(mes_destaque, mes_destaque),     "Mês com maior volume"),
    (c3, f"{val_destaque:,.0f}".replace(",","."),   "Volume no mês destaque"),
    (c4, f"{val_mes_ativo:,.0f}".replace(",","."),  f"Volume — {ABREV.get(st.session_state.mes_ativo,'')}"),
]:
    col.markdown(f"""
    <div class='metric-card'>
      <div class='metric-val'>{val}</div>
      <div class='metric-lab'>{lab}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Título + pills dos meses ──────────────────────────────────────────────────
st.markdown(f"<h3 style='color:{T['text_primary']}'>📅 Veículos por tipo</h3>",
            unsafe_allow_html=True)
st.markdown(
    f"<p class='subtitle-mes' style='color:{T['text_secondary']}'>"
    "Selecione o mês para atualizar o gráfico</p>",
    unsafe_allow_html=True,
)

cols_pill = st.columns(len(MESES))
for i, mes in enumerate(MESES):
    abrev    = ABREV.get(mes, mes)
    is_active = (mes == st.session_state.mes_ativo)
    with cols_pill[i]:
        if is_active:
            st.markdown(f"""
            <div style="
              text-align:center; padding:7px 2px; border-radius:999px;
              background:{COR_SECAO}; color:white; font-size:.72rem;
              font-weight:700; border:2px solid {COR_SECAO}; line-height:1.2;
              margin-bottom:2px; user-select:none
            ">{abrev}</div>
            """, unsafe_allow_html=True)
        else:
            if st.button(abrev, key=f"pill_{mes}", use_container_width=True):
                st.session_state.mes_ativo = mes
                st.rerun()

st.markdown("<br style='margin:0'>", unsafe_allow_html=True)

# ── Gráfico de barras horizontal com animação ─────────────────────────────────
df_grafico = get_mes_df(st.session_state.mes_ativo)

cores_barra = [
    COR_SECAO if v > 0 else T["zero_bar"]
    for v in df_grafico["Valor"]
]

# Hover estilo "education dashboard":
# linha 1 → tipo de veículo  |  linha 2 → rótulo métrica  |  linha 3 → valor em destaque
hover_tpl = (
    f"<b style='font-size:13px;color:{T['text_primary']}'>%{{y}}</b><br>"
    f"<span style='font-size:11px;color:{T['text_secondary']}'>{metrica_label}</span><br>"
    f"<b style='font-size:18px;color:{COR_SECAO}'>%{{x:,.0f}}</b>"
    "<extra></extra>"
)

fig = go.Figure()
fig.add_trace(go.Bar(
    x=df_grafico["Valor"],
    y=df_grafico["Descrição"],
    orientation="h",
    marker=dict(
        color=cores_barra,
        line=dict(width=0),
        opacity=0.92,
    ),
    text=df_grafico["Valor"].apply(
        lambda v: f"{int(v):,}".replace(",", ".") if v > 0 else ""
    ),
    textposition="outside",
    textfont=dict(size=11, color=T["text_secondary"]),
    hovertemplate=hover_tpl,
    hoverlabel=dict(
        bgcolor=T["card_bg"],
        bordercolor=COR_SECAO,
        font=dict(family="Arial", size=12, color=T["text_primary"]),
        namelength=0,
    ),
    cliponaxis=False,
))

# ── Animação: transition suave ao trocar mês/seção/métrica ───────────────────
fig.update_layout(
    transition=dict(
        duration=550,
        easing="cubic-in-out",
        ordering="traces first",
    ),
    plot_bgcolor=T["chart_bg"],
    paper_bgcolor=T["chart_bg"],
    font=dict(family="Arial", size=12, color=T["text_secondary"]),
    xaxis=dict(
        gridcolor=T["chart_grid"],
        zeroline=False,
        showline=False,
        tickfont=dict(size=11, color=T["text_muted"]),
        title=dict(text=metrica_label, font=dict(size=12, color=T["text_muted"])),
    ),
    yaxis=dict(
        gridcolor="rgba(0,0,0,0)",
        tickfont=dict(size=11, color=T["text_primary"]),
        automargin=True,
    ),
    margin=dict(t=16, b=16, l=10, r=90),
    height=max(400, len(df_grafico) * 36),
    bargap=0.30,
    hoverdistance=20,
)

st.markdown(f"<div class='chart-card'>", unsafe_allow_html=True)
# key fixo → Streamlit mantém o mesmo elemento e o Plotly anima a transição
st.plotly_chart(fig, use_container_width=True,
                config={"displayModeBar": False}, key="chart_main")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabela detalhada ──────────────────────────────────────────────────────────
st.markdown(f"<h3 style='color:{T['text_primary']}'>📋 Tabela detalhada</h3>",
            unsafe_allow_html=True)

tab_pivot = df_long.pivot_table(
    index="Descrição", columns="Mês", values="Valor", aggfunc="sum"
).fillna(0)
tab_pivot = tab_pivot.reindex(columns=[m for m in MESES if m in tab_pivot.columns])
tab_pivot["TOTAL"] = tab_pivot.sum(axis=1)
tab_pivot = tab_pivot.sort_values("TOTAL", ascending=False)

tab_fmt = tab_pivot.copy()
for c in tab_fmt.columns:
    tab_fmt[c] = tab_fmt[c].apply(lambda v: f"{int(v):,}".replace(",", "."))

st.dataframe(tab_fmt, use_container_width=True, height=400)

buf = io.BytesIO()
tab_pivot.to_excel(buf, index=True)
st.download_button(
    label="⬇️ Exportar tabela (.xlsx)",
    data=buf.getvalue(),
    file_name=f"balsa_delfin_{secao.lower()}_{metrica.replace(' ','_')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.markdown("---")
st.markdown(
    f"<small style='color:{T['text_muted']}'>Dados: Relatório Balsa Delfs 2026 · "
    "Município de Delfinópolis – MG</small>",
    unsafe_allow_html=True,
)