import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go


# ============================================================
# FUNÇÃO: Ajustar Datas Operacionais
# ============================================================
def gerar_ordem_horas(hora_inicio, hora_fim):
    h_ini = hora_inicio.hour
    h_fim = hora_fim.hour

    if h_ini <= h_fim:
        # Intervalo simples (ex: 13 → 20)
        return list(range(h_ini, h_fim + 1))
    else:
        # Intervalo passando da meia-noite (ex: 19 → 05)
        return list(range(h_ini, 24)) + list(range(0, h_fim + 1))

def ajustar_data_operacional(df, coluna_datahora, hora_inicio, hora_fim):
    df[coluna_datahora] = pd.to_datetime(
        df[coluna_datahora],
        format="mixed",
        dayfirst=True,
        errors="coerce"
    )

    # Caso o intervalo atravesse a meia-noite (ex: 19 → 05)
    atravessa_meia_noite = hora_inicio > hora_fim

    if atravessa_meia_noite:
        # exemplo: 19:00 até 05:00
        df_filtrado = df[
            (df[coluna_datahora].dt.time >= hora_inicio) |
            (df[coluna_datahora].dt.time <= hora_fim)
        ].copy()
    else:
        # exemplo: 13:00 até 20:00
        df_filtrado = df[
            (df[coluna_datahora].dt.time >= hora_inicio) &
            (df[coluna_datahora].dt.time <= hora_fim)
        ].copy()

    # Criar data operacional
    df_filtrado["Data Operacional"] = df_filtrado[coluna_datahora].apply(
        lambda x: x.date() if x.time() >= hora_inicio else (x - pd.Timedelta(days=1)).date()
    )

    return df_filtrado



# ============================================================
# UPLOAD DE ARQUIVOS
# ============================================================
st.sidebar.header("📁 Upload de Arquivos")

arquivo_geral = st.sidebar.file_uploader("Carregar geral_pedidos.csv", type=["csv"])
arquivo_order = st.sidebar.file_uploader("Carregar order_start.csv", type=["csv"])

if arquivo_geral is None:
    st.warning("Envie o arquivo geral_pedidos.csv para continuar.")
    st.stop()
if arquivo_order is None:
    st.warning("Envie o arquivo order_start.csv para continuar.")
    st.stop()

st.sidebar.subheader("⏱ Filtro de Horário")

horas = [f"{h:02d}:00" for h in range(24)]

hora_inicio_str = st.sidebar.selectbox("Hora Inicial", horas, index=19)  # default 19:00
hora_fim_str    = st.sidebar.selectbox("Hora Final", horas, index=5)     # default 05:00

hora_inicio = pd.to_datetime(hora_inicio_str).time()
hora_fim    = pd.to_datetime(hora_fim_str).time()

df = pd.read_csv(arquivo_geral, sep=";", on_bad_lines="skip", engine="python")
order_start = pd.read_csv(arquivo_order, sep=";", on_bad_lines="skip", engine="python")


# ============================================================
# AJUSTAR DATAS OPERACIONAIS
# ============================================================
df = ajustar_data_operacional(df, 'Data Início', hora_inicio, hora_fim)

remover_primeiro_dia = st.sidebar.checkbox(
    "Remover o primeiro dia operacional",
    value=True
)

if remover_primeiro_dia:
    primeiro_dia = df["Data Operacional"].min()
    df = df[df["Data Operacional"] != primeiro_dia]


# ============================================================
# CONFIGURAÇÕES INICIAIS
# ============================================================
st.set_page_config(page_title="Acompanhamento MFC", layout="wide")
st.title("Resumo MFC")

df_apanhas = df.drop_duplicates(subset=['Cod. SKU', 'Num. Pedido']).copy()


# ============================================================
# CARDS RESUMO
# ============================================================
total_apanhas = len(df_apanhas)
apanhas_realizadas = df_apanhas["Situação"].value_counts().get("F", 0)
apanhas_pendentes = total_apanhas - apanhas_realizadas
total_caixas = df['Num. Picking'].nunique()


def status_picking(s):
    if all(x == "F" for x in s):
        return "F"
    elif all(x == "I" for x in s):
        return "I"
    return "P"


df_status = df.groupby("Num. Picking")["Situação"].apply(status_picking).reset_index()
status_counts = df_status["Situação"].value_counts()

caixas_pendentes = status_counts.get("P", 0)
pendentes_inducao = status_counts.get("I", 0)


def card(title, value, icon, color):
    return f"""
    <div style="
        background-color:{color};
        padding:15px;
        border-radius:12px;
        text-align:center;
        color:white;
        font-weight:bold;
        font-size:16px;
        box-shadow:2px 2px 8px rgba(0,0,0,0.2);
        margin:5px;">
        <div style="font-size:25px">{icon}</div>
        <div>{title}</div>
        <div style="font-size:20px">{value}</div>
    </div>
    """


cols = st.columns(5)
cols[0].markdown(card("Total de Apanhas", total_apanhas, "🛒", "#1E88E5"), unsafe_allow_html=True)
cols[1].markdown(card("Apanhas Realizadas", apanhas_realizadas, "✅", "#43A047"), unsafe_allow_html=True)
cols[2].markdown(card("Total de Volumes", total_caixas, "📦", "#8E24AA"), unsafe_allow_html=True)
cols[3].markdown(card("Volumes Pendentes", caixas_pendentes, "⚠️", "#CEA903"), unsafe_allow_html=True)
cols[4].markdown(card("Volumes p/ Indução", pendentes_inducao, "⏳", "#F4511E"), unsafe_allow_html=True)


# ============================================================
# EFICIÊNCIA BALANÇA
# ============================================================
col_ef = df[['Situação', 'Situação Conferência', 'Num. Picking',
             'Usuário Conferência', 'Usuário Operador']].copy()

ef = df[(col_ef['Situação'] == 'F') & (col_ef['Situação Conferência'] == 'F')] \
    .drop_duplicates(subset='Num. Picking')

balanca = ef[ef["Usuário Conferência"] == "CHECK_WEIGHT"]
reconf = ef[ef["Usuário Conferência"] != "CHECK_WEIGHT"]

total_bal = len(balanca)
total_reconf = len(reconf)
total = total_bal + total_reconf

perc_bal = (total_bal / total) * 100 if total > 0 else 0
perc_reconf = (total_reconf / total) * 100 if total > 0 else 0


# ============================================================
# ORDER START — PRODUTIVIDADE POR HORA
# ============================================================
ordem = gerar_ordem_horas(hora_inicio, hora_fim)

order_start["Hora Inducao"] = pd.to_datetime(order_start["Hora Inducao"], errors="coerce")
order_start["HORA"] = order_start["Hora Inducao"].dt.hour

order_start["HORA"] = pd.Categorical(order_start["HORA"], categories=ordem, ordered=True)
order_start = order_start.sort_values("HORA")

order_start["HORA"] = order_start["HORA"].apply(lambda x: f"{int(x):02d}:00" if pd.notna(x) else None)


# ============================================================
# APANHAS FINALIZADAS POR HORA
# ============================================================
df_finalizado = df_apanhas[df_apanhas['Situação'] == 'F'].copy()
df_finalizado["Data Finalização"] = pd.to_datetime(df_finalizado["Data Finalização"], errors="coerce")
df_finalizado["Hora"] = df_finalizado["Data Finalização"].dt.hour

df_finalizado["Hora"] = pd.Categorical(df_finalizado["Hora"],categories=ordem, ordered=False)
df_finalizado = df_finalizado.sort_values("Hora")

df_finalizado["Hora"] = df_finalizado["Hora"].apply(lambda x: f"{int(x):02d}:00" if pd.notna(x) else None)

df_grouped = df_finalizado.groupby("Hora")["Situação"].count().reset_index()


# ============================================================
# CAIXAS POR POSTO
# ============================================================
df_posto = (
    df.drop_duplicates(subset=['Num. Picking', 'Num. Posto'])
    .loc[df['Num. Posto'].notna()]
    .copy()
)

df_posto['Num. Posto'] = df_posto['Num. Posto'].astype(str).str.strip()

df_contagem = df_posto.groupby("Num. Posto")["Num. Picking"].count().reset_index()
df_contagem.columns = ["Num. Posto", "Quantidade"]
df_contagem = df_contagem.sort_values("Quantidade", ascending=False)


# ============================================================
# APANHAS POR POSTO
# ============================================================
apanha_posto = df_apanhas[df_apanhas["Num. Posto"].notna()].copy()
apanha_posto["Num. Posto"] = apanha_posto["Num. Posto"].astype(str).str.strip()

apanhas_group = apanha_posto.groupby("Num. Posto")["Cod. SKU"].count().reset_index()
apanhas_group.columns = ["Num. Posto", "Quantidade"]
apanhas_group = apanhas_group.sort_values("Quantidade", ascending=False)


# ============================================================
# GRÁFICOS
# ============================================================
col_left, col_center, col_right = st.columns([4, 4, 5])

# PIZZA BALANÇA
df_pizza = pd.DataFrame({
    "Tipo": ["Balança", "Reconferência"],
    "Quantidade": [total_bal, total_reconf]
})

fig_pizza = px.pie(df_pizza, names="Tipo", values="Quantidade",
                   color="Tipo",
                   color_discrete_map={"Balança": "#1E88E5", "Reconferência": "#F4511E"})

fig_pizza.update_layout(
    title="",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=10, b=10, l=10, r=10),
    legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center")
)


with col_left:
    st.subheader("Eficiência da Balança")
    st.plotly_chart(fig_pizza, use_container_width=True)




with col_center:
    st.subheader("Produtividade Order Start")
    fig_bar = px.bar(
        order_start,
        x="HORA",
        y="Quantidade",
        text="Quantidade",
        labels={"HORA": "Hora do Turno"},
    )
    fig_bar.update_traces(marker_color="#1E88E5", textposition="outside")
    st.plotly_chart(fig_bar, use_container_width=True)



with col_right:
    st.subheader("Apanhas por Hora Separação")
    fig = px.line(
        df_grouped,
        x="Hora",
        y="Situação",
        markers=True,
        text="Situação",
        title=""
    )
    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, use_container_width=True)


st.divider(width=5)
# ---------------------------------- PRODUTIVIDADE SEPARAÇÕES ------------------------------
st.markdown("# Produtividade Separação")

col1, col2, col3 = st.columns([4, 4, 5])

# ============================
# APANHAS POR POSTO
# ============================
with col1:
    fig = go.Figure(
        data=[
            go.Bar(
                x=list(range(len(apanhas_group))),
                y=apanhas_group["Quantidade"],
                text=apanhas_group["Quantidade"],
                textposition="outside",
                marker=dict(
                    color="#F4511E",
                    line=dict(color="rgba(0,0,0,0.6)", width=1)  # borda leve
                ),
                hovertemplate="Posto: %{x}<br>Quantidade: %{y}<extra></extra>"
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text="Total de Apanhas Separados p/ Posto",
            x=0.5,
            xanchor="center",
            font=dict(size=20, family="Arial", color="#333")
        ),
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(len(apanhas_group))),
            ticktext=apanhas_group["Num. Posto"],
            title="Num. Posto",
            tickangle=-45,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            title="Quantidade",
            showgrid=True,
            gridcolor="rgba(200,200,200,0.3)"
        ),
        bargap=0.15,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hovermode="x"
    )

    fig.update_traces(
        textfont=dict(size=12, color="black"),
        textangle=0,
        cliponaxis=False
    )

    st.plotly_chart(fig, use_container_width=True)


# ============================
# VOLUMES POR POSTO
# ============================
with col2:
    fig = go.Figure(
        data=[
            go.Bar(
                x=list(range(len(df_contagem))),
                y=df_contagem["Quantidade"],
                text=df_contagem["Quantidade"],
                textposition="outside",
                marker=dict(
                    color="#1E88E5",
                    line=dict(color="rgba(0,0,0,0.6)", width=1)  # borda leve
                ),
                hovertemplate="Posto: %{x}<br>Quantidade: %{y}<extra></extra>"
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text="Total de Volumes Separados p/ Posto",
            x=0.5,
            xanchor="center",
            font=dict(size=20, family="Arial", color="#333")
        ),
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(len(df_contagem))),
            ticktext=df_contagem["Num. Posto"],
            title="Num. Posto",
            tickangle=-45,
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            title="Quantidade",
            showgrid=True,
            gridcolor="rgba(200,200,200,0.3)"
        ),
        bargap=0.15,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hovermode="x"
    )

    fig.update_traces(
        textfont=dict(size=12, color="black"),
        textangle=0,
        cliponaxis=False
    )

    st.plotly_chart(fig, use_container_width=True)


# Seu st.altair_chart() estava solto e sem gráfico
# Mantive aqui para você adicionar quando quiser
# st.altair_chart(fig_altair, use_container_width=True)
