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

st.header('Acompanhamento Separação Confinado')

def hora_para_float(hora_str):
    if isinstance(hora_str, str):  # Verifica se o valor é string
        h, m = map(int, hora_str.split(':'))
        return h + m / 60.0  # Converte minutos para fração de hora
    return hora_str  # Se já for número, retorna como está

def data_varejo():
    
    df_desempenho = pd.read_excel('archives/Gestao_Produtividade_detalhada_WMS_2.xlsx', header=2)

    return df_desempenho

df_desempenho = data_varejo()
df = df_desempenho
colunas = ['Nro. Nota', 'Conferente', 'Enviado p/ Doca', 'Descrição (Área de Conferência)', 'Nro. Sep.', 'Nro. Único',
            'Descrição (Doca do WMS)', 'Cód. Doca', 'Peso Bruto', 'M3 Bruto', 'Área', 'Cód. Emp OC', 'Cód. Área Sep', 'Triagem Realizada', 'Cod. Conferente' ]
# Definindo fuso
fuso_horario = 'America/Sao_Paulo'


def data():
    data_atual = datetime.now(pytz.timezone(fuso_horario)).strftime('%d-%m-%Y')
    hora_atual = datetime.now(pytz.timezone(fuso_horario)).strftime('%H:%M')
    return data_atual, hora_atual

data, hora = data()     

df_desempenho['Dt./Hora Inicial'] = pd.to_datetime(df_desempenho['Dt./Hora Inicial'], format='%d/%m/%Y %H:%M:%S')
df_desempenho['Hora'] = df_desempenho['Dt./Hora Inicial'].dt.hour
df_desempenho['Hora'] = pd.to_datetime(df_desempenho['Hora'], format='%H').dt.time


def pedidos_varejo():
    
    pedidos = pd.read_excel('archives/Expedicao_de_Mercadorias_Varejo.xls', header=2)

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

#st.write(status_confinado)


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

# plt.figure(figsize=(12, 6))
# plt.plot(total_hora_data.index, total_hora_data.values, marker='o', linestyle='-', color='black', label='Total de Tarefas')

# for i, (hora, total) in enumerate(total_hora_data.items()):
#     plt.annotate(f'{int(total)}', (hora, total), textcoords="offset points", xytext=(0, 10), ha='center')

# plt.title('Total de Tarefas por Hora')
# plt.xlabel('Hora')
# plt.ylabel('Quantidade Total de Tarefas')
# plt.xticks(rotation=45)
# plt.legend(loc='upper left')
# plt.grid(True)
# plt.tight_layout()
# st.pyplot(plt)

df_total = total_hora_data.reset_index()
df_total.columns = ['Hora', 'Total']

# Criar o DataFrame para a linha de meta
meta_hora_filtrado = df_total[df_total['Hora'].isin(['19:00','20:00','21:00','22:00','23:00','00:00','01:00','02:00','03:00','04:00','05:00'])].copy()

meta_valores = []
for hora in meta_hora_filtrado['Hora']:
    if hora in ['19:00', '00:00', '01:00']:
        meta_valores.append(100)  # Meta para horários específicos
    else:
        meta_valores.append(200)  # Meta para os outros horários

# Adicionar a coluna de meta no DataFrame
meta_hora_filtrado['Meta'] = meta_valores

# === Cálculo da Projeção para a Próxima Hora ===
# Converter Hora para valores numéricos para prever a próxima hora
df_total['Hora_float'] = pd.to_datetime(df_total['Hora'], format='%H:%M').dt.hour + pd.to_datetime(df_total['Hora'], format='%H:%M').dt.minute / 60

# Criar modelo de regressão linear
X = df_total['Hora_float'].values.reshape(-1, 1)
y = df_total['Total'].values
model = LinearRegression()
model.fit(X, y)

# Previsão para a próxima hora
ultima_hora = df_total['Hora_float'].iloc[-1]
proxima_hora_float = ultima_hora + 1  # Adiciona 1 hora
proxima_tarefa_prevista = model.predict([[proxima_hora_float]])

# Adicionar a projeção ao DataFrame
# df_projecao = pd.DataFrame({
#     'Hora': [f'{int(proxima_hora_float)}:00'],
#     'Total': [proxima_tarefa_prevista[0]],
#     'Projecao': ['Sim']  # Indicando que esse valor é projetado
# })

# Combinar o DataFrame original com a projeção
df_total['Projecao'] = 'Não'  # Indicando dados reais
df_full = pd.concat([df_total], ignore_index=True)

# Gráfico principal: Total de tarefas por hora
grafico_total = alt.Chart(df_full).mark_line(point=True).encode(
    x=alt.X('Hora:N', sort=None, title='Hora'),
    y=alt.Y('Total:Q', title='Total de Tarefas'),
    color=alt.Color('Projecao:N', legend=None, scale=alt.Scale(domain=['Não', 'Sim'], range=['black', 'red'])),  # Diferença visual entre real e projetado
    tooltip=['Hora', 'Total']
).properties(
    title='Total de Apanhas por Hora',
    width=600,
    height=400
)
linha_pontilhada = alt.Chart(df_full[df_full['Projecao'] == 'Sim']).mark_line(
point=True,
strokeDash=[5, 5],  # Define a linha como pontilhada
color='red'
).encode(
    x=alt.X('Hora:N', sort=None),
    y=alt.Y('Total:Q'),
    tooltip=['Hora', 'Total']
)
# Rótulos dos dados no gráfico de total de tarefas
rotulos_total = alt.Chart(df_full).mark_text(align='left', dx=5, dy=-5, color='black').encode(
    x=alt.X('Hora:N', sort=None),
    y=alt.Y('Total:Q'),
    text=alt.Text('Total:Q')
)

# Gráfico da meta
grafico_meta = alt.Chart(meta_hora_filtrado).mark_line(strokeDash=[5, 5], color='blue').encode(
    x=alt.X('Hora:N', sort=None, title='Hora'),
    y=alt.Y('Meta:Q'),
    tooltip=['Hora', 'Meta']
)

# Combinar ambos os gráficos (total de tarefas e meta), incluindo rótulos e projeção
grafico_final = (grafico_total + linha_pontilhada + rotulos_total + grafico_meta )

# Exibir no Streamlit
st.altair_chart(grafico_final, use_container_width=True)

    # Converter horas para valores numéricos
df_total['Hora_float'] = df_total['Hora'].apply(hora_para_float)

# Criar o modelo de regressão linear
X = df_total['Hora_float'].values.reshape(-1, 1)
y = df_total['Total'].values

model = LinearRegression()
model.fit(X, y)

# Previsão para a próxima hora
ultima_hora = df_total['Hora_float'].iloc[-1]  # Pegando o valor numérico da última hora
proxima_hora_float = ultima_hora + 1  # Adiciona 1 hora
proxima_tarefa_prevista = model.predict([[proxima_hora_float]])

# Adicionar a previsão ao DataFrame
df_projecao = pd.DataFrame({
    'Hora': [f'{int(proxima_hora_float)}:00'],
    'Tarefas': [proxima_tarefa_prevista[0]],
    'Tipo': ['Previsão']
})

df_total['Tipo'] = 'Real'  # Marcando dados reais
df_full = pd.concat([df_total, df_projecao], ignore_index=True)  # Unindo os dados reais com a projeção

# Criar o gráfico com Altair
chart = alt.Chart(df_full).mark_line().encode(
    x='Hora',
    y='Tarefas',
    color='Tipo'
).properties(
    title='Projeção de Tarefas para a Próxima Hora'
)

# Adicionar pontos aos dados
points = chart.mark_point().encode(
    shape=alt.Shape('Tipo:N', legend=None)
)

# Adicionar rótulos de dados
labels = alt.Chart(df_full).mark_text(align='left', dx=5, dy=-5).encode(
    x='Hora',
    y='Tarefas',
    text=alt.Text('Tarefas:Q', format='.2f'),  # Formato de duas casas decimais para os rótulos
    color=alt.Color('Tipo:N', legend=None)
)

# Exibir o gráfico com os rótulos
(points + labels + chart).interactive()