import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

# ── Página ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Balsa Delfinópolis 2026",
    page_icon="⛴️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paleta ───────────────────────────────────────────────────────────────────
COR_VISITANTE = "#2E75B6"
COR_LOCAL     = "#70AD47"
COR_FUNDO     = "#F0F4F8"

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #F0F4F8; }
[data-testid="stSidebar"]          { background: #1F4E79; }
[data-testid="stSidebar"] * { color: #FFFFFF !important; }
[data-testid="stSidebar"] .stRadio label { color: #FFFFFF !important; }
h1,h2,h3 { color: #1F4E79; }
.metric-card {
    background: white; border-radius: 12px; padding: 18px 22px;
    box-shadow: 0 2px 8px rgba(0,0,0,.08); text-align: center;
}
.metric-val  { font-size: 2rem; font-weight: 700; color: #1F4E79; }
.metric-lab  { font-size: .85rem; color: #666; margin-top: 4px; }
.section-badge {
    display:inline-block; padding:4px 14px; border-radius:20px;
    font-weight:600; font-size:.9rem; margin-bottom:12px;
}
</style>
""", unsafe_allow_html=True)

# ── Carrega & processa dados ──────────────────────────────────────────────────
@st.cache_data
def load_data(path: str):
    raw = pd.read_csv(path, sep=";", header=None, encoding="utf-8-sig", dtype=str)

    # Linha 0 → nomes dos meses; Linha 1 → sub-headers (QTD / Nº PAS / EST)
    month_row = raw.iloc[0].fillna("").tolist()
    sub_row   = raw.iloc[1].fillna("").tolist()

    # Monta mapeamento coluna → (mês, sub-header)
    current_month = ""
    col_map = {}          # col_index → (month_label, sub_label)
    for i, (m, s) in enumerate(zip(month_row, sub_row)):
        if m.strip():
            current_month = m.strip()
        if s.strip() and i > 0:
            col_map[i] = (current_month, s.strip())

    # Dados a partir da linha 2
    data_rows = raw.iloc[2:].reset_index(drop=True)

    # Identifica seção (VISITANTE / LOCAL) e filtra linhas úteis
    records = []
    current_section = ""
    for _, row in data_rows.iterrows():
        desc = str(row.iloc[0]).strip()
        if not desc or desc == "nan":
            continue
        if "VEÍCULOS VISITANTES" in desc:
            current_section = "VISITANTE"
            continue
        if "VEÍCULOS LOCAIS" in desc:
            current_section = "LOCAL"
            continue
        if desc.startswith("TOTAL"):
            continue

        record = {"DESCRIÇÃO": desc, "SEÇÃO": current_section}
        for ci, (month, sub) in col_map.items():
            val_str = str(row.iloc[ci]).replace(".", "").replace(",", ".").strip()
            try:
                record[(month, sub)] = float(val_str)
            except ValueError:
                record[(month, sub)] = 0.0
        records.append(record)

    df = pd.DataFrame(records)

    # Simplifica descrição (remove sufixo VISITANTE/LOCAL)
    df["DESC_CURTA"] = (
        df["DESCRIÇÃO"]
        .str.replace(r"\s+VISITANTE$", "", regex=True)
        .str.replace(r"\s+LOCAL$", "", regex=True)
        .str.strip()
    )

    # Meses na ordem correta
    mes_ordem = [
        "Janeiro 2026","Fevereiro 2026","Março 2026","Abril 2026",
        "Maio 2026","Junho 2026","Julho 2026","Agosto 2026",
        "Setembro 2026","Outubro 2026","Novembro 2026","Dezembro 2026",
        "Feriados Abril 2026","Feriados Maio 2026",
    ]
    meses_disponiveis = [m for m in mes_ordem if m in {k[0] for k in col_map.values()}]
    return df, meses_disponiveis

CSV_PATH = "/mnt/user-data/uploads/Relatório_Balsa_Delfs_2026_csv.csv"
df_all, MESES = load_data(CSV_PATH)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Bandeira_de_Delfinópolis.png/200px-Bandeira_de_Delfinópolis.png",
             use_container_width=True)
    st.markdown("## ⛴️ Balsa Delfinópolis")
    st.markdown("**Relatório de Tráfego — 2026**")
    st.markdown("---")

    # Toggle LOCAL × VISITANTE
    secao = st.radio(
        "**Tipo de veículo**",
        ["VISITANTE", "LOCAL"],
        format_func=lambda x: f"🔵 Visitante" if x == "VISITANTE" else "🟢 Local",
        horizontal=False,
    )

    st.markdown("---")
    metrica = st.radio(
        "**Métrica exibida**",
        ["QTD", "EST PASSAGEIROS"],
        format_func=lambda x: "🚗 Quantidade de veículos" if x == "QTD" else "👥 Estimativa de passageiros",
    )

    st.markdown("---")
    meses_sel = st.multiselect(
        "**Filtrar meses**",
        options=MESES,
        default=MESES,
    )

    st.markdown("---")
    st.markdown("<small>Dados: Relatório Balsa Delfs 2026</small>", unsafe_allow_html=True)

# ── Filtra dados ──────────────────────────────────────────────────────────────
COR_SECAO = COR_VISITANTE if secao == "VISITANTE" else COR_LOCAL
LABEL_SECAO = "Visitante" if secao == "VISITANTE" else "Local"

df_sec = df_all[df_all["SEÇÃO"] == secao].copy()

# Monta dataframe long apenas com meses selecionados e métrica escolhida
long_rows = []
for mes in meses_sel:
    col = (mes, metrica)
    if col in df_sec.columns:
        tmp = df_sec[["DESC_CURTA", col]].copy()
        tmp.columns = ["Descrição", "Valor"]
        tmp["Mês"] = mes
        long_rows.append(tmp)

df_long = pd.concat(long_rows, ignore_index=True) if long_rows else pd.DataFrame(columns=["Descrição","Valor","Mês"])

# ── Cabeçalho ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<h1 style='margin-bottom:0'>⛴️ Balsa Delfinópolis — 2026</h1>
<p style='color:#555;margin-top:4px'>Tráfego de veículos e estimativa de passageiros</p>
""", unsafe_allow_html=True)

badge_color = COR_VISITANTE if secao == "VISITANTE" else COR_LOCAL
st.markdown(f"""
<span class='section-badge' style='background:{badge_color}22;color:{badge_color};border:1.5px solid {badge_color}'>
  {'🔵' if secao=='VISITANTE' else '🟢'} Exibindo: veículos {LABEL_SECAO}s &nbsp;|&nbsp; {metrica}
</span>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
st.markdown("### 📊 Resumo do período selecionado")

total_geral   = df_long["Valor"].sum()
mes_destaque  = df_long.groupby("Mês")["Valor"].sum().idxmax() if not df_long.empty else "—"
val_destaque  = df_long.groupby("Mês")["Valor"].sum().max()   if not df_long.empty else 0
tipo_destaque = df_long.groupby("Descrição")["Valor"].sum().idxmax() if not df_long.empty else "—"
n_tipos       = df_sec["DESC_CURTA"].nunique()

col1, col2, col3, col4 = st.columns(4)
for col, val, lab in [
    (col1, f"{total_geral:,.0f}".replace(",","."       ), f"Total — {metrica}"),
    (col2, mes_destaque,                                   "Mês com maior volume"),
    (col3, f"{val_destaque:,.0f}".replace(",","."),         f"Volume no mês destaque"),
    (col4, str(n_tipos),                                   "Tipos de veículo"),
]:
    col.markdown(f"""
    <div class='metric-card'>
      <div class='metric-val'>{val}</div>
      <div class='metric-lab'>{lab}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Gráfico 1: Total por mês (barras) ─────────────────────────────────────────
st.markdown("### 📅 Total por mês")

tot_mes = df_long.groupby("Mês")["Valor"].sum().reindex(meses_sel).fillna(0).reset_index()
tot_mes.columns = ["Mês","Valor"]

fig_bar = px.bar(
    tot_mes, x="Mês", y="Valor",
    color_discrete_sequence=[COR_SECAO],
    text_auto=".3s",
    labels={"Valor": metrica, "Mês": ""},
)
fig_bar.update_traces(textposition="outside", textfont_size=11)
fig_bar.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Arial", size=12),
    xaxis=dict(tickangle=-35),
    yaxis=dict(gridcolor="#eee"),
    margin=dict(t=30, b=10),
    height=380,
)
st.plotly_chart(fig_bar, use_container_width=True)

# ── Gráfico 2: Heatmap tipo × mês ────────────────────────────────────────────
st.markdown("### 🔥 Intensidade por tipo de veículo e mês")

pivot = df_long.pivot_table(index="Descrição", columns="Mês", values="Valor", aggfunc="sum").fillna(0)
pivot = pivot.reindex(columns=[m for m in meses_sel if m in pivot.columns])
pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]

fig_heat = px.imshow(
    pivot,
    color_continuous_scale=["#EBF3FB","#2E75B6" if secao=="VISITANTE" else "#375623"],
    aspect="auto",
    labels=dict(color=metrica),
    text_auto=".3s",
)
fig_heat.update_layout(
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Arial", size=11),
    margin=dict(t=30, b=10),
    height=520,
    coloraxis_showscale=True,
    xaxis=dict(tickangle=-35),
)
fig_heat.update_traces(textfont_size=9)
st.plotly_chart(fig_heat, use_container_width=True)

# ── Gráfico 3: Composição por tipo — pizza + barras empilhadas ────────────────
col_pizza, col_stack = st.columns([1, 2])

with col_pizza:
    st.markdown("### 🥧 Composição por tipo")
    tot_tipo = df_long.groupby("Descrição")["Valor"].sum().sort_values(ascending=False)
    # Top 8 + "Outros"
    top8 = tot_tipo.head(8)
    outros = tot_tipo.iloc[8:].sum()
    if outros > 0:
        top8 = pd.concat([top8, pd.Series({"Outros": outros})])

    fig_pie = px.pie(
        values=top8.values, names=top8.index,
        color_discrete_sequence=px.colors.sequential.Blues_r if secao=="VISITANTE"
                                else px.colors.sequential.Greens_r,
        hole=0.38,
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label", textfont_size=10)
    fig_pie.update_layout(
        showlegend=False, margin=dict(t=20,b=0,l=0,r=0),
        paper_bgcolor="white", height=420,
        font=dict(family="Arial"),
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_stack:
    st.markdown("### 📊 Evolução mensal por tipo")
    top_tipos = (
        df_long.groupby("Descrição")["Valor"].sum()
        .sort_values(ascending=False).head(8).index.tolist()
    )
    df_top = df_long[df_long["Descrição"].isin(top_tipos)]
    df_stack = df_top.pivot_table(index="Mês", columns="Descrição", values="Valor", aggfunc="sum").fillna(0)
    df_stack = df_stack.reindex([m for m in meses_sel if m in df_stack.index])

    cores = (px.colors.sequential.Blues_r if secao=="VISITANTE"
             else px.colors.sequential.Greens_r)[:len(top_tipos)]

    fig_stack = go.Figure()
    for tipo, cor in zip(top_tipos, cores):
        if tipo in df_stack.columns:
            fig_stack.add_trace(go.Bar(
                name=tipo, x=df_stack.index, y=df_stack[tipo],
                marker_color=cor, hovertemplate="%{y:,.0f}<extra>%{fullData.name}</extra>"
            ))
    fig_stack.update_layout(
        barmode="stack", plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Arial", size=11),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font_size=9),
        xaxis=dict(tickangle=-35, gridcolor="#eee"),
        yaxis=dict(gridcolor="#eee", title=metrica),
        margin=dict(t=60, b=10),
        height=420,
    )
    st.plotly_chart(fig_stack, use_container_width=True)

# ── Tabela detalhada ──────────────────────────────────────────────────────────
st.markdown("### 📋 Tabela detalhada")

tab_pivot = df_long.pivot_table(index="Descrição", columns="Mês", values="Valor", aggfunc="sum").fillna(0)
tab_pivot = tab_pivot.reindex(columns=[m for m in meses_sel if m in tab_pivot.columns])
tab_pivot["TOTAL"] = tab_pivot.sum(axis=1)
tab_pivot = tab_pivot.sort_values("TOTAL", ascending=False)

# Formata números
tab_fmt = tab_pivot.copy()
for c in tab_fmt.columns:
    tab_fmt[c] = tab_fmt[c].apply(lambda v: f"{v:,.0f}".replace(",","."))

st.dataframe(tab_fmt, use_container_width=True, height=420)

# ── Download ──────────────────────────────────────────────────────────────────
buf = io.BytesIO()
tab_pivot.to_excel(buf, index=True)
st.download_button(
    label="⬇️ Exportar tabela (.xlsx)",
    data=buf.getvalue(),
    file_name=f"balsa_delfinopolis_{secao.lower()}_{metrica.replace(' ','_')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.markdown("---")
st.markdown(
    "<small style='color:#aaa'>Dados: Relatório Balsa Delfs 2026 · "
    "Município de Delfinópolis – MG</small>",
    unsafe_allow_html=True
)