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

st.subheader('Separação Confinado')

@st.cache_data
def data_varejo():
    
    df_desempenho = pd.read_excel('Gestao_Produtividade_detalhada_WMS_2.xlsx', header=2)

    return df_desempenho

df_desempenho = data_varejo()
df = df_desempenho
colunas = ['Nro. Nota', 'Conferente', 'Enviado p/ Doca', 'Descrição (Área de Conferência)', 'Nro. Sep.', 'Nro. Único',
            'Descrição (Doca do WMS)', 'Cód. Doca', 'Peso Bruto', 'M3 Bruto', 'Área', 'Cód. Emp OC', 'Cód. Área Sep', 'Triagem Realizada', 'Cod. Conferente' ]
# Definindo fuso
fuso_horario = 'America/Sao_Paulo'

@st.cache_data
def data():
    data_atual = datetime.now(pytz.timezone(fuso_horario)).strftime('%d-%m-%Y')
    hora_atual = datetime.now(pytz.timezone(fuso_horario)).strftime('%H:%M')
    return data_atual, hora_atual

data, hora = data()     

df_desempenho['Dt./Hora Inicial'] = pd.to_datetime(df_desempenho['Dt./Hora Inicial'], format='%d/%m/%Y %H:%M:%S')
df_desempenho['Hora'] = df_desempenho['Dt./Hora Inicial'].dt.hour
df_desempenho['Hora'] = pd.to_datetime(df_desempenho['Hora'], format='%H').dt.time

@st.cache_data
def pedidos_varejo():
    
    pedidos = pd.read_excel('Expedicao_de_Mercadorias_Varejo.xls', header=2)

    return pedidos

pedidos = pedidos_varejo()

area_confinado = ['SEP CONFINADO']
situacao = ['Enviado para separação', 'Em processo separação','Aguardando conferência', 'Em processo conferência', 'Aguardando conferência volumes']

status_confinado = pedidos[pedidos['Descrição (Area de Separacao)'].isin(area_confinado)]
status_confinado = status_confinado[status_confinado['Situação'].isin(situacao)]

status_confinado.drop(columns=colunas, inplace=True)

status_confinado['O.C'] = status_confinado['O.C'].astype(int)
status_confinado['O.C'] = status_confinado['O.C'].astype(str)

status_confinado = status_confinado.groupby('Situação').agg(Qtd_Pedidos = ('O.C', 'count'), OC = ('O.C', 'min'))

st.write(status_confinado)


#Filtrando apenas por Confinado
confinado = df[df['Area Separação'] == 'SEP CONFINADO' ]

#Soma de apanhas e pedidos
prod_conf = confinado[['Usuário','Qtde Tarefas']].groupby('Usuário').agg(Apanhas=('Qtde Tarefas', 'count'), Pedidos=('Qtde Tarefas', 'nunique'))

#Ordernando por Apanhas.
prod_conf = prod_conf.sort_values(by='Apanhas', ascending=False)

data_confinado = pd.DataFrame({"Apanhas": data, 'Pedidos': hora},index=['Data'], columns=prod_conf.columns)

#Somando o total de apanhas e pedidos
total_confinado = pd.DataFrame({'Apanhas': prod_conf['Apanhas'].sum(), 'Pedidos': prod_conf['Pedidos'].sum()}, index=['Total'])

#Juntando os DF
prod_conf = pd.concat([prod_conf, total_confinado, data_confinado])

prod_conf.index.name = "Usuário"

st.write(prod_conf)

tarefas_por_hora = confinado.groupby(['Usuário', 'Hora']).size().reset_index(name='Qtde Tarefas')
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

#st.subheader('Tarefas por Hora')
#st.write(tarefas_pivot)

tarefas_pivot = tarefas_pivot.drop(columns='Total')
total_hora_data = tarefas_pivot.loc['Total P/ Hora']

plt.figure(figsize=(12, 6))
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
st.pyplot(plt)