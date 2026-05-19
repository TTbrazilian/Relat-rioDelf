import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io, base64
from pathlib import Path

# ── Página ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Balsa Delfinópolis 2026",
    page_icon="⛴️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("dark_mode", False), ("mes_ativo", None), ("acumulado", False)]:
    if k not in st.session_state:
        st.session_state[k] = v

DARK = st.session_state.dark_mode

# ── Paletas ───────────────────────────────────────────────────────────────────
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
    "input_border"  : "#475569" if DARK else "#CBD5E1",
    "btn_bg"        : "#1E293B" if DARK else "#FFFFFF",
    "btn_text"      : "#94A3B8" if DARK else "#475569",
    "btn_border"    : "#334155" if DARK else "#CBD5E1",
    "zero_bar"      : "#334155" if DARK else "#E2E8F0",
    "tbl_bg"        : "#1E293B" if DARK else "#FFFFFF",
    "tbl_head_bg"   : "#0F172A" if DARK else "#F1F5F9",
    "tbl_head_txt"  : "#94A3B8" if DARK else "#475569",
    "tbl_row_alt"   : "#253247" if DARK else "#F8FAFC",
    "tbl_txt"       : "#E2E8F0" if DARK else "#1E293B",
    "tbl_border"    : "#334155" if DARK else "#E2E8F0",
    "toggle_icon"   : "☀️" if DARK else "🌙",
    "toggle_label"  : "Modo Claro" if DARK else "Modo Escuro",
}

COR_VISITANTE = "#3B82F6" if DARK else "#2E75B6"
COR_LOCAL     = "#34D399" if DARK else "#16A34A"

# ── CSS dinâmico ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="block-container"] {{
    background-color: {T['bg']} !important;
    color: {T['text_primary']} !important;
}}
[data-testid="stSidebar"] {{
    background: {T['sidebar_bg']} !important;
}}
[data-testid="stSidebar"] *       {{ color: #FFFFFF !important; }}
[data-testid="stSidebar"] small   {{ color: rgba(255,255,255,.6) !important; }}

/* textos gerais fora da sidebar */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] li {{
    color: {T['text_primary']} !important;
}}

/* cards KPI */
.kpi-card {{
    background: {T['card_bg']};
    border: 1px solid {T['card_border']};
    border-radius: 14px; padding: 18px 22px;
    box-shadow: 0 2px 8px rgba(0,0,0,{'.28' if DARK else '.06'});
    text-align: center;
}}
.kpi-val {{ font-size: 1.85rem; font-weight: 700; color: {T['text_primary']}; }}
.kpi-lab {{ font-size: .78rem; color: {T['text_secondary']}; margin-top: 5px; }}

/* badge seção */
.section-badge {{
    display:inline-block; padding:4px 16px; border-radius:20px;
    font-weight:600; font-size:.88rem; margin-bottom:14px;
}}

/* container gráfico */
.chart-card {{
    background: {T['card_bg']};
    border: 1px solid {T['card_border']};
    border-radius: 14px; padding: 22px 18px 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,{'.32' if DARK else '.07'});
}}

/* pills meses */
div[data-testid="stHorizontalBlock"] button {{
    border-radius: 999px !important;
    border: 1.5px solid {T['input_border']} !important;
    background: {T['btn_bg']} !important;
    color: {T['btn_text']} !important;
    font-size: .72rem !important; font-weight: 500 !important;
    padding: 4px 4px !important; transition: all .15s !important;
}}
div[data-testid="stHorizontalBlock"] button:hover {{
    border-color: #94A3B8 !important;
    background: {'#334155' if DARK else '#F1F5F9'} !important;
}}

/* botão download */
[data-testid="stDownloadButton"] button {{
    background: {T['card_bg']} !important;
    border: 1px solid {T['input_border']} !important;
    color: {T['text_primary']} !important;
    border-radius: 8px !important;
}}

hr {{ border-color: {T['card_border']} !important; }}
</style>
""", unsafe_allow_html=True)

# ── Bandeira — arquivo local do repositório ───────────────────────────────────
@st.cache_data(show_spinner=False)
def get_flag_b64() -> str:
    """Carrega Bandeira.png do repositório como base64."""
    for candidate in [Path("Bandeira.png"),
                      Path("Relat-rioDelf/Bandeira.png"),
                      Path("relat-riodelf/Bandeira.png")]:
        if candidate.exists():
            data = candidate.read_bytes()
            return "data:image/png;base64," + base64.b64encode(data).decode()
    # fallback SVG simples
    svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 360 240'>"
           "<rect width='360' height='240' fill='#1a3a6e'/>"
           "<rect x='0' y='80' width='360' height='80' fill='white'/>"
           "<text x='180' y='132' font-family='serif' font-size='20' font-weight='bold' "
           "fill='#1a3a6e' text-anchor='middle'>DELFINÓPOLIS</text>"
           "<polygon points='180,14 193,52 234,52 201,74 213,112 180,90 147,112 "
           "159,74 126,52 167,52' fill='#f5c518'/></svg>")
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

flag_src = get_flag_b64()

# ── Carrega & parseia CSV ─────────────────────────────────────────────────────
@st.cache_data
def load_data(path: str):
    raw = pd.read_csv(path, sep=";", header=None, encoding="utf-8-sig", dtype=str)
    month_row = raw.iloc[0].fillna("").tolist()
    sub_row   = raw.iloc[1].fillna("").tolist()

    current_month, col_map = "", {}
    for i, (m, s) in enumerate(zip(month_row, sub_row)):
        if m.strip(): current_month = m.strip()
        if s.strip() and i > 0: col_map[i] = (current_month, s.strip())

    data_rows = raw.iloc[2:].reset_index(drop=True)
    records, current_section = [], ""
    for _, row in data_rows.iterrows():
        desc = str(row.iloc[0]).strip()
        if not desc or desc == "nan":        continue
        if "VEÍCULOS VISITANTES" in desc:    current_section = "VISITANTE"; continue
        if "VEÍCULOS LOCAIS"     in desc:    current_section = "LOCAL";     continue
        if desc.startswith("TOTAL"):         continue
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
    return df, meses_ok, col_map

CSV_PATH = "Relatório_Balsa_Delfs_2026.csv"
df_all, MESES, col_map = load_data(CSV_PATH)

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
           style="width:90%;border-radius:10px;
                  border:2px solid rgba(255,255,255,.35);
                  box-shadow:0 4px 14px rgba(0,0,0,.5)"
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
        format_func=lambda x: "🚗 Quantidade" if x == "QTD" else "👥 Est. passageiros",
    )
    st.markdown("---")

    if st.button(f"{T['toggle_icon']}  {T['toggle_label']}", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.markdown("---")
    st.markdown("<small style='opacity:.6'>Dados: Relatório Balsa Delfs 2026</small>",
                unsafe_allow_html=True)

# ── Derivados ─────────────────────────────────────────────────────────────────
COR_SECAO     = COR_VISITANTE if secao == "VISITANTE" else COR_LOCAL
LABEL_SECAO   = "Visitante"   if secao == "VISITANTE" else "Local"
metrica_label = "Quantidade" if metrica == "QTD" else "Estimativa de Passageiros"

df_sec = df_all[df_all["SEÇÃO"] == secao].copy()

# long com todos os meses (para KPIs e tabela)
long_rows = []
for mes in MESES:
    col_key = (mes, metrica)
    if col_key in df_sec.columns:
        tmp = df_sec[["DESC_CURTA", col_key]].copy()
        tmp.columns = ["Descrição", "Valor"]
        tmp["Mês"] = mes
        long_rows.append(tmp)
df_long = (pd.concat(long_rows, ignore_index=True)
           if long_rows else pd.DataFrame(columns=["Descrição","Valor","Mês"]))

def get_mes_df(mes: str) -> pd.DataFrame:
    col_key = (mes, metrica)
    if col_key not in df_sec.columns:
        return pd.DataFrame(columns=["Descrição","Valor"])
    tmp = df_sec[["DESC_CURTA", col_key]].copy()
    tmp.columns = ["Descrição","Valor"]
    return tmp.sort_values("Valor", ascending=True)

def get_acumulado_df() -> pd.DataFrame:
    """Soma de todos os meses por tipo de veículo."""
    return (df_long.groupby("Descrição", as_index=False)["Valor"]
            .sum().sort_values("Valor", ascending=True))

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
  {'🔵' if secao=='VISITANTE' else '🟢'}&nbsp; Veículos {LABEL_SECAO}s
  &nbsp;·&nbsp; {metrica}
</span>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
total_geral   = df_long["Valor"].sum()
por_mes       = df_long.groupby("Mês")["Valor"].sum()
mes_destaque  = por_mes.idxmax() if not por_mes.empty else "—"
val_destaque  = por_mes.max()    if not por_mes.empty else 0
n_tipos       = df_sec["DESC_CURTA"].nunique()

if st.session_state.acumulado:
    kpi4_val = f"{total_geral:,.0f}".replace(",",".")
    kpi4_lab = "Total acumulado (todos os meses)"
else:
    val_mes = df_long[df_long["Mês"] == st.session_state.mes_ativo]["Valor"].sum()
    kpi4_val = f"{val_mes:,.0f}".replace(",",".")
    kpi4_lab = f"Volume — {ABREV.get(st.session_state.mes_ativo,'')}"

c1, c2, c3, c4 = st.columns(4)
for col, val, lab in [
    (c1, f"{total_geral:,.0f}".replace(",","."),  f"Total acumulado — {metrica}"),
    (c2, ABREV.get(mes_destaque, mes_destaque),    "Mês com maior volume"),
    (c3, f"{val_destaque:,.0f}".replace(",","."),  "Volume no mês destaque"),
    (c4, kpi4_val, kpi4_lab),
]:
    col.markdown(f"""
    <div class='kpi-card'>
      <div class='kpi-val'>{val}</div>
      <div class='kpi-lab'>{lab}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Título + botão acumulado + pills de meses ──────────────────────────────────
st.markdown(f"<h3 style='color:{T['text_primary']};margin-bottom:4px'>📅 Veículos por tipo</h3>",
            unsafe_allow_html=True)
st.markdown(
    f"<p style='color:{T['text_secondary']};font-size:.84rem;margin-top:0;margin-bottom:10px'>"
    "Selecione o mês ou visualize o acumulado do período</p>",
    unsafe_allow_html=True,
)

# Linha de controles: [Acumulado] [Jan] [Fev] ... [Dez]
acum_label = "📊 Acumulado ✓" if st.session_state.acumulado else "📊 Acumulado"
all_buttons = [acum_label] + [ABREV.get(m, m) for m in MESES]
cols_ctrl   = st.columns([1.4] + [1] * len(MESES))

# Botão Acumulado
with cols_ctrl[0]:
    is_acum = st.session_state.acumulado
    if is_acum:
        st.markdown(f"""
        <div style="text-align:center;padding:7px 4px;border-radius:999px;
          background:{COR_SECAO};color:white;font-size:.72rem;font-weight:700;
          border:2px solid {COR_SECAO};user-select:none">📊 Acumulado</div>
        """, unsafe_allow_html=True)
    else:
        if st.button("📊 Acumulado", key="btn_acum", use_container_width=True):
            st.session_state.acumulado = True
            st.rerun()

# Pills de meses
for i, mes in enumerate(MESES):
    abrev    = ABREV.get(mes, mes)
    is_active = (not st.session_state.acumulado) and (mes == st.session_state.mes_ativo)
    with cols_ctrl[i + 1]:
        if is_active:
            st.markdown(f"""
            <div style="text-align:center;padding:7px 2px;border-radius:999px;
              background:{COR_SECAO};color:white;font-size:.72rem;font-weight:700;
              border:2px solid {COR_SECAO};user-select:none">{abrev}</div>
            """, unsafe_allow_html=True)
        else:
            if st.button(abrev, key=f"pill_{mes}", use_container_width=True):
                st.session_state.mes_ativo = mes
                st.session_state.acumulado = False
                st.rerun()

st.markdown("<br style='margin:0'>", unsafe_allow_html=True)

# ── Dados do gráfico ──────────────────────────────────────────────────────────
if st.session_state.acumulado:
    df_grafico   = get_acumulado_df()
    titulo_grafico = f"Acumulado 2026 — {metrica_label}"
else:
    df_grafico   = get_mes_df(st.session_state.mes_ativo)
    titulo_grafico = f"{st.session_state.mes_ativo} — {metrica_label}"

cores_barra = [COR_SECAO if v > 0 else T["zero_bar"] for v in df_grafico["Valor"]]

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
    marker=dict(color=cores_barra, line=dict(width=0), opacity=0.92),
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

fig.update_layout(
    transition=dict(duration=550, easing="cubic-in-out", ordering="traces first"),
    title=dict(text=titulo_grafico, font=dict(size=13, color=T["text_secondary"]),
               x=0, xanchor="left", pad=dict(b=10)),
    plot_bgcolor=T["chart_bg"],
    paper_bgcolor=T["chart_bg"],
    font=dict(family="Arial", size=12, color=T["text_secondary"]),
    xaxis=dict(
        gridcolor=T["chart_grid"], zeroline=False, showline=False,
        tickfont=dict(size=11, color=T["text_muted"]),
        title=dict(text=metrica_label, font=dict(size=12, color=T["text_muted"])),
    ),
    yaxis=dict(
        gridcolor="rgba(0,0,0,0)",
        tickfont=dict(size=11, color=T["text_primary"]),
        automargin=True,
    ),
    margin=dict(t=40, b=16, l=10, r=100),
    height=max(420, len(df_grafico) * 36),
    bargap=0.28, hoverdistance=20,
)

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True,
                config={"displayModeBar": False}, key="chart_main")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabela detalhada (HTML para controle total do tema) ────────────────────────
st.markdown(f"<h3 style='color:{T['text_primary']}'>📋 Tabela detalhada</h3>",
            unsafe_allow_html=True)

# Monta pivot com dados reais
tab_pivot = df_long.pivot_table(
    index="Descrição", columns="Mês", values="Valor", aggfunc="sum"
).fillna(0)
tab_pivot = tab_pivot.reindex(columns=[m for m in MESES if m in tab_pivot.columns])
tab_pivot["TOTAL"] = tab_pivot.sum(axis=1)
tab_pivot = tab_pivot.sort_values("TOTAL", ascending=False)

# Cabeçalhos abreviados
tab_cols_display = [ABREV.get(c, c) for c in tab_pivot.columns[:-1]] + ["TOTAL"]

# Renderiza como HTML para respeitar o tema escuro/claro
def fmt(v):
    try:
        return f"{int(float(v)):,}".replace(",",".")
    except:
        return str(v)

rows_html = ""
for idx, (desc, row) in enumerate(tab_pivot.iterrows()):
    bg = T["tbl_row_alt"] if idx % 2 == 0 else T["tbl_bg"]
    cells = ""
    for ci, val in enumerate(row):
        bold = " font-weight:700;" if ci == len(row)-1 else ""
        color = COR_SECAO if (ci == len(row)-1 and val > 0) else T["tbl_txt"]
        cells += (f"<td style='padding:7px 12px;border-bottom:1px solid {T['tbl_border']};"
                  f"color:{color};{bold}text-align:right'>{fmt(val)}</td>")
    rows_html += (f"<tr style='background:{bg}'>"
                  f"<td style='padding:7px 12px;border-bottom:1px solid {T['tbl_border']};"
                  f"color:{T['tbl_txt']};font-size:.82rem'>{desc}</td>"
                  f"{cells}</tr>")

header_cells = "".join(
    f"<th style='padding:8px 12px;text-align:right;color:{T['tbl_head_txt']};"
    f"font-size:.75rem;font-weight:600;letter-spacing:.05em;white-space:nowrap'>{h}</th>"
    for h in tab_cols_display
)

table_html = f"""
<div style="overflow-x:auto;border-radius:12px;border:1px solid {T['tbl_border']};
            margin-bottom:12px;max-height:420px;overflow-y:auto">
  <table style="width:100%;border-collapse:collapse;background:{T['tbl_bg']};
                font-family:Arial,sans-serif;font-size:.82rem">
    <thead style="position:sticky;top:0;z-index:2">
      <tr style="background:{T['tbl_head_bg']}">
        <th style="padding:8px 12px;text-align:left;color:{T['tbl_head_txt']};
                   font-size:.75rem;font-weight:600;letter-spacing:.05em">TIPO DE VEÍCULO</th>
        {header_cells}
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>
"""
st.markdown(table_html, unsafe_allow_html=True)

# ── Download ──────────────────────────────────────────────────────────────────
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