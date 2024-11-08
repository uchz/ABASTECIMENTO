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


st.header("Acompanhamento Separação Varejo")

def hora_para_float(hora_str):
    if isinstance(hora_str, str):  # Verifica se o valor é string
        h, m = map(int, hora_str.split(':'))
        return h + m / 60.0  # Converte minutos para fração de hora
    return hora_str  # Se já for número, retorna como está

def data_varejo():
    
    df_desempenho = pd.read_excel('Gestao_Produtividade_detalhada_WMS_2.xlsx', header=2)

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
    
    pedidos = pd.read_excel('Expedicao_de_Mercadorias_Varejo.xls', header=2)

    return pedidos

pedidos = pedidos_varejo()

area_varejo = ['SEP VAREJO 01 - (PICKING)']
situacao = ['Enviado para separação', 'Em processo separação','Aguardando conferência', 'Em processo conferência', 'Aguardando conferência volumes']



pedidos.drop(columns=colunas)

status_var = pedidos[pedidos['Descrição (Area de Separacao)'].isin(area_varejo)]
status_var = status_var[status_var['Situação'].isin(situacao)]

status_var['O.C'] = status_var['O.C'].astype(int)
status_var['O.C'] = status_var['O.C'].astype(str)

status_varejo = status_var.groupby('Situação').agg(Qtd_Pedidos = ('O.C', 'count'), OC = ('O.C', 'min'))

#st.write(status_varejo)


st.subheader("Produtividade Separação")
#Filtrando apenas por Separação do varejo


varejo = df[df['Area Separação'].isin(area_varejo)]

#Produtividade Varejo. Ordenado por apanhas
prod_varejo = varejo[['Usuário','Qtde Tarefas']].groupby('Usuário').agg(Apanhas=('Qtde Tarefas', 'count'), Pedidos=('Qtde Tarefas', 'nunique'))

prod_varejo = prod_varejo.sort_values(by=('Apanhas'), ascending=False)

data_atual = pd.DataFrame({"Apanhas": data, 'Pedidos': hora},index=['Data'], columns=prod_varejo.columns)

#Somando o total de apanhas e pedidos
total = pd.DataFrame({'Apanhas': prod_varejo['Apanhas'].sum(), 'Pedidos': prod_varejo['Pedidos'].sum()}, index=['Total'])

data_atual = pd.DataFrame({"Apanhas": data, 'Pedidos': hora },index=['Data'], columns=prod_varejo.columns)

prod_varejo.fillna(0, inplace=True)
# Concatenar as linhas ao DataFrame original
prod_varejo = pd.concat([prod_varejo, total, data_atual])

prod_varejo.fillna('', inplace=True)

#Tabela para impressão/visualização
prod_varejo['Usuário'] = prod_varejo.index

prod_varejo.drop(columns="Usuário", inplace=True)
prod_varejo.index.name = "Usuário"

st.write(prod_varejo)
## TAREFAS POR HORA

st.subheader('Tarefas por Hora:')

tarefas_por_hora_var = varejo.groupby(['Usuário', 'Hora']).size().reset_index(name='Qtde Tarefas')

tarefas_por_hora_var['Hora'] = tarefas_por_hora_var['Hora'].apply(lambda x: x.strftime('%H:%M'))

tarefas_por_hora_var = tarefas_por_hora_var.sort_values(by=['Usuário', 'Hora'])

tarefas_por_hora_var['Ordenacao'] = tarefas_por_hora_var['Hora'].apply(lambda x: (pd.to_datetime(str(x), format='%H:%M') + pd.DateOffset(hours=5)).time())

tarefas_por_hora_var = tarefas_por_hora_var.sort_values(by=['Usuário', 'Ordenacao'])

# Remover a coluna de ordenação temporária
tarefas_por_hora_var = tarefas_por_hora_var.drop('Ordenacao', axis=1)

tarefas_pivot_var = tarefas_por_hora_var.pivot_table(index='Usuário', columns='Hora', values='Qtde Tarefas', fill_value=0)

# Ordenar o DataFrame pelas horas
tarefas_pivot_var = tarefas_pivot_var.reindex(columns=sorted(tarefas_pivot_var.columns, key=lambda x: (pd.to_datetime(str(x), format='%H:%M') + pd.DateOffset(hours=5)).time()))

# Calculando a média de cada coluna de horas
#mean_values = tarefas_pivot.mean()

#mean_values = mean_values.round(0).astype(int)

# Adicionando as médias como uma nova linha ao DataFrame tarefas_pivot
#tarefas_pivot.loc['Média Hora'] = mean_values

#mean_total  = mean_values.mean().mean()

sum_values = tarefas_pivot_var.sum()

#sum_values = tarefas_pivot.drop('Média Hora').sum()


tarefas_pivot_var.loc['Total P/ Hora'] = sum_values
tarefas_pivot_var = tarefas_pivot_var.fillna(0)
tarefas_pivot_var = tarefas_pivot_var.astype(int)

# Definir uma função para aplicar as cores com base nas condições
def apply_color(val):
    color = '#038a09' if val > 76 else '#ff5733'
    return f'background-color: {color}; color: white'


tarefas_pivot_var['Total'] = tarefas_pivot_var.sum(axis=1)
#tarefas_pivot['Total'] = tarefas_pivot['Total'].drop('Média Hora')

#tarefas_pivot['Total'].fillna(mean_total, inplace=True)

tarefas_pivot_var['Total'] = tarefas_pivot_var['Total'].astype(int)

# Aplicar a função de cor à tabela dinâmica
tarefas_pivot_styled_var = tarefas_pivot_var.style.applymap(apply_color)


    # Exibir a tabela dinâmica com estilos de cor
st.write(tarefas_pivot_styled_var)


st.subheader('Tarefas por Hora')

#st.write(tarefas_pivot)

tarefas_pivot_var = tarefas_pivot_var.drop(columns='Total')
total_hora_data = tarefas_pivot_var.loc['Total P/ Hora']



# df_total = total_hora_data.reset_index()
# df_total.columns = ['Hora', 'Total']

# # Converter Hora para valores numéricos para fazer a projeção
# df_total['Hora_float'] = pd.to_datetime(df_total['Hora'], format='%H:%M').dt.hour + pd.to_datetime(df_total['Hora'], format='%H:%M').dt.minute / 60

# # Criar modelo de regressão linear
# X = df_total['Hora_float'].values.reshape(-1, 1)
# y = df_total['Total'].values
# #Treinamento do modelo
# model = LinearRegression()
# model.fit(X, y)

# # Previsão para a próxima hora
# ultima_hora = df_total['Hora_float'].iloc[-1]
# proxima_hora_float = ultima_hora + 1  # Adiciona 1 hora
# proxima_tarefa_prevista = model.predict([[proxima_hora_float]])

# # Adicionar a projeção ao DataFrame
# df_projecao = pd.DataFrame({
#     'Hora': [f'{int(proxima_hora_float)}:00'],
#     'Total': [proxima_tarefa_prevista[0]],
#     'Projecao': ['Sim']  # Indicando que esse valor é projetado
# })

# # Combinar o DataFrame original com a projeção
# df_total['Projecao'] = 'Não'  # Indicando dados reais
# df_full = pd.concat([df_total, df_projecao], ignore_index=True)

# # Criar o gráfico usando Matplotlib
# plt.figure(figsize=(10, 6))

# # Gráfico das tarefas reais
# plt.plot(df_total['Hora'], df_total['Total'], label='Tarefas Reais', color='black', marker='o')

# # Adicionar a projeção
# # plt.plot(df_projecao['Hora'], df_projecao['Total'], label='Projeção', color='red', linestyle='--', marker='o')
# meta_valores = []
# for hora in total_hora_data.index:
#     if hora in ['19:00', '00:00', '01:00']:
#         meta_valores.append(621)  # Exemplo de meta nesses horários
#     else:
#         meta_valores.append(1242)  # Exemplo de meta para os outros horários

# # Traçar a linha de meta
# plt.plot(total_hora_data.index, meta_valores, linestyle='--', color='blue', label='Meta')

# # Adicionar rótulos para os dados reais
# for i, txt in enumerate(df_total['Total']):
#     plt.text(df_total['Hora'].iloc[i], df_total['Total'].iloc[i] + 0.2, f'{txt:.2f}', color='black')

# # plt.plot([df_total['Hora'].iloc[-1], f'{int(proxima_hora_float)}:00'], 
# #         [df_total['Total'].iloc[-1], proxima_tarefa_prevista[0]], 
# #         label='Projeção', linestyle='--', marker='x', color='red')

# # Adicionar rótulos para a projeção
# #plt.text(df_projecao['Hora'].iloc[0], df_projecao['Total'].iloc[0] + 0.2, f'{df_projecao["Total"].iloc[0]:.2f}', color='red')

# # Configurar os rótulos e título do gráfico
# plt.xlabel('Hora')
# plt.ylabel('Total de Tarefas')
# plt.title('Projeção de Tarefas por Hora')
# plt.legend(['Total de Tarefas', 'Total Projetado', 'Meta'])
# plt.grid(True)

# # Exibir o gráfico
# st.pyplot(plt)

df_total = total_hora_data.reset_index()
df_total.columns = ['Hora', 'Total']

# Criar o DataFrame para a linha de meta
meta_hora_filtrado = df_total[df_total['Hora'].isin(['20:00','21:00','22:00','23:00','00:00','01:00','02:00','03:00','04:00','05:00'])].copy()

meta_valores = []
for hora in meta_hora_filtrado['Hora']:
    if hora in ['19:00', '00:00', '01:00']:
        meta_valores.append(750)  # Meta para horários específicos
    else:
        meta_valores.append(1500)  # Meta para os outros horários

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