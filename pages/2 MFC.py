import streamlit as st
st.set_page_config(page_title="Acompanhamento MFC", layout="wide")
st.title("Resumo MFC")
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

df_posto_finalizado = df_posto[df_posto['Situação'] == 'F'].copy()
df_posto_finalizado["Data Finalização"] = pd.to_datetime(df_posto_finalizado["Data Finalização"], errors="coerce")
df_posto_finalizado["Hora"] = df_posto_finalizado["Data Finalização"].dt.hour

df_posto_finalizado["Hora"] = pd.Categorical(df_posto_finalizado["Hora"],categories=ordem, ordered=False)
df_posto_finalizado = df_posto_finalizado.sort_values("Hora")

df_posto_finalizado["Hora"] = df_posto_finalizado["Hora"].apply(lambda x: f"{int(x):02d}:00" if pd.notna(x) else None)

df_grouped = df_posto_finalizado.groupby("Hora")["Situação"].count().reset_index()

df_contagem = df_posto_finalizado.groupby("Num. Posto")["Num. Picking"].count().reset_index()
df_contagem.columns = ["Num. Posto", "Quantidade"]
df_contagem = df_contagem.sort_values("Quantidade", ascending=False)


# ============================================================
# APANHAS POR POSTO
# ============================================================
apanha_posto = df_finalizado[df_finalizado["Num. Posto"].notna()].copy()
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
    st.markdown(
    f"""
    <div style="text-align: center; font-size:16px;">
        <b>Volumes Finalizados:</b> {total}  <br>
        <b style="color:#1E88E5;">Balança:</b> {total_bal} ({perc_bal:.2f}%)  <br>
        <b style="color:#F4511E;">Reconferência:</b> {total_reconf} ({perc_reconf:.2f}%)
    </div>
    """,
    unsafe_allow_html=True
    )




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


# Filtrar apenas pendências
pendentes = df[df['Situação'] == 'P']

# Ordenar pelo índice original (mantendo o mais antigo)
pendentes = pendentes.sort_index()

# Selecionar o primeiro registro pendente por Num. Picking
resultado = (
    pendentes.groupby('Num. Picking')
    .agg({
        'Livre 4': 'first',   # OC
        'Num. Posto': 'first'     # Posto pendente mais antigo
    })
    .reset_index()
)

# Reordenar colunas
resultado_formatado = resultado.rename(columns={
    'Livre 4': 'OC',
    'Num. Picking': 'Picking',
    'Num. Posto': 'Posto'
})[['OC', 'Picking', 'Posto']]

# Função de classificação
def classificar_posto(posto):
    try:
        p = int(posto)
    except:
        return "Desconhecido"

    if 1 <= p <= 5 :
        return "Crítico"
    elif p == 101:
        return "Crítico"
    elif 6 <= p <= 12:
        return "Atenção"
    else:
        return "Normal"

resultado_formatado['Status'] = resultado_formatado['Posto'].apply(classificar_posto)


# Função de cores
def colorir_status(val):
    if val == "Crítico":
        return 'background-color: #ff9999; color: black; font-weight: bold;'   # vermelho claro
    elif val == "Atenção":
        return 'background-color: #ffe599; color: black;'                     # amarelo
    elif val == "Normal":
        return 'background-color: #b6d7a8; color: black;'                     # verde claro
    return ''


# Aplicar estilo
tabela_colorida = (
    resultado_formatado
    .style
    .applymap(colorir_status, subset=['Status'])
    .set_properties(**{
        'font-size': '12pt',
        'border': '1px solid #ddd',
        'padding': '6px'
    })
)

st.dataframe(tabela_colorida, width=800, height=500)

# ---------------------------------- PRODUTIVIDADE SEPARAÇÕES ------------------------------

# ============================
# APANHAS POR POSTO
# ============================
# ============================
# Cores padrão
# ============================
COR_APANHAS = "#FBC02D"   # Amarelo
COR_VOLUMES = "#1E88E5"   # Azul
BORDA = "rgba(0,0,0,0.5)"

# ============================
# Função para criar gráfico padrão
# ============================
def criar_grafico_barra(x_vals, y_vals, labels, titulo, cor):
    fig = go.Figure(
        data=[
            go.Bar(
                x=x_vals,
                y=y_vals,
                text=y_vals,
                textposition="outside",
                marker=dict(
                    color=cor,
                    line=dict(color=BORDA, width=1)
                ),
                hovertemplate="Posto: %{x}<br>Quantidade: %{y}<extra></extra>"
            )
        ]
    )

    fig.update_layout(
        title=dict(
            text=titulo,
            x=0.5, xanchor="center",
            font=dict(size=20, family="Arial", color="#333")
        ),
        xaxis=dict(
            tickmode="array",
            tickvals=x_vals,
            ticktext=labels,
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

    return fig


# ============================
# SEÇÃO: PRODUTIVIDADE SEPARAÇÃO
# ============================
st.markdown("# Produtividade Separação")

col1, col2 = st.columns([2,2.4])

import numpy as np

# ============================================
#       REMOVER OUTLIERS POR IQR
# ============================================
def remover_outliers_baixos(series):
    """Remove somente outliers absurdamente baixos usando o método do IQR."""
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lim_inferior = Q1 - 1.5 * IQR
    # remove apenas valores abaixo do limite inferior
    return series[series >= lim_inferior]


# ============================================
#       CÁLCULO DAS MÉTRICAS
# ============================================
tabela = (
    df_finalizado
    .groupby(['Usuário Operador', 'Hora'])
    .size()
    .reset_index(name='Quantidade')
)


tabela_posto = (
    df_posto_finalizado
    .groupby(['Usuário Operador', 'Hora'])
    .size()
    .reset_index(name='Quantidade')
)

# Criar tabela pivotada
tabela_pivot_posto = tabela_posto.pivot_table(
    index='Usuário Operador',   # linhas
    columns='Hora',             # colunas da tabela
    values='Quantidade',        # valores
    fill_value=0                # onde não existe valor, coloca 0
)


# Total apanhas por operador
apanhas_por_operador = df_finalizado.groupby("Usuário Operador")["Usuário Operador"].value_counts()
apanhas_por_operador = apanhas_por_operador[apanhas_por_operador > 30]
# Remover outliers
apanhas_sem_outlier = remover_outliers_baixos(apanhas_por_operador)



# Média final
media_apanhas_por_operador = apanhas_sem_outlier.mean()


# --- Produtividade por hora ---
prod_por_hora = (
    tabela.groupby(["Usuário Operador", "Hora"])["Quantidade"].sum()
)
#----- produtividade hora posto -----
prod_por_hora_posto = (
    tabela_posto.groupby(["Usuário Operador", "Hora"])["Quantidade"].sum()
)

prod_por_hora = prod_por_hora[prod_por_hora > 10]
prod_por_hora_sem_outlier = remover_outliers_baixos(prod_por_hora)

media_apanhas_por_hora = prod_por_hora_sem_outlier.mean()


prod_por_hora_posto = prod_por_hora_posto[prod_por_hora_posto > 10]
prod_por_hora_sem_outlier_posto = remover_outliers_baixos(prod_por_hora_posto)

media_volumes_por_hora = prod_por_hora_sem_outlier_posto.mean()

# ------ produtividade p/ volume ------
volume_p_operador = df_posto_finalizado.groupby("Usuário Operador")["Usuário Operador"].value_counts()
volume_p_operador = volume_p_operador[volume_p_operador > 30]

volume_p_operador_outlier = remover_outliers_baixos(volume_p_operador)


media_volume = volume_p_operador_outlier.mean()


# Seu st.altair_chart() estava solto e sem gráfico
# Mantive aqui para você adicionar quando quiser
# st.altair_chart(fig_altair, use_container_width=True)



# ============================================
#       CARDS DE ESTILO
# ============================================

card_style = """
    <div style="
        background-color: #ffffff;
        border-radius: 5 px;
        padding: 5px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        text-align: center;
        border-left: 10px solid #1E88E5;
    ">
        <h3 style="margin-bottom: 2px;">{titulo}</h3>
        <h1 style="color:#1E88E5; margin-top:0;">{valor}</h1>
    </div>
"""



colunas = st.columns([2,2,2,2])

with colunas[0]:
        
        st.markdown(
        card_style.format(
            titulo="Média de Apanhas por Operador",
            valor=f"{media_apanhas_por_operador:,.1f}"
        ),
        unsafe_allow_html=True, 
        
        )

with colunas[1]:
        st.markdown(
        card_style.format(
        titulo="Média de Apanhas por Operador por Hora",
        valor=f"{media_apanhas_por_hora:,.2f}"
    ),
    unsafe_allow_html=True,
    
    )
        
with colunas[2]:
        st.markdown(
        card_style.format(
        titulo="Média de Volumes por Operador",
        valor=f"{media_volume:,.2f}"
    ),
    unsafe_allow_html=True,
    
    )
with colunas[3]:
        st.markdown(
        card_style.format(
        titulo="Média de Volumes por Operador Hora",
        valor=f"{media_volumes_por_hora:,.2f}"
    ),
    unsafe_allow_html=True,
    
    )





col1, col2 = st.columns(2)


# APANHAS POR OPERADOR / POSTO
with col1:



    st.subheader("📊 Apanhas por Operador")

    # Agrupar e ordenar
    apanhas_operador = (
        df_apanhas.groupby("Usuário Operador")["Usuário Operador"]
        .count()
        .reset_index(name="Quantidade")
        .sort_values("Quantidade", ascending=False)
    )

    fig_operadores = go.Figure(
        data=[
            go.Bar(
                x=apanhas_operador["Usuário Operador"],
                y=apanhas_operador["Quantidade"],
                text=apanhas_operador["Quantidade"],
                textposition="outside",
                marker=dict(
                    color="#0904A6",  # Amarelo para combinar com o restante
                    line=dict(color="rgba(0,0,0,0.5)", width=1)
                )
            )
        ]
    )

    fig_operadores.update_layout(
        title=dict(
            text="Apanhas por Operador",
            x=0.5, xanchor="center",
            font=dict(size=22)
        ),
        xaxis=dict(
            title="Operador",
            tickangle=-45
        ),
        yaxis=dict(
            title="Quantidade de Apanhas",
            showgrid=True,
            gridcolor="rgba(200,200,200,0.3)"
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    fig_operadores.update_traces(
        textfont=dict(size=12, color="black"),
        cliponaxis=False
    )

    st.plotly_chart(fig_operadores, width="content")

        # Agrupar por operador e hora
        # Criar tabela pivotada

    tabela_pivot = tabela.pivot_table(
        index='Usuário Operador',   # linhas
        columns='Hora',             # colunas da tabela
        values='Quantidade',        # valores
        fill_value=0                # onde não existe valor, coloca 0
    )

    # Ordenar usuários pelo total somado
    tabela_pivot["TOTAL"] = tabela_pivot.sum(axis=1)
    tabela_pivot = tabela_pivot.sort_values("TOTAL", ascending=False)

    # Jogar para o Streamlit
    st.subheader("📊 Produtividade de Apanhas por Hora e Operador")
    st.dataframe(tabela_pivot, use_container_width=True)
    
    fig_apanhas = criar_grafico_barra(
        x_vals=list(range(len(apanhas_group))),
        y_vals=apanhas_group["Quantidade"],
        labels=apanhas_group["Num. Posto"],
        titulo="Total de Apanhas Separados p/ Posto",
        cor=COR_APANHAS
    )
    st.plotly_chart(fig_apanhas, width="content", key="apanhas_chart")




# VOLUMES POR POSTO
with col2:

    st.divider()
    operador_posto = df_posto['Usuário Operador'].value_counts()

    fig_operadores = go.Figure(
        data=[
            go.Bar(
                x=operador_posto.index,      # Operadores
                y=operador_posto.values,     # Quantidade
                text=operador_posto.values,  # Texto em cima da barra
                textposition="outside",
                marker=dict(
                    color="#2A57B9",
                    line=dict(color="rgba(0,0,0,0.5)", width=1)
                )
            )
        ]
    )

    fig_operadores.update_layout(
    title=dict(
        text="Volumes por Operador",
        x=0.5, xanchor="center",
        font=dict(size=22)
    ),
    xaxis=dict(
        title="Operador",
        tickangle=-45
    ),
    yaxis=dict(
        title="Quantidade de Volumes",
        showgrid=True,
        gridcolor="rgba(200,200,200,0.3)"
    ),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    )

    fig_operadores.update_traces(
        textfont=dict(size=12, color="black"),
        cliponaxis=False
    )

    st.plotly_chart(fig_operadores, width="content")

    # Agrupar por operador e hora
    tabela = (
        df_finalizado
        .groupby(['Usuário Operador', 'Hora'])
        .size()
        .reset_index(name='Quantidade')
    )


    # Ordenar usuários pelo total somado
    tabela_pivot_posto["TOTAL"] = tabela_pivot_posto.sum(axis=1)
    tabela_pivot_posto = tabela_pivot_posto.sort_values("TOTAL", ascending=False)

    # Jogar para o Streamlit
    st.subheader("📊 Produtividade de Volumes por Hora e Operador")
    st.dataframe(tabela_pivot_posto, width="content")

    fig_volumes = criar_grafico_barra(
        x_vals=list(range(len(df_contagem))),
        y_vals=df_contagem["Quantidade"],
        labels=df_contagem["Num. Posto"],
        titulo="Total de Volumes Separados p/ Posto",
        cor=COR_VOLUMES
    )
    st.plotly_chart(fig_volumes, width="content", key="volumes_chart")

    



