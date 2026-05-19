import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# ── Página ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Balsa Delfinópolis 2026",
    page_icon="⛴️",
    layout="wide",
    initial_sidebar_state="expanded",
)

COR_VISITANTE = "#2E75B6"
COR_LOCAL     = "#70AD47"

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #F0F4F8; }
[data-testid="stSidebar"]          { background: #1F4E79; }
[data-testid="stSidebar"] *        { color: #FFFFFF !important; }
[data-testid="stSidebar"] .stRadio label { color: #FFFFFF !important; }
h1, h2, h3 { color: #1F4E79; }
.metric-card {
    background: white; border-radius: 12px; padding: 18px 22px;
    box-shadow: 0 2px 8px rgba(0,0,0,.08); text-align: center;
}
.metric-val { font-size: 2rem; font-weight: 700; color: #1F4E79; }
.metric-lab { font-size: .82rem; color: #777; margin-top: 4px; }
.section-badge {
    display: inline-block; padding: 4px 16px; border-radius: 20px;
    font-weight: 600; font-size: .9rem; margin-bottom: 14px;
}
.chart-card {
    background: white; border-radius: 14px;
    padding: 24px 20px 12px; box-shadow: 0 2px 10px rgba(0,0,0,.07);
}
/* remove bordas dos botões pill */
div[data-testid="stHorizontalBlock"] button {
    border-radius: 999px !important;
    border: 1.5px solid #CBD5E1 !important;
    background: white !important;
    color: #475569 !important;
    font-size: .78rem !important;
    font-weight: 500 !important;
    padding: 4px 6px !important;
    transition: all .15s !important;
}
div[data-testid="stHorizontalBlock"] button:hover {
    border-color: #94A3B8 !important;
    background: #F1F5F9 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Carrega dados ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data(path: str):
    raw = pd.read_csv(path, sep=";", header=None, encoding="utf-8-sig", dtype=str)
    month_row = raw.iloc[0].fillna("").tolist()
    sub_row   = raw.iloc[1].fillna("").tolist()

    current_month = ""
    col_map = {}
    for i, (m, s) in enumerate(zip(month_row, sub_row)):
        if m.strip():
            current_month = m.strip()
        if s.strip() and i > 0:
            col_map[i] = (current_month, s.strip())

    data_rows = raw.iloc[2:].reset_index(drop=True)
    records = []
    current_section = ""
    for _, row in data_rows.iterrows():
        desc = str(row.iloc[0]).strip()
        if not desc or desc == "nan": continue
        if "VEÍCULOS VISITANTES" in desc: current_section = "VISITANTE"; continue
        if "VEÍCULOS LOCAIS"     in desc: current_section = "LOCAL";     continue
        if desc.startswith("TOTAL"):      continue

        record = {"DESCRIÇÃO": desc, "SEÇÃO": current_section}
        for ci, (month, sub) in col_map.items():
            val_str = str(row.iloc[ci]).replace(".", "").replace(",", ".").strip()
            try:    record[(month, sub)] = float(val_str)
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
    meses_disponiveis = [m for m in mes_ordem if m in {k[0] for k in col_map.values()}]
    return df, meses_disponiveis

CSV_PATH = "Relatório_Balsa_Delfs_2026.csv"
df_all, MESES = load_data(CSV_PATH)

ABREV = {
    "Janeiro 2026":"Jan","Fevereiro 2026":"Fev","Março 2026":"Mar",
    "Abril 2026":"Abr","Maio 2026":"Mai","Junho 2026":"Jun",
    "Julho 2026":"Jul","Agosto 2026":"Ago","Setembro 2026":"Set",
    "Outubro 2026":"Out","Novembro 2026":"Nov","Dezembro 2026":"Dez",
    "Feriados Abril 2026":"Fer.Abr","Feriados Maio 2026":"Fer.Mai",
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Bandeira via HTML com URL encoded (corrige erro de encoding do st.image)
    st.markdown("""
    <div style="text-align:center;margin-bottom:12px">
      <img
        src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Bandeira_de_Delfin%C3%B3polis.png/200px-Bandeira_de_Delfin%C3%B3polis.png"
        style="width:90%;border-radius:8px;border:2px solid rgba(255,255,255,.3)"
        onerror="this.outerHTML='<p style=font-size:2.5rem;margin:0>🏳️</p>'"
      >
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
    st.markdown("<small style='opacity:.65'>Dados: Relatório Balsa Delfs 2026</small>",
                unsafe_allow_html=True)

# ── Estado: mês ativo ─────────────────────────────────────────────────────────
if "mes_ativo" not in st.session_state or st.session_state.mes_ativo not in MESES:
    st.session_state.mes_ativo = MESES[0]

COR_SECAO   = COR_VISITANTE if secao == "VISITANTE" else COR_LOCAL
LABEL_SECAO = "Visitante"   if secao == "VISITANTE" else "Local"

# ── Dados aggregados ──────────────────────────────────────────────────────────
df_sec = df_all[df_all["SEÇÃO"] == secao].copy()

long_rows = []
for mes in MESES:
    col = (mes, metrica)
    if col in df_sec.columns:
        tmp = df_sec[["DESC_CURTA", col]].copy()
        tmp.columns = ["Descrição", "Valor"]
        tmp["Mês"] = mes
        long_rows.append(tmp)
df_long = pd.concat(long_rows, ignore_index=True) if long_rows else pd.DataFrame(columns=["Descrição","Valor","Mês"])

def get_mes_df(mes):
    col = (mes, metrica)
    if col not in df_sec.columns:
        return pd.DataFrame(columns=["Descrição","Valor"])
    tmp = df_sec[["DESC_CURTA", col]].copy()
    tmp.columns = ["Descrição","Valor"]
    return tmp.sort_values("Valor", ascending=True)

# ── Cabeçalho ─────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='margin-bottom:0'>⛴️ Balsa Delfinópolis — 2026</h1>
<p style='color:#64748B;margin-top:4px;font-size:.95rem'>
  Tráfego de veículos e estimativa de passageiros
</p>
""", unsafe_allow_html=True)

st.markdown(f"""
<span class='section-badge'
  style='background:{COR_SECAO}18;color:{COR_SECAO};border:1.5px solid {COR_SECAO}'>
  {'🔵' if secao=='VISITANTE' else '🟢'}&nbsp; Veículos {LABEL_SECAO}s
  &nbsp;·&nbsp; {metrica}
</span>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
total_geral  = df_long["Valor"].sum()
por_mes      = df_long.groupby("Mês")["Valor"].sum()
mes_destaque = por_mes.idxmax() if not por_mes.empty else "—"
val_destaque = por_mes.max()    if not por_mes.empty else 0
n_tipos      = df_sec["DESC_CURTA"].nunique()
val_mes_ativo = df_long[df_long["Mês"] == st.session_state.mes_ativo]["Valor"].sum()

c1, c2, c3, c4 = st.columns(4)
for col, val, lab in [
    (c1, f"{total_geral:,.0f}".replace(",","."),  f"Total acumulado — {metrica}"),
    (c2, ABREV.get(mes_destaque, mes_destaque),    "Mês com maior volume"),
    (c3, f"{val_destaque:,.0f}".replace(",","."),  "Volume no mês destaque"),
    (c4, f"{val_mes_ativo:,.0f}".replace(",","."), f"Volume — {ABREV.get(st.session_state.mes_ativo,'')}"),
]:
    col.markdown(f"""
    <div class='metric-card'>
      <div class='metric-val'>{val}</div>
      <div class='metric-lab'>{lab}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Título da seção + pills dos meses ────────────────────────────────────────
st.markdown("### 📅 Veículos por tipo de veículo")
st.markdown(
    "<p style='color:#64748B;font-size:.85rem;margin-top:-10px;margin-bottom:4px'>"
    "Selecione o mês para atualizar o gráfico</p>",
    unsafe_allow_html=True,
)

cols_pill = st.columns(len(MESES))
for i, mes in enumerate(MESES):
    abrev = ABREV.get(mes, mes)
    is_active = (mes == st.session_state.mes_ativo)
    with cols_pill[i]:
        if is_active:
            # Pill ativo: renderiza como badge estático (não é clicável)
            st.markdown(f"""
            <div style="
              text-align:center; padding:7px 2px; border-radius:999px;
              background:{COR_SECAO}; color:white; font-size:.75rem;
              font-weight:700; border:2px solid {COR_SECAO};
              line-height:1.2; margin-bottom:2px
            ">{abrev}</div>
            """, unsafe_allow_html=True)
        else:
            if st.button(abrev, key=f"pill_{mes}", use_container_width=True):
                st.session_state.mes_ativo = mes
                st.rerun()

st.markdown("<br style='margin:0'>", unsafe_allow_html=True)

# ── Gráfico de barras horizontal ─────────────────────────────────────────────
df_grafico    = get_mes_df(st.session_state.mes_ativo)
metrica_label = "Quantidade de Veículos" if metrica == "QTD" else "Estimativa de Passageiros"

cores_barra = [COR_SECAO if v > 0 else "#E2E8F0" for v in df_grafico["Valor"]]

# Hover no estilo "education dashboard":
# linha 1 → nome em negrito | linha 2 → rótulo da métrica (cinza) | linha 3 → valor em destaque
hover_tpl = (
    "<b style='font-size:13px;color:#1E293B'>%{y}</b><br>"
    f"<span style='font-size:11px;color:#64748B'>{metrica_label}</span><br>"
    f"<b style='font-size:18px;color:{COR_SECAO}'>%{{x:,.0f}}</b>"
    "<extra></extra>"
)

fig = go.Figure()
fig.add_trace(go.Bar(
    x=df_grafico["Valor"],
    y=df_grafico["Descrição"],
    orientation="h",
    marker=dict(color=cores_barra, line=dict(width=0)),
    text=df_grafico["Valor"].apply(
        lambda v: f"{int(v):,}".replace(",",".") if v > 0 else ""
    ),
    textposition="outside",
    textfont=dict(size=11, color="#334155"),
    hovertemplate=hover_tpl,
    hoverlabel=dict(
        bgcolor="white",
        bordercolor=COR_SECAO,
        font=dict(family="Arial", size=12, color="#1E293B"),
        namelength=0,
    ),
    cliponaxis=False,
))

fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family="Arial", size=12, color="#334155"),
    xaxis=dict(
        gridcolor="#F1F5F9",
        zeroline=False,
        showline=False,
        tickfont=dict(size=11, color="#94A3B8"),
        title=dict(text=metrica_label, font=dict(size=12, color="#94A3B8")),
    ),
    yaxis=dict(
        gridcolor="rgba(0,0,0,0)",
        tickfont=dict(size=11, color="#334155"),
        automargin=True,
    ),
    margin=dict(t=16, b=16, l=10, r=90),
    height=max(400, len(df_grafico) * 36),
    bargap=0.30,
    hoverdistance=20,
)

st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabela detalhada ──────────────────────────────────────────────────────────
st.markdown("### 📋 Tabela detalhada")

tab_pivot = df_long.pivot_table(
    index="Descrição", columns="Mês", values="Valor", aggfunc="sum"
).fillna(0)
tab_pivot = tab_pivot.reindex(columns=[m for m in MESES if m in tab_pivot.columns])
tab_pivot["TOTAL"] = tab_pivot.sum(axis=1)
tab_pivot = tab_pivot.sort_values("TOTAL", ascending=False)

tab_fmt = tab_pivot.copy()
for c in tab_fmt.columns:
    tab_fmt[c] = tab_fmt[c].apply(lambda v: f"{int(v):,}".replace(",","."))

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
    "<small style='color:#94A3B8'>Dados: Relatório Balsa Delfs 2026 · "
    "Município de Delfinópolis – MG</small>",
    unsafe_allow_html=True,
)