import streamlit as st
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



#Upload do arquivo de abastecimento

def abastecimento():

    df_abastecimento = pd.read_excel('archives/abastecimento-por-oc.xls', header=2)

    return df_abastecimento

df_abastecimento = abastecimento()
df_abastecimento = df_abastecimento[['CODPROD', 'DESCDESTINO', 'AREA DE SEPA ENDEREçO DESTINO']]
df_abastecimento = df_abastecimento.drop_duplicates(subset=['CODPROD', 'DESCDESTINO'])
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
empilhadores = ['JOSIMAR.DUTRA', 'CROI.MOURA', 'LUIZ.BRAZ', 'ERICK.REIS','IGOR.VIANA', 'CLAUDIO.MARINS', 'THIAGO.SOARES', 'LUCAS.FARIAS', 'FABRICIO.SILVA', 'IGOR.CORREIA', 'YURI.XAVIER','LUIS.ALMEIDA']

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
empilhadores = ['JOSIMAR.DUTRA', 'CROI.MOURA', 'LUIZ.BRAZ', 'ERICK.REIS','IGOR.VIANA', 'CLAUDIO.MARINS', 'THIAGO.SOARES', 'LUCAS.FARIAS', 'FABRICIO.SILVA', 'IGOR.CORREIA', 'YURI.XAVIER','LUIS.ALMEIDA']

df_desempenho = df_desempenho[df_desempenho['Tipo '].isin(tipo)]
df_desempenho = df_desempenho[df_desempenho['Usuário'].isin(empilhadores)]
corretivo_preventivo = df_desempenho[df_desempenho['Tipo '].isin(['CORRETIVO', 'PREVENTIVO'])]

contagem_tipos = corretivo_preventivo.groupby('Usuário')['Tipo '].count().sort_values(ascending=False)

contagem_tipos = df_desempenho.groupby(['Usuário', 'Tipo ']).size().unstack(fill_value=0)

contagem_tipos['Total'] = contagem_tipos.sum(axis=1)
contagem_tipos.loc['Total'] = contagem_tipos.sum()


st.write(' ## Total de Abastecimentos')
col3, col4 = st.columns(2)



with col3:
    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.write('')

    total_tipos = df_desempenho.groupby(['Tipo '])['Tipo '].count().reset_index(name='Total')
    total_tipos = total_tipos.rename(columns={'Tipo ': 'Tipo'})
    st.dataframe(total_tipos, height=151, width=450)

with col4:

    
    import plotly.express as px

    fig = px.pie(
        total_tipos,
        names='Tipo',
        values='Total',
        title='',
        width=350,
        height=350
    )

    st.plotly_chart(fig)


# st.header('Abastecimentos por Empilhador')
# with col1:
#     st.write(abastecimento_area)

# with col2:
#     st.write(contagem_tipos)

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
tarefas_por_hora['Ordenacao'] = tarefas_por_hora['Hora'].apply(lambda x: (pd.to_datetime(str(x), format='%H:%M') + pd.DateOffset(hours=5)).time())
tarefas_por_hora = tarefas_por_hora.sort_values(by=['Usuário', 'Ordenacao'])
tarefas_por_hora = tarefas_por_hora.drop('Ordenacao', axis=1)
tarefas_pivot = tarefas_por_hora.pivot_table(index='Usuário', columns='Hora', values='Qtde Tarefas', fill_value=0)
tarefas_pivot = tarefas_pivot.reindex(columns=sorted(tarefas_pivot.columns, key=lambda x: (pd.to_datetime(str(x), format='%H:%M') + pd.DateOffset(hours=5)).time()))
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
