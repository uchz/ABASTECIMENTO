# streamlit run app_streamlit_abastecimentos.py
# ------------------------------------------------------------
# Dashboard Profissional de Abastecimentos (BASE)
# - KPIs com comparativos (dia/semana/mês)
# - Indicadores avançados: % corretivas, abast/hora, eficiência
# - Gráficos interativos (Plotly)
# - Filtros por data e operador
# - Produtos mais abastecidos e heatmap hora x dia
# - Turno operacional: 19:00 → 06:00
# - Botão de atualização manual
# ------------------------------------------------------------

import io
import os
import unicodedata
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Abastecimentos — Dashboard", layout="wide", initial_sidebar_state="expanded")

DEFAULT_DIR = "C:\\Users\luis.silva\Documents\\OneDrive - LLE Ferragens\\BASE PBI"
DEFAULT_PATH = os.path.join(DEFAULT_DIR, "Abastecimentos.xlsx")

# =============================
# Leitura e tratamento de dados
# =============================
@st.cache_data(show_spinner=False)
def _read_excel(path: str, sheet: str = "BASE") -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet)

@st.cache_data(show_spinner=False)
def load_base(default_path: Optional[str] = None, uploaded: Optional[io.BytesIO] = None) -> pd.DataFrame:
    if uploaded is not None:
        df = pd.read_excel(uploaded, sheet_name="BASE")
    elif default_path is not None and os.path.exists(default_path):
        df = _read_excel(default_path, sheet="BASE")
    else:
        st.error("Nenhum arquivo encontrado. Envie o Excel na barra lateral.")
        st.stop()

    def normalize_columns(df):
        def norm(s):
            s = str(s).strip()
            s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('utf-8')
            return s.lower().replace(' ', '_')
        df.columns = [norm(c) for c in df.columns]
        return df
    df = normalize_columns(df)

    def parse_dt(s):
        return pd.to_datetime(s, errors="coerce", dayfirst=True, infer_datetime_format=True)

    if "data_inicial" in df.columns:
        df["data_inicial"] = parse_dt(df["data_inicial"])
    if "data_final" in df.columns:
        df["data_final"] = parse_dt(df["data_final"])
    if "data_operacional" in df.columns:
        df["data_operacional"] = parse_dt(df["data_operacional"])

    if "data_inicial" in df.columns and "data_final" in df.columns:
        df["data_final_ajustada"] = df.apply(
            lambda x: x["data_final"] + timedelta(days=1)
            if pd.notna(x["data_inicial"]) and pd.notna(x["data_final"]) and x["data_inicial"].hour > 12 and x["data_final"].hour < 12
            else x["data_final"], axis=1)
        df["duracao_min"] = (df["data_final_ajustada"] - df["data_inicial"]).dt.total_seconds() / 60
        df["duracao_h"] = df["duracao_min"] / 60
        df["hora_operacional"] = df["data_inicial"].dt.hour

    def ajustar_dia(row):
        data, hora = row.get("data_operacional"), row.get("hora_operacional")
        if pd.isna(data) or pd.isna(hora):
            return data
        return data - timedelta(days=1) if hora < 7 else data

    if "data_operacional" in df.columns:
        df["data_operacional_ajustada"] = df.apply(ajustar_dia, axis=1)
        df["dia"] = df["data_operacional_ajustada"].dt.date
        df["dia_semana"] = df["data_operacional_ajustada"].dt.day_name(locale="pt_BR.utf8")

    if "descricao_tarefa" in df.columns:
        df["eh_corretivo"] = df["descricao_tarefa"].astype(str).str.contains("corretiv", case=False, na=False)
    else:
        df["eh_corretivo"] = False

    return df

# =============================
# Funções de análise
# =============================
def chart_timeseries(df: pd.DataFrame):
    if df.empty or "dia" not in df.columns:
        st.info("Sem dados para exibir.")
        return
    g = df.groupby("dia").size().reset_index(name="tarefas")
    g["dia"] = pd.to_datetime(g["dia"])
    fig = px.area(g, x="dia", y="tarefas", title="📈 Abastecimentos por Dia Operacional (19h→06h)", markers=True)
    fig.update_traces(line_color="#2E86C1", fillcolor="rgba(46,134,193,0.3)")
    fig.update_xaxes(dtick="D1", tickformat="%d/%m/%y")
    st.plotly_chart(fig, use_container_width=True)

def chart_operadores(df: pd.DataFrame):
    if "usuario" not in df.columns:
        return
    g = df.groupby("usuario").size().reset_index(name="tarefas").sort_values("tarefas", ascending=False)
    fig = px.bar(g.head(6), x="usuario", y="tarefas", title="👷‍♂️ Operadores ", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)


def tabela_produtos(df: pd.DataFrame):
    if "cod_produto" not in df.columns:
        return
    g = df["cod_produto"].value_counts().head(15).reset_index()
    g.columns = ["Produto", "Tarefas"]
    fig = px.bar(g, x="Produto", y="Tarefas", title="🏷️ Produtos mais Abastecidos", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

# =============================
# 🚀 Abastecimentos por Hora
# =============================
def grafico_abastecimentos(df: pd.DataFrame):
    if "usuario" not in df.columns or "duracao_h" not in df.columns:
        st.info("Colunas insuficientes para cálculo.")
        return

    prod = df.groupby("usuario").agg(
        tarefas=("usuario", "count"),
        horas=("duracao_h", "sum")
    ).reset_index()
    prod = prod[prod["horas"] > 0]
    prod["abast_por_hora"] = prod["tarefas"] / prod["horas"]

    fig = px.bar(
        prod.sort_values("abast_por_hora", ascending=False),
        x="usuario",
        y="abast_por_hora",
        text_auto=".2f",
        title="🚀 Abastecimentos por Hora Ativa (real)"
    )
    fig.update_layout(height=420, xaxis_tickangle=-35)
    st.plotly_chart(fig, use_container_width=True)

    media_geral = prod["abast_por_hora"].mean()
    st.caption(f"Média geral: {media_geral:.2f} abast/hora")


# =============================
# 🎯 Eficiência Relativa
# =============================
def grafico_eficiencia(df: pd.DataFrame):
    if "usuario" not in df.columns or "duracao_h" not in df.columns:
        st.info("Colunas insuficientes para cálculo.")
        return

    prod = df.groupby("usuario").agg(
        tarefas=("usuario", "count"),
        horas=("duracao_h", "sum")
    ).reset_index()
    prod = prod[prod["horas"] > 0]
    prod["abast_por_hora"] = prod["tarefas"] / prod["horas"]
    media_geral = prod["abast_por_hora"].mean()
    prod["eficiencia_relativa_%"] = (prod["abast_por_hora"] / media_geral) * 100

    fig = px.bar(
        prod.sort_values("eficiencia_relativa_%", ascending=False),
        x="usuario",
        y="eficiencia_relativa_%",
        text_auto=".1f",
        title="🎯 Eficiência Relativa (média = 100%)"
    )
    fig.add_hline(y=100, line_dash="dash", line_color="gray")
    fig.update_layout(height=420, xaxis_tickangle=-35)
    st.plotly_chart(fig, use_container_width=True)

    st.caption("Acima de 100% = acima da média | Abaixo de 100% = abaixo da média")


# =============================
# Interface principal
# =============================
st.sidebar.header("📂 Dados")
if st.sidebar.button("🔄 Atualizar dados"):
    st.cache_data.clear()
    st.rerun()

up = st.sidebar.file_uploader("Carregue o Excel (aba BASE)", type=["xlsx"])
df = load_base(default_path=DEFAULT_PATH if up is None else None, uploaded=up)

if df is None or len(df) == 0:
    st.error("⚠️ Nenhum dado carregado.")
    st.stop()

# =============================
# Filtros laterais
# =============================
st.sidebar.header("🔍 Filtros")

if "data_operacional_ajustada" in df.columns and df["data_operacional_ajustada"].notna().any():
    min_dt = pd.to_datetime(df["data_operacional_ajustada"].min())
    max_dt = pd.to_datetime(df["data_operacional_ajustada"].max())

    # 👉 valor padrão = última data disponível
    start = max_dt.date()
    end = max_dt.date()

    start, end = st.sidebar.date_input(
        "Período (dia operacional)",
        value=(start, end),
        min_value=min_dt.date(),
        max_value=max_dt.date(),
    )

    mask = (
        (df["data_operacional_ajustada"] >= pd.to_datetime(start)) &
        (df["data_operacional_ajustada"] <= pd.to_datetime(end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))
    )
    df = df[mask].copy()

if "usuario" in df.columns:
    ops = sorted(df["usuario"].dropna().unique().tolist())
    sel_ops = st.sidebar.multiselect("Operadores", options=ops, default=ops[:])
    if sel_ops:
        df = df[df["usuario"].isin(sel_ops)]

# =============================
# Corpo principal
# =============================
st.title("📦 Dashboard de Abastecimentos")
# st.caption("_Período operacional: 19h → 06h (dia seguinte)_")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Tarefas", f"{len(df):,}")
# col4.metric("Operadores", f"{df['usuario'].nunique():,}")
col2.metric("% Corretivo", f"{df['eh_corretivo'].mean()*100:.1f}%")
col3.metric("Duração média (min)", f"{df['duracao_min'].mean():.1f}")
col4.write('                                   ')

with col1:

    chart_timeseries(df)
with col2:
    chart_operadores(df)
with col3:
    grafico_abastecimentos(df)
with col4:
    
    grafico_eficiencia(df)

tabela_produtos(df)
st.markdown("---")
st.caption("_Dashboard otimizado — foco em produtividade e eficiência durante o turno noturno._")


import pandas as pd
from datetime import datetime
import pytz
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.plotting import table
import altair as alt
from sklearn.linear_model import LinearRegression
from datetime import datetime
import numpy as np



st.header("Abastecimentos")

col1, col2 = st.columns(2)



# #Upload do arquivo de abastecimento

def abastecimento():

    df_abastecimento = pd.read_excel('archives/abastecimento-por-oc.xls', header=2)

    return df_abastecimento

df_abastecimento = abastecimento()
df_abastecimento = df_abastecimento[['CODPROD', 'DESCDESTINO', 'AREA DE SEPA ENDEREçO DESTINO']]
df_abastecimento['AREA DE SEPA ENDEREçO DESTINO'] = df_abastecimento['AREA DE SEPA ENDEREçO DESTINO'].fillna(value="ESTEIRA MFC")
df_abastecimento = df_abastecimento.drop_duplicates(subset=['CODPROD', 'AREA DE SEPA ENDEREçO DESTINO'])
df_abastecimento.sort_values(by='DESCDESTINO', inplace=True)


def validar_e_substituir(valor):
    if valor in ['ESTEIRA MFC', 'SEP CONFINADO', 'SEP VAREJO CONEXOES']:
        return valor
    else:
        return 'SEP VOLUMOSO'

df_abastecimento['AREA DE SEPA ENDEREçO DESTINO'] = df_abastecimento['AREA DE SEPA ENDEREçO DESTINO'].apply(validar_e_substituir)

df_abastecimento.rename(columns={"AREA DE SEPA ENDEREçO DESTINO" : "Area", 'CODPROD' : 'Qtd Códigos'}, inplace=True)

st.subheader('Abastecimentos por Área')

abastecimento_area = df_abastecimento.groupby('Area')['Qtd Códigos'].count().reset_index()

total = abastecimento_area['Qtd Códigos'].sum()
total_row = pd.DataFrame({'Area': ['Total'], 'Qtd Códigos': [total]})
abastecimento_area = pd.concat([abastecimento_area, total_row], ignore_index=True)

abastecimento_area = abastecimento_area.set_index('Area')

st.dataframe(abastecimento_area)

df_abastec = abastecimento()

st.write(df_abastec.drop_duplicates(subset=['CODPROD', 'CODENDORIGEM']).count())


# st.title("Desempenho dos Operadores")

# Carga e Processamento dos Dados de Desempenho dos Operadores

def data_abastecimento():


    df_desempenho = pd.read_excel('archives/Gestao_Produtividade_detalhada_WMS_2.xlsx', header=2)

    return df_desempenho

df_desempenho = data_abastecimento()

df = df_desempenho

# Definindo fuso
fuso_horario = 'America/Sao_Paulo'


def data():
    data_atual = datetime.now(pytz.timezone(fuso_horario)).strftime('%d-%m-%Y')
    hora_atual = datetime.now(pytz.timezone(fuso_horario)).strftime('%H:%M')
    return data_atual, hora_atual

data_atual, hora_atual = data()

df_desempenho['Dt./Hora Inicial'] = pd.to_datetime(df_desempenho['Dt./Hora Inicial'], format='%d/%m/%Y %H:%M:%S')
df_desempenho['Hora'] = df_desempenho['Dt./Hora Inicial'].dt.hour
df_desempenho['Hora'] = pd.to_datetime(df_desempenho['Hora'], format='%H').dt.time

tipo = ['PREVENTIVO', 'CORRETIVO', 'TRANSFERÊNCIA']
empilhadores = ['JOSIMAR.DUTRA','ETIQUETA', 'CROI.MOURA', 'LUIZ.BRAZ', 'ERICK.REIS','IGOR.VIANA', 'CLAUDIO.MARINS', 'THIAGO.SOARES', 'LUCAS.FARIAS', 'FABRICIO.SILVA', 'IGOR.CORREIA', 'YURI.XAVIER','LUIS.ALMEIDA']

df_desempenho = df_desempenho[df_desempenho['Tipo '].isin(tipo)]
df_desempenho = df_desempenho[df_desempenho['Usuário'].isin(empilhadores)]
corretivo_preventivo = df_desempenho[df_desempenho['Tipo '].isin(['CORRETIVO', 'PREVENTIVO'])]

contagem_tipos = corretivo_preventivo.groupby('Usuário')['Tipo '].count().sort_values(ascending=False)


contagem_tipos = df_desempenho.groupby(['Usuário', 'Tipo ']).size().unstack(fill_value=0)
contagem_tipos['Total'] = contagem_tipos.sum(axis=1)
contagem_tipos = contagem_tipos.sort_values(by='Total', ascending=False)
contagem_tipos.loc['Total'] = contagem_tipos.sum()
# st.header('Abastecimentos por Empilhador')
st.dataframe(contagem_tipos)


df_desempenho['Dt./Hora Inicial'] = pd.to_datetime(df_desempenho['Dt./Hora Inicial'], format='%d/%m/%Y %H:%M:%S')
df_desempenho['Hora'] = df_desempenho['Dt./Hora Inicial'].dt.hour
df_desempenho['Hora'] = pd.to_datetime(df_desempenho['Hora'], format='%H').dt.time

tipo = ['PREVENTIVO', 'CORRETIVO', 'TRANSFERÊNCIA']
empilhadores = ['JOSIMAR.DUTRA', 'ETIQUETA','CROI.MOURA', 'LUIZ.BRAZ', 'ERICK.REIS','IGOR.VIANA', 'CLAUDIO.MARINS', 'THIAGO.SOARES', 'LUCAS.FARIAS', 'FABRICIO.SILVA', 'IGOR.CORREIA', 'YURI.XAVIER','LUIS.ALMEIDA']

df_desempenho = df_desempenho[df_desempenho['Tipo '].isin(tipo)]
df_desempenho = df_desempenho[df_desempenho['Usuário'].isin(empilhadores)]
corretivo_preventivo = df_desempenho[df_desempenho['Tipo '].isin(['CORRETIVO', 'PREVENTIVO'])]

contagem_tipos = corretivo_preventivo.groupby('Usuário')['Tipo '].count().sort_values(ascending=False)

contagem_tipos = df_desempenho.groupby(['Usuário', 'Tipo ']).size().unstack(fill_value=0)

contagem_tipos['Total'] = contagem_tipos.sum(axis=1)
contagem_tipos.loc['Total'] = contagem_tipos.sum()



cores = sns.color_palette('afmhot', len(contagem_tipos.columns[:-1]))
tipos = contagem_tipos.columns[:-1]


# Agrupando por 'Usuário' e 'Tipo', e criando a tabela de contagem
contagem_tipos = df_desempenho.groupby(['Usuário', 'Tipo ']).size().unstack(fill_value=0)


# Transformando os dados para formato long (necessário para Altair)
df_long = contagem_tipos.reset_index().melt(id_vars='Usuário', var_name='Tipo', value_name='Quantidade')


# Exibindo a tabela completa, incluindo a linha 'Total'
# st.write("Tabela de contagem com Totais:")


tarefas_por_hora = df_desempenho.groupby(['Usuário', 'Hora']).size().reset_index(name='Qtde Tarefas')
tarefas_por_hora['Hora'] = tarefas_por_hora['Hora'].apply(lambda x: x.strftime('%H:%M'))
tarefas_por_hora = tarefas_por_hora.sort_values(by=['Usuário', 'Hora'])
tarefas_por_hora['Ordenacao'] = tarefas_por_hora['Hora'].apply(lambda x: (pd.to_datetime(str(x), format='%H:%M') + pd.DateOffset(hours=6)).time())
tarefas_por_hora = tarefas_por_hora.sort_values(by=['Usuário', 'Ordenacao'])
tarefas_por_hora = tarefas_por_hora.drop('Ordenacao', axis=1)
tarefas_pivot = tarefas_por_hora.pivot_table(index='Usuário', columns='Hora', values='Qtde Tarefas', fill_value=0)
tarefas_pivot = tarefas_pivot.reindex(columns=sorted(tarefas_pivot.columns, key=lambda x: (pd.to_datetime(str(x), format='%H:%M') + pd.DateOffset(hours=6)).time()))
sum_values = tarefas_pivot.sum()
tarefas_pivot.loc['Total P/ Hora'] = sum_values
tarefas_pivot['Total'] = tarefas_pivot.sum(axis=1)
tarefas_pivot['Total'] = tarefas_pivot['Total'].astype(int)

# st.subheader('Tarefas por Hora')
#st.write(tarefas_pivot)



tarefas_pivot = tarefas_pivot.drop(columns='Total')
total_hora_data = tarefas_pivot.loc['Total P/ Hora']


# st.subheader('Evolução p/ Hora')

plt.figure(figsize=(13, 7), dpi=800 )
plt.plot(total_hora_data.index, total_hora_data.values, marker='o', linestyle='-', color='black', label='Total de Tarefas')

for i, (hora, total) in enumerate(total_hora_data.items()):
    plt.annotate(f'{int(total)}', (hora, total), textcoords="offset points", xytext=(0, 10), ha='center')

plt.title('Total de Tarefas por Hora')
plt.xlabel('Hora')
plt.ylabel('Quantidade Total de Tarefas')
plt.xticks(rotation=45)
plt.legend(loc='upper left')
plt.grid(True)
plt.tight_layout()
#st.pyplot(plt)



# Exibição do título
st.title("Produtividade dos Empilhadores")

# KPI Cards
# st.subheader("Resumo Geral")
kpi_cols = st.columns(2)

with kpi_cols[0]:
    st.metric("Total de Tarefas", f"{df_desempenho['Tipo '].count()}")

with kpi_cols[1]:
    st.metric("Produtividade Média", f"{tarefas_pivot.loc['Total P/ Hora'].mean():.1f} tarefas/hora")

# Gráfico de Barras - Tarefas Concluídas

st.write('')

# Agrega os dados para calcular a soma total por empilhador
df_totals = df_long.groupby("Usuário", as_index=False).agg({"Quantidade": "sum"})

# Gráfico de barras empilhadas
bar_chart = alt.Chart(df_long).mark_bar().encode(
    x=alt.X("Usuário:N", title="Empilhador"),
    y=alt.Y("Quantidade:Q", title="Quantidade"),
    color=alt.Color("Tipo:N", title="Tipo de Abastecimento"),  # Define as cores
).properties(
    title="Abastecimentos por Empilhador"
)

# Rótulos com a soma total no topo de cada barra
total_labels = alt.Chart(df_totals).mark_text(
    align="center",  # Centraliza horizontalmente
    baseline="bottom",  # Coloca os rótulos no topo
    dy=-5,  # Ajusta a posição acima das barras
    color='white'
).encode(
    x=alt.X("Usuário:N"),
    y=alt.Y("Quantidade:Q"),
    text=alt.Text("Quantidade:Q")  # Mostra a soma total como texto
)

# Combina o gráfico de barras com os rótulos
final_chart = bar_chart + total_labels

# Exibe o gráfico
st.altair_chart(final_chart, use_container_width=True)



st.pyplot(plt)

# streamlit run app_streamlit_abastecimentos.py
# ------------------------------------------------------------
# Dashboard Profissional de Abastecimentos (BASE)
# - KPIs com comparação vs período anterior (dia, semana ISO, mês)
# - Gráficos interativos (Plotly)
# - Filtros por data, operador, tipo de tarefa
# - Heatmap por hora x dia da semana
# ------------------------------------------------------------

import io
import sys
from datetime import datetime, timedelta
from typing import Tuple, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Abastecimentos — Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Utilidades
# -----------------------------

RENAME_MAP = {
    "Descição": "Descrição",
    "Úsuario": "Usuário",
    "Cód.Usuario": "Cód. Usuário",
    "Cód.Produto": "Cód.Produto",
    "Nro.da Tarefa": "Nro. da Tarefa",
    "Cód.do End. de Origem": "Cód. End. Origem",
    "Cód.do End. de Destino": "Cód. End. Destino",
    "End. Origem": "Endereço Origem",
    "End. Destino": "Endereço Destino",
    "Data Operacional": "Data Operacional",
    "Data Inicial": "Data Inicial",
    "Data Final": "Data Final",
    "Qtd.Origem": "Qtd Origem",
    "Qtd.Destino": "Qtd Destino",
    "Descrição Tarefa": "Descrição Tarefa",
}

@st.cache_data(show_spinner=False)
def load_base(default_path: Optional[str] = None, uploaded: Optional[io.BytesIO] = None) -> pd.DataFrame:
    if uploaded is not None:
        df = pd.read_excel(uploaded, sheet_name="BASE")
    elif default_path is not None:
        df = pd.read_excel(default_path, sheet_name="BASE")
    else:
        st.stop()

    df = df.rename(columns=lambda c: str(c).strip())
    df = df.rename(columns=RENAME_MAP)

    # Datas robustas
    def parse_dt(s):
        return pd.to_datetime(s, errors="coerce", dayfirst=True, infer_datetime_format=True)

    if "Data Inicial" in df.columns:
        df["Data Inicial"] = parse_dt(df["Data Inicial"])    
    if "Data Final" in df.columns:
        df["Data Final"] = parse_dt(df["Data Final"]) 
    if "Data Operacional" in df.columns:
        # No exemplo anterior, formato YYYY-MM-DD
        df["Data Operacional"] = pd.to_datetime(df["Data Operacional"], errors="coerce")

    # Derivados
    if "Data Operacional" in df.columns:
        df["Dia"] = df["Data Operacional"].dt.date
        df["SemanaISO"] = df["Data Operacional"].dt.isocalendar().week.astype("Int64")
        df["Ano"] = df["Data Operacional"].dt.isocalendar().year.astype("Int64")
        df["Mes"] = df["Data Operacional"].dt.month.astype("Int64")
        df["AnoMes"] = df["Data Operacional"].dt.to_period("M").astype(str)
        df["DiaSemana"] = df["Data Operacional"].dt.dayofweek  # 0=Seg, 6=Dom

    # Hora operacional
    if "Hora" in df.columns and pd.api.types.is_numeric_dtype(df["Hora"]):
        df["Hora Operacional"] = df["Hora"].astype("Int64")
    elif "Data Inicial" in df.columns:
        df["Hora Operacional"] = df["Data Inicial"].dt.hour
    else:
        df["Hora Operacional"] = pd.NA

    # Duração (min)
    if "Data Inicial" in df.columns and "Data Final" in df.columns:
        df["Duracao (min)"] = (df["Data Final"] - df["Data Inicial"]).dt.total_seconds() / 60.0

    # Tipo corretivo
    if "Descrição Tarefa" in df.columns:
        df["Eh Corretivo"] = df["Descrição Tarefa"].astype(str).str.contains("corretiv", case=False, na=False)
    else:
        df["Eh Corretivo"] = False

    return df


def clamp_dt(dt: pd.Timestamp) -> pd.Timestamp:
    if pd.isna(dt):
        return pd.Timestamp("1970-01-01")
    return dt


def pick_period(df: pd.DataFrame, modo: str, data_ref: Optional[pd.Timestamp] = None) -> Tuple[pd.DataFrame, pd.DataFrame, str]:
    """Retorna (df_periodo_atual, df_periodo_anterior, label)
    modo: 'Dia', 'Semana', 'Mês'
    data_ref: data final de referência
    """
    if df.empty or "Data Operacional" not in df.columns:
        return df, df.iloc[0:0], "Sem período"

    if data_ref is None:
        data_ref = clamp_dt(pd.to_datetime(df["Data Operacional"].max()))

    data_ref = pd.to_datetime(data_ref)
    if modo == "Dia":
        inicio = data_ref.normalize()
        fim = inicio + pd.Timedelta(days=1)
        prev_inicio = inicio - pd.Timedelta(days=1)
        prev_fim = inicio
        label = f"{inicio.date()} vs {prev_inicio.date()}"
    elif modo == "Semana":  # ISO
        ano, semana, _ = data_ref.isocalendar()
        inicio = pd.to_datetime(f"{ano}-W{int(semana):02d}-1", format="%G-W%V-%u")
        fim = inicio + pd.Timedelta(days=7)
        prev_inicio = inicio - pd.Timedelta(days=7)
        prev_fim = inicio
        label = f"Semana {int(semana)} vs Semana {int(semana)-1}"
    else:  # Mês
        inicio = data_ref.replace(day=1).normalize()
        fim = (inicio + pd.offsets.MonthEnd(1)) + pd.Timedelta(days=1)
        prev_inicio = (inicio - pd.offsets.MonthBegin(1)).normalize()
        prev_fim = inicio
        label = f"{inicio.strftime('%b/%Y')} vs {(prev_inicio).strftime('%b/%Y')}"

    cur = df[(df["Data Operacional"] >= inicio) & (df["Data Operacional"] < fim)]
    prv = df[(df["Data Operacional"] >= prev_inicio) & (df["Data Operacional"] < prev_fim)]
    return cur.copy(), prv.copy(), label


def kpi_block(df_cur: pd.DataFrame, df_prev: pd.DataFrame):
    def pct_delta(cur, prev):
        if prev in (0, None, np.nan) or pd.isna(prev) or prev == 0:
            return None
        return (cur - prev) / prev * 100

    # KPI 1: Tarefas
    kpi_cur = len(df_cur)
    kpi_prev = len(df_prev)
    delta1 = pct_delta(kpi_cur, kpi_prev)

    # KPI 2: Operadores únicos
    op_cur = df_cur["Usuário"].nunique() if "Usuário" in df_cur.columns else 0
    op_prev = df_prev["Usuário"].nunique() if "Usuário" in df_prev.columns else 0
    delta2 = pct_delta(op_cur, op_prev)

    # KPI 3: Duração média
    dur_cur = df_cur["Duracao (min)"].mean() if "Duracao (min)" in df_cur.columns else np.nan
    dur_prev = df_prev["Duracao (min)"].mean() if "Duracao (min)" in df_prev.columns else np.nan
    delta3 = pct_delta(dur_cur, dur_prev)

    # KPI 4: % Corretivo
    cor_cur = (df_cur["Eh Corretivo"].mean() * 100) if "Eh Corretivo" in df_cur.columns and len(df_cur) else 0.0
    cor_prev = (df_prev["Eh Corretivo"].mean() * 100) if "Eh Corretivo" in df_prev.columns and len(df_prev) else 0.0
    delta4 = pct_delta(cor_cur, cor_prev)

    # KPI 5: Abastecimentos/Hora (global)
    def abast_por_hora(df):
        if df.empty:
            return 0.0
        if "Data Inicial" in df.columns and "Data Final" in df.columns:
            total_min = (df["Data Final"].max() - df["Data Inicial"].min()).total_seconds() / 60.0
            if total_min <= 0 or np.isnan(total_min):
                return np.nan
            return len(df) / (total_min / 60.0)
        # fallback via diferença de datas operacionais
        dur = (df["Data Operacional"].max() - df["Data Operacional"].min()).total_seconds() / 3600.0 if len(df) else np.nan
        return len(df) / dur if dur and dur > 0 else np.nan

    tph_cur = abast_por_hora(df_cur)
    tph_prev = abast_por_hora(df_prev)
    delta5 = pct_delta(tph_cur, tph_prev)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Tarefas", f"{kpi_cur:,}", None if delta1 is None else f"{delta1:+.1f}% vs ant.")
    c2.metric("Operadores", f"{op_cur:,}", None if delta2 is None else f"{delta2:+.1f}% vs ant.")
    c3.metric("Duração média (min)", f"{dur_cur:.1f}" if not np.isnan(dur_cur) else "—", None if delta3 is None else f"{delta3:+.1f}% vs ant.")
    c4.metric("% Corretivo", f"{cor_cur:.1f}%", None if delta4 is None else f"{delta4:+.1f}% vs ant.")
    c5.metric("Abastecimentos/hora", f"{tph_cur:.2f}" if not np.isnan(tph_cur) else "—", None if delta5 is None else f"{delta5:+.1f}% vs ant.")


def chart_timeseries(df: pd.DataFrame, grain: str):
    if df.empty:
        st.info("Sem dados no período selecionado.")
        return

    if grain == "Dia":
        g = df.groupby("Dia").size().reset_index(name="Tarefas")
        x, title = "Dia", "Tarefas por Dia"
    elif grain == "Semana":
        g = df.groupby(["Ano", "SemanaISO"], dropna=True).size().reset_index(name="Tarefas")
        g["Semana"] = g["Ano"].astype(str) + "-W" + g["SemanaISO"].astype(str)
        x, title = "Semana", "Tarefas por Semana ISO"
    else:
        g = df.groupby("AnoMes").size().reset_index(name="Tarefas")
        x, title = "AnoMes", "Tarefas por Mês"

    fig = px.line(g, x=x, y="Tarefas", markers=True)
    fig.update_layout(title=title, height=400, xaxis_title="Período", yaxis_title="Qtd")
    st.plotly_chart(fig, use_container_width=True)


def chart_operadores(df: pd.DataFrame, top_n: int = 10):
    if "Usuário" not in df.columns:
        return
    g = df.groupby("Usuário").size().reset_index(name="Tarefas").sort_values("Tarefas", ascending=False).head(top_n)
    fig = px.bar(g, x="Usuário", y="Tarefas")
    fig.update_layout(title=f"Top {top_n} Operadores por Tarefas", height=420, xaxis_tickangle=-35)
    st.plotly_chart(fig, use_container_width=True)


def chart_tipo_tarefa(df: pd.DataFrame):
    if "Descrição Tarefa" not in df.columns:
        return
    g = df["Descrição Tarefa"].value_counts().reset_index()
    g.columns = ["Tipo", "Tarefas"]
    fig = px.bar(g, x="Tipo", y="Tarefas")
    fig.update_layout(title="Distribuição por Tipo de Tarefa", height=420, xaxis_tickangle=-25)
    st.plotly_chart(fig, use_container_width=True)


def chart_heatmap_hora_semana(df: pd.DataFrame):
    if df.empty or "Hora Operacional" not in df.columns or "DiaSemana" not in df.columns:
        return
    g = df.groupby(["DiaSemana", "Hora Operacional"]).size().reset_index(name="Tarefas")
    # Completa grade 0..6 x 0..23
    idx = pd.MultiIndex.from_product([range(0,7), range(0,24)], names=["DiaSemana", "Hora Operacional"]) 
    g = g.set_index(["DiaSemana", "Hora Operacional"]).reindex(idx, fill_value=0).reset_index()
    pivot = g.pivot(index="DiaSemana", columns="Hora Operacional", values="Tarefas")

    fig = px.imshow(
        pivot,
        labels=dict(x="Hora", y="Dia da Semana (0=Seg)"),
        aspect="auto",
        color_continuous_scale="Blues",
    )
    fig.update_layout(title="Heatmap de Tarefas — Hora x Dia da Semana", height=480)
    st.plotly_chart(fig, use_container_width=True)


def tabela_origem_destino(df: pd.DataFrame, top_n: int = 15):
    cols = ["Endereço Origem", "Endereço Destino"]
    if not set(cols).issubset(df.columns):
        return
    g = df.groupby(cols).size().reset_index(name="Tarefas").sort_values("Tarefas", ascending=False).head(top_n)
    st.dataframe(g, use_container_width=True)


# -----------------------------
# Sidebar — Entrada de dados e filtros
# -----------------------------

st.sidebar.header("Dados")
up = st.sidebar.file_uploader("Carregue o Excel de Abastecimentos (aba BASE)", type=["xls","xlsx"])

default_path = "/mnt/data/Abastecimentos.xlsx"  # funciona no ChatGPT; ajuste no seu ambiente local

try:
    df_base = load_base(default_path=default_path if up is None else None, uploaded=up)
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

st.sidebar.header("Filtros")
# Filtro período absoluto
min_dt = pd.to_datetime(df_base["Data Operacional"].min()) if "Data Operacional" in df_base.columns else None
max_dt = pd.to_datetime(df_base["Data Operacional"].max()) if "Data Operacional" in df_base.columns else None

if min_dt is not None and max_dt is not None:
    start, end = st.sidebar.date_input(
        "Período (Data Operacional)",
        value=(min_dt.date(), max_dt.date()),
        min_value=min_dt.date(),
        max_value=max_dt.date(),
    )
    mask = (df_base["Data Operacional"] >= pd.to_datetime(start)) & (df_base["Data Operacional"] <= pd.to_datetime(end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))
    df_f = df_base[mask].copy()
else:
    df_f = df_base.copy()

ops = sorted(df_f["Usuário"].dropna().unique().tolist()) if "Usuário" in df_f.columns else []
sel_ops = st.sidebar.multiselect("Operadores", options=ops, default=ops[:])
if sel_ops and "Usuário" in df_f.columns:
    df_f = df_f[df_f["Usuário"].isin(sel_ops)]

tipos = sorted(df_f["Descrição Tarefa"].dropna().unique().tolist()) if "Descrição Tarefa" in df_f.columns else []
sel_tipos = st.sidebar.multiselect("Tipos de Tarefa", options=tipos, default=tipos[:])
if sel_tipos and "Descrição Tarefa" in df_f.columns:
    df_f = df_f[df_f["Descrição Tarefa"].isin(sel_tipos)]

st.sidebar.header("Comparação")
modo_comp = st.sidebar.radio("Comparar vs período anterior por:", ["Dia", "Semana", "Mês"], index=1)
ref_date = st.sidebar.date_input("Data de referência (fim do período)", value=(max_dt.date() if max_dt is not None else datetime.today().date()))

# -----------------------------
# KPIs
# -----------------------------

st.title("📦 Dashboard de Abastecimentos")
cur, prv, label = pick_period(df_f, modo_comp, pd.to_datetime(ref_date))
st.caption(f"Comparação: {label}")

kpi_block(cur, prv)

# -----------------------------
# Gráficos principais
# -----------------------------

left, right = st.columns((3,2), vertical_alignment="top")
with left:
    st.subheader("Tendência no período")
    grain = st.radio("Granularidade", ["Dia", "Semana", "Mês"], horizontal=True, index=0, key="gran_ts")
    chart_timeseries(df_f, grain)

with right:
    st.subheader("Operadores")
    topn = st.slider("Top N", 5, 30, 10)
    chart_operadores(cur if not cur.empty else df_f, top_n=topn)

st.subheader("Tipos de Tarefa")
chart_tipo_tarefa(cur if not cur.empty else df_f)

st.subheader("Heatmap — Hora x Dia da Semana")
chart_heatmap_hora_semana(cur if not cur.empty else df_f)

st.subheader("Rotas mais frequentes (Origem → Destino)")
tabela_origem_destino(cur if not cur.empty else df_f)

# -----------------------------
# Export
# -----------------------------

with st.expander("📥 Exportar subconjunto filtrado"):
    buf = io.BytesIO()
    df_f.to_excel(buf, index=False, sheet_name="BASE_filtrado")
    st.download_button("Baixar Excel filtrado", data=buf.getvalue(), file_name="abastecimentos_filtrado.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown(
    """
    ---
    _Dica_: Ajuste os filtros e o **Top N** para enxergar gargalos, operadores abaixo/acima da média e horários de pico.
    """
)



