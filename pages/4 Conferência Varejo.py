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


def hora_para_float(hora_str):
    if isinstance(hora_str, str):  # Verifica se o valor é string
        h, m = map(int, hora_str.split(':'))
        return h + m / 60.0  # Converte minutos para fração de hora
    return hora_str  # Se já for número, retorna como está

fuso_horario = 'America/Sao_Paulo'


def data_conf():

    df_conf = pd.read_excel('archives/Gestao_Produtividade_detalhada_WMS_2.xlsx', header=2)

    return df_conf

df_conf = data_conf()

#Função para trazer data e hora atualizada

def data ():

    data_atual = datetime.now(pytz.timezone(fuso_horario)).strftime('%d-%m-%Y')
    hora_atual = datetime.now(pytz.timezone(fuso_horario)).strftime('%H:%M')

    return data_atual, hora_atual

data, hora = data()

df_conf['Dt./Hora Inicial'] = pd.to_datetime( df_conf['Dt./Hora Inicial'], format='%d/%m/%Y %H:%M:%S')

df_conf['Hora'] = df_conf['Dt./Hora Inicial'].dt.hour

df_conf['Hora'] = pd.to_datetime(df_conf['Hora'], format='%H').dt.time

#st.pyplot(fig)

st.header('Produtividade Conferência')

area_conf = ['CONFERENCIA VAREJO 1']

conferencia = df_conf[df_conf['Area Separação'].isin(area_conf)]

prod_conferencia = conferencia[['Usuário','Qtde Tarefas']].groupby('Usuário').agg(Apanhas=('Qtde Tarefas', 'count'), Pedidos=('Qtde Tarefas', 'nunique'))

prod_conferencia = prod_conferencia.sort_values(by=('Apanhas'), ascending=False)

data_atual = pd.DataFrame({"Apanhas": data, 'Pedidos': hora},index=['Data'], columns=prod_conferencia.columns)

#Somando o total de apanhas e pedidos
total = pd.DataFrame({'Apanhas': prod_conferencia['Apanhas'].sum(), 'Pedidos': prod_conferencia['Pedidos'].sum()}, index=['Total'])

# Concatenar as linhas ao DataFrame original
prod_conferencia = pd.concat([prod_conferencia, total, data_atual])

prod_conferencia['Usuário'] = prod_conferencia.index
prod_conferencia.drop(columns="Usuário", inplace=True)
prod_conferencia.index.name = "Usuário"

st.write(prod_conferencia)

## TAREFAS POR HORA

st.subheader('Tarefas por Hora:')

tarefas_por_hora = conferencia.groupby(['Usuário', 'Hora']).size().reset_index(name='Qtde Tarefas')

tarefas_por_hora['Hora'] = tarefas_por_hora['Hora'].apply(lambda x: x.strftime('%H:%M'))

tarefas_por_hora = tarefas_por_hora.sort_values(by=['Usuário', 'Hora'])

tarefas_por_hora['Ordenacao'] = tarefas_por_hora['Hora'].apply(lambda x: (pd.to_datetime(str(x), format='%H:%M') + pd.DateOffset(hours=5)).time())

tarefas_por_hora = tarefas_por_hora.sort_values(by=['Usuário', 'Ordenacao'])

# Remover a coluna de ordenação temporária
tarefas_por_hora = tarefas_por_hora.drop('Ordenacao', axis=1)

tarefas_pivot = tarefas_por_hora.pivot_table(index='Usuário', columns='Hora', values='Qtde Tarefas', fill_value=0)

# Ordenar o DataFrame pelas horas
tarefas_pivot = tarefas_pivot.reindex(columns=sorted(tarefas_pivot.columns, key=lambda x: (pd.to_datetime(str(x), format='%H:%M') + pd.DateOffset(hours=5)).time()))

# Calculando a média de cada coluna de horas
mean_values = tarefas_pivot.mean()

mean_values = mean_values.round(0).astype(int)

# Adicionando as médias como uma nova linha ao DataFrame tarefas_pivot
# tarefas_pivot.loc['Média Hora'] = mean_values

# mean_total  = mean_values.mean().mean()

sum_values = tarefas_pivot.sum()

# sum_values = tarefas_pivot.drop('Média Hora').sum()


tarefas_pivot.loc['Total P/ Hora'] = sum_values

tarefas_pivot = tarefas_pivot.astype(int)

# Definir uma função para aplicar as cores com base nas condições
def apply_color(val):
    color = '#038a09' if val > 80 else '#ff5733'
    return f'background-color: {color}; color: white'


tarefas_pivot['Total'] = tarefas_pivot.sum(axis=1)
# tarefas_pivot['Total'] = tarefas_pivot['Total'].drop('Média Hora')

# tarefas_pivot['Total'].fillna(mean_total, inplace=True)

tarefas_pivot['Total'] = tarefas_pivot['Total'].astype(int)

# Aplicar a função de cor à tabela dinâmica
tarefas_pivot_styled = tarefas_pivot.style.applymap(apply_color)


    # Exibir a tabela dinâmica com estilos de cor
st.write(tarefas_pivot_styled)

tarefas_pivot = tarefas_pivot.drop(columns='Total')
total_hora_data = tarefas_pivot.loc['Total P/ Hora']


df_total = total_hora_data.reset_index()
df_total.columns = ['Hora', 'Total']

# Criar o DataFrame para a linha de meta
meta_hora_filtrado = df_total[df_total['Hora'].isin(['20:00','21:00','22:00','23:00','00:00','01:00','02:00','03:00','04:00','05:00'])].copy()

meta_valores = []
for hora in meta_hora_filtrado['Hora']:
    if hora in ['20:00', '00:00', '01:00']:
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
    color=alt.Color('Projecao:N', legend=None, scale=alt.Scale(domain=['Não', 'Sim'], range=['orange', 'red'])),  # Diferença visual entre real e projetado
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
rotulos_total = alt.Chart(df_full).mark_text(align='left', dx=5, dy=-5, color='white').encode(
    x=alt.X('Hora:N', sort=None),
    y=alt.Y('Total:Q'),
    text=alt.Text('Total:Q'),


)

# Gráfico da meta
grafico_meta = alt.Chart(meta_hora_filtrado).mark_line(strokeDash=[5, 5], color='red').encode(
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
    color='Tipo',
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


#contagem_tipos = prod_conferencia.groupby(['Usuário', 'Pedidos']).size().unstack(fill_value=0)


# Transformando os dados para formato long (necessário para Altair)
df_long = prod_conferencia.reset_index().melt(id_vars='Usuário', var_name='Pedidos', value_name='Quantidade')

df_apanhas = df_long[(df_long['Pedidos'] == 'Apanhas') & (df_long['Usuário'] != 'Total') & (df_long['Usuário'] != 'Data')]

user_order = df_apanhas['Usuário'].tolist()

st.title("Produtividade da Conferência")

# KPI Cards
# st.subheader("Resumo Geral")
kpi_cols = st.columns(2)

with kpi_cols[0]:
    st.metric("Total de Tarefas", f"{prod_conferencia.loc['Total'][0]}")

with kpi_cols[1]:
    st.metric("Produtividade Média", f"{tarefas_pivot.loc['Total P/ Hora'].mean():.1f} tarefas/hora")

# Gráfico de Barras - Tarefas Concluídas

st.write('')

# Agrega os dados para calcular a soma total por empilhador
df_totals = df_apanhas.groupby("Usuário", as_index=False).agg({"Quantidade": "sum"})

df_totals['Quantidade'] = df_totals['Quantidade'].astype(int)
df_apanhas['Quantidade'] = df_apanhas['Quantidade'].astype(int)

df_apanhas = df_apanhas.sort_values(by='Quantidade', ascending=False)
df_totals = df_totals.sort_values(by='Quantidade', ascending=False)

# Gráfico de barras empilhadas
bar_chart = alt.Chart(df_apanhas).mark_bar().encode(
    x=alt.X("Usuário:N" ,title="Conferente", sort=user_order),
    y=alt.Y("Quantidade:Q", title="Quantidade"),  # Define as cores
).properties(
    title="Produtividade Conferência"
)

# Rótulos com a soma total no topo de cada barra
total_labels = alt.Chart(df_totals).mark_text(
    align="center",  # Centraliza horizontalmente
    baseline="bottom",  # Coloca os rótulos no topo
    dy=-5,  # Ajusta a posição acima das barras
    color='white'
).encode(
    x=alt.X("Usuário:N", sort=user_order),
    y=alt.Y("Quantidade:Q"),
    text=alt.Text("Quantidade:Q")  # Mostra a soma total como texto
)

# Combina o gráfico de barras com os rótulos
final_chart = bar_chart + total_labels

# Exibe o gráfico
st.altair_chart(final_chart, use_container_width=True)

df_apanhas

