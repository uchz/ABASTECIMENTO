# ## ANALISAR A MÉDIA DA DURAÇÃO DAS TAREFAS
# ## ANALISAR QUANTAS TAREFAS FEITAS NA NOITE
# ## 

# # %% 
# import pandas as pd

# df = pd.read_excel('Gestao_Produtividade_detalhada_WMS_2.xlsx', header=2)
# # %%
# df.rename(columns={'Tipo ': 'Tipo'}, inplace=True)
# # %%
# tipo = ['PREVENTIVO','CORRETIVO']

# df = df[df['Tipo'].isin(tipo)]
# # %%
# df.Usuário.unique()
# # %%
# empilhadores = ['CLAUDIO.MARINS', 'ERICK.REIS', 'CROI.MOURA',
#                  'JOSIMAR.DUTRA', 'INOEL.GUIMARAES' ]

# df = df[df['Usuário'].isin(empilhadores)]
# # %%
# df.info()
# # %%
# df['Dt./Hora Inicial'] = pd.to_datetime(df['Dt./Hora Inicial'])
# # %%
# df.info()
# # %%
# df['Hora Final'] = df['Dt./Hora Final'].dt.time


# # %%
# df.head()
# # %%
# df.sort_values(by='Dt./Hora Inicial', ascending=True, inplace=True)
# # %%
# media_duracao = df['Time'].mean()
# # %%
# media_duracao_horas = media_duracao.total_seconds() // 3600
# media_duracao_minutos = (media_duracao.total_seconds() % 3600) // 60
# # %%
# print(f'Média da duração: {int(media_duracao_horas)}h {int(media_duracao_minutos)}m')
# # %%
# media_empilhador = df.groupby('Usuário')['Time'].mean()
# # %%
# media = media_empilhador.apply( lambda x: f"{int(x.total_seconds() // 3600)}h {int((x.total_seconds() % 3600) // 60)}m")
# # %%
# media_empilhador
# # %%
# import matplotlib.pyplot as plt

# # Plotar os dados
# plt.figure(figsize=(10, 6))
# ax = media_empilhador.plot(kind='bar', color='red')
# plt.xlabel('Empilhador')
# plt.ylabel('Média de Duração (Minutos)')
# plt.title('Média de Duração das Tarefas por Empilhador')
# plt.xticks(rotation=0)
# plt.grid(axis='y')

# for i in ax.containers:
#     ax.bar_label(i, label_type='edge')
# # Exibir o gráfico
# plt.show()
# # %%
# import pandas as pd 
# df = pd.read_excel('Expedicao_de_Mercadorias_Varejo.xls', header=2)

# # %%
# df['Qtd. Tarefas'] = pd.to_numeric(df['Qtd. Tarefas'], errors='coerce')

# agrupado = df.groupby(['Situação', 'Descrição (Area de Separacao)'])['Qtd. Tarefas'].sum().reset_index()
# agrupado['Descrição (Area de Separacao)'].unique()
# # %%
# varejo = agrupado[agrupado['Descrição (Area de Separacao)'] == 'SEP VAREJO 01 - (PICKING)'].reset_index()
# varejo
# # %%

# feito = ['Em processo conferência','Conferência validada','Conferência com divergência','Aguardando recontagem','Aguardando conferência volumes','Aguardando conferência', 'Concluído']
# varejo_feito = varejo[varejo['Situação'].isin(feito)].copy()
# varejo_feito['Situação'] = 'Apanhas Realizadas'
# varejo_feito
# # %%
# df_feito_total = pd.DataFrame({
#     'Situação': ['Feito'],
#     'Total Apanhas': [varejo['Qtd. Tarefas'].sum()],
#     'Setor': ['Varejo']  # Renomear o setor
# })

# df_importados = pd.DataFrame({
#     'Situação': ['Importados'],
#     'Total Apanhas': [varejo['Qtd. Tarefas'].sum()],
#     'Setor': ['Varejo']
# })

# resultado_final = pd.concat([df_feito_total, df_importados], ignore_index=True)
# resultado_final
# # %%
# import pandas as pd

# # Exemplo de DataFrame com o total de tarefas "Feito" e "Importados"
# data = {
#     'Situação': ['Feito', 'Importados'],
#     'Qtd. Tarefas': [13, 15],
#     'Descrição (Area de Separacao)': ['Todos os setores', 'Todos os setores']
# }
# df = pd.DataFrame(data)

# # 1. Calcular a porcentagem de "Feito" em relação ao total de "Importados"
# percent_feito = (df.loc[df['Situação'] == 'Feito', 'Qtd. Tarefas'].values[0] / df.loc[df['Situação'] == 'Importados', 'Qtd. Tarefas'].values[0]) * 100

# # 2. Adicionar a linha com a porcentagem
# df_percent = pd.DataFrame({
#     'Situação': ['Porcentagem Feito'],
#     'Qtd. Tarefas': [f'{percent_feito:.2f}%'],
#     'Descrição (Area de Separacao)': ['Todos os setores']
# })

# # Concatenar o DataFrame original com o de porcentagem
# df_final = pd.concat([df, df_percent], ignore_index=True)

# # Exibindo o resultado
# print(df_final)

# # %%
import pandas as pd
import streamlit as st

st.sidebar.markdown("# Page 2 ❄️")
st.sidebar.markdown("# Page 3 🎉")
# DataFrame de exemplo
df = pd.DataFrame({
    'Nome': ['Item A', 'Item B', 'Item C'],
    'Quantidade': [10, 0, 5],
    'Preço': [100, 200, 50]
})

# Estilizando o DataFrame
def colorir_quantidade(val):
    color = 'red' if val == 0 else 'green'
    return f'background-color: {color}'

df_estilizado = df.style.applymap(colorir_quantidade, subset=['Quantidade'])

# Exibindo no Streamlit
st.dataframe(df_estilizado)

import altair as alt

# Exemplo de gráfico de barras
chart = alt.Chart(df).mark_bar().encode(
    x='Nome',
    y='Preço'
)

# Exibir tabela e gráfico
st.dataframe(df)
st.altair_chart(chart)

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Dados de exemplo (você pode substituir pelo seu DataFrame)
data = {
    'Ano': [2015, 2016, 2017, 2018, 2019, 2020],
    'Vendas': [100, 150, 200, 250, 300, 400]
}
df = pd.DataFrame(data)

# Criar o modelo de regressão linear
X = df['Ano'].values.reshape(-1, 1)
y = df['Vendas'].values

model = LinearRegression()
model.fit(X, y)

# Projeção para anos futuros
anos_futuros = np.array([2021, 2022, 2023, 2024]).reshape(-1, 1)
vendas_previstas = model.predict(anos_futuros)

# Plotar os dados históricos e a projeção
plt.plot(df['Ano'], df['Vendas'], label='Dados Reais', marker='o')
plt.plot(anos_futuros, vendas_previstas, label='Projeção', linestyle='--', marker='x')
plt.xlabel('Ano')
plt.ylabel('Vendas')
plt.title('Projeção de Vendas')
plt.legend()
plt.grid(True)
plt.show()

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from datetime import datetime

# Função para converter horas (HH:MM) para valores numéricos
def hora_para_float(hora_str):
    h, m = map(int, hora_str.split(':'))
    return h + m / 60.0  # Converte minutos para fração de hora

# Dados de exemplo com horários
data = {
    'Hora': ['19:00', '20:00', '21:00', '22:00', '23:00', '00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00'],
    'Tarefas': [5, 7, 9, 6, 4, 3, 2, 1, 1, 2, 3, 4, 6]
}
df = pd.DataFrame(data)

# Converter horas para valores numéricos
df['Hora_float'] = df['Hora'].apply(hora_para_float)

# Criar o modelo de regressão linear
X = df['Hora_float'].values.reshape(-1, 1)
y = df['Tarefas'].values

model = LinearRegression()
model.fit(X, y)

# Projeção para horários futuros (por exemplo, de 19:00 até 07:00)
horarios_futuros = ['08:00', '09:00', '10:00']  # Adicione mais se necessário
horarios_futuros_float = np.array([hora_para_float(h) for h in horarios_futuros]).reshape(-1, 1)
tarefas_previstas = model.predict(horarios_futuros_float)

# Plotar os dados históricos e a projeção
plt.plot(df['Hora'], df['Tarefas'], label='Dados Reais', marker='o')
plt.plot(horarios_futuros, tarefas_previstas, label='Projeção', linestyle='--', marker='x')
plt.xlabel('Hora')
plt.ylabel('Tarefas')
plt.title('Projeção de Tarefas por Hora')
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.show()

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Função para converter horas (HH:MM) para valores numéricos
def hora_para_float(hora_str):
    h, m = map(int, hora_str.split(':'))
    return h + m / 60.0  # Converte minutos para fração de hora

# Dados de exemplo com horários e tarefas/abastecimentos
data = {
    'Hora': ['19:00', '20:00', '21:00', '22:00', '23:00', '00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00'],
    'Tarefas': [5, 7, 9, 6, 4, 3, 2, 1, 1, 2, 3, 4, 6]  # Substitua pelos seus dados reais
}
df = pd.DataFrame(data)

# Converter horas para valores numéricos
df['Hora_float'] = df['Hora'].apply(hora_para_float)

# Criar o modelo de regressão linear
X = df['Hora_float'].values.reshape(-1, 1)
y = df['Tarefas'].values

model = LinearRegression()
model.fit(X, y)

# Previsão para a próxima hora
ultima_hora = df['Hora'].iloc[-1]  # Pegando a última hora da lista
proxima_hora_float = hora_para_float(ultima_hora) + 1  # Adiciona 1 hora
proxima_tarefa_prevista = model.predict([[proxima_hora_float]])

# Exibir a previsão
print(f'Previsão para a próxima hora ({proxima_hora_float}): {proxima_tarefa_prevista[0]:.2f} tarefas')

# Plotar os dados históricos e a projeção
plt.plot(df['Hora'], df['Tarefas'], label='Dados Reais', marker='o')
plt.plot([ultima_hora, f'{int(proxima_hora_float)}:00'], [df['Tarefas'].iloc[-1], proxima_tarefa_prevista[0]], 
         label='Projeção', linestyle='--', marker='x', color='red')
plt.xlabel('Hora')
plt.ylabel('Tarefas')
plt.title('Projeção de Tarefas para a Próxima Hora')
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.show()

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Função para converter horas (HH:MM) para valores numéricos, só aplica se for string
def hora_para_float(hora_str):
    if isinstance(hora_str, str):  # Verifica se o valor é string
        h, m = map(int, hora_str.split(':'))
        return h + m / 60.0  # Converte minutos para fração de hora
    return hora_str  # Se já for número, retorna como está

# Dados de exemplo com horários e tarefas/abastecimentos
data = {
    'Hora': ['19:00', '20:00', '21:00', '22:00', '23:00', '00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00'],
    'Tarefas': [5, 7, 9, 6, 4, 3, 2, 1, 1, 2, 3, 4, 6]  # Substitua pelos seus dados reais
}
df = pd.DataFrame(data)

# Converter horas para valores numéricos
df['Hora_float'] = df['Hora'].apply(hora_para_float)

# Criar o modelo de regressão linear
X = df['Hora_float'].values.reshape(-1, 1)
y = df['Tarefas'].values

model = LinearRegression()
model.fit(X, y)

# Previsão para a próxima hora
ultima_hora = df['Hora_float'].iloc[-1]  # Pegando o valor numérico da última hora
proxima_hora_float = ultima_hora + 1  # Adiciona 1 hora
proxima_tarefa_prevista = model.predict([[proxima_hora_float]])

# Exibir a previsão
print(f'Previsão para a próxima hora ({proxima_hora_float}): {proxima_tarefa_prevista[0]:.2f} tarefas')

# Plotar os dados históricos e a projeção
plt.plot(df['Hora'], df['Tarefas'], label='Dados Reais', marker='o')
plt.plot([df['Hora'].iloc[-1], f'{int(proxima_hora_float)}:00'], [df['Tarefas'].iloc[-1], proxima_tarefa_prevista[0]], 
         label='Projeção', linestyle='--', marker='x', color='red')
plt.xlabel('Hora')
plt.ylabel('Tarefas')
plt.title('Projeção de Tarefas para a Próxima Hora')
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.show()


# %%
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import altair as alt

# Função para converter horas (HH:MM) para valores numéricos
def hora_para_float(hora_str):
    if isinstance(hora_str, str):
        h, m = map(int, hora_str.split(':'))
        return h + m / 60.0
    return hora_str

# Dados de exemplo com horários e tarefas
data = {
    'Hora': ['19:00', '20:00', '21:00', '22:00', '23:00', '00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00'],
    'Tarefas': [5, 7, 9, 6, 4, 3, 2, 1, 1, 2, 3, 4, 6]
}
df = pd.DataFrame(data)

# Converter horas para valores numéricos
df['Hora_float'] = df['Hora'].apply(hora_para_float)

# Criar o modelo de regressão linear
X = df['Hora_float'].values.reshape(-1, 1)
y = df['Tarefas'].values

model = LinearRegression()
model.fit(X, y)

# Previsão para a próxima hora
ultima_hora = df['Hora_float'].iloc[-1]  # Pegando o valor numérico da última hora
proxima_hora_float = ultima_hora + 1  # Adiciona 1 hora
proxima_tarefa_prevista = model.predict([[proxima_hora_float]])

# Adicionar a previsão ao DataFrame
df_projecao = pd.DataFrame({
    'Hora': [f'{int(proxima_hora_float)}:00'],
    'Tarefas': [proxima_tarefa_prevista[0]],
    'Tipo': ['Previsão']
})

df['Tipo'] = 'Real'  # Marcando dados reais
df_full = pd.concat([df, df_projecao], ignore_index=True)  # Unindo os dados reais com a projeção

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

# Exibir o gráfico
chart + points

# %%
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import altair as alt

# Função para converter horas (HH:MM) para valores numéricos
def hora_para_float(hora_str):
    if isinstance(hora_str, str):
        h, m = map(int, hora_str.split(':'))
        return h + m / 60.0
    return hora_str

# Dados de exemplo com horários e tarefas
data = {
    'Hora': ['19:00', '20:00', '21:00', '22:00', '23:00', '00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00'],
    'Tarefas': [5, 7, 9, 6, 4, 3, 2, 1, 1, 2, 3, 4, 6]
}
df = pd.DataFrame(data)

# Converter horas para valores numéricos
df['Hora_float'] = df['Hora'].apply(hora_para_float)

# Criar o modelo de regressão linear
X = df['Hora_float'].values.reshape(-1, 1)
y = df['Tarefas'].values

model = LinearRegression()
model.fit(X, y)

# Previsão para a próxima hora
ultima_hora = df['Hora_float'].iloc[-1]  # Pegando o valor numérico da última hora
proxima_hora_float = ultima_hora + 1  # Adiciona 1 hora
proxima_tarefa_prevista = model.predict([[proxima_hora_float]])

# Adicionar a previsão ao DataFrame
df_projecao = pd.DataFrame({
    'Hora': [f'{int(proxima_hora_float)}:00'],
    'Tarefas': [proxima_tarefa_prevista[0]],
    'Tipo': ['Previsão']
})

df['Tipo'] = 'Real'  # Marcando dados reais
df_full = pd.concat([df, df_projecao], ignore_index=True)  # Unindo os dados reais com a projeção

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

# %%
import pandas as pd

# Criando um DataFrame a partir dos dados fornecidos
data = {
    'O.C': [0, 97154, 97154, 97154, 97129, 97129, 97129],
    'Nro. Nota': [0, 0, 0, 3243126, 0, 0, 0],
    'Qtd. Tarefas': [1, 2, 3, 1, 3, 2, 9],
    'Conferente': ['CRISTIANEP', 'JONATANC', 'LEANDRO.ALBANO', 'JOAOC', 'LEANDRO.ALBANO', 'LEANDRO.ALBANO', 'LEANDRO.ALBANO'],
    'Situação': ['Concluído', 'Concluído', 'Concluído', 'Concluído', 'Concluído', 'Concluído', 'Concluído'],
    'Descrição (Área de Separação)': ['13', 'SEP TUBOS', 'SEP VOLUMES RUA 34', 'SEP VAREJO 01 - (PICKING)', 'SEP VOLUMES RUA 24', 'SEP VOLUMES RUA 21', 'SEP VOLUMES RUA 14'],
    'Enviado p/ Doca': ['Sim', 'Sim', 'Sim', 'Sim', 'Sim', 'Sim', 'Sim'],
    'Descrição (Área de Conferência)': ['<SEM AREA>', '<SEM AREA>', '<SEM AREA>', 'CONFERENCIA VAREJO 1', '<SEM AREA>', '<SEM AREA>', '<SEM AREA>']
}

df = pd.DataFrame(data)

# Função para estilizar a coluna "Situação"
def colorize_situacao(situacao):
    if situacao == 'Concluído':
        return 'background-color: green'
    elif situacao == 'Em Andamento':
        return 'background-color: yellow'
    else:  # Considera 'Pendente' ou qualquer outro status
        return 'background-color: red'

# Aplicando a estilização
styled_df = df.style.applymap(colorize_situacao, subset=['Situação'])

# Exibindo o DataFrame estilizado
styled_df

# %%
import pandas as pd

# Criando um DataFrame a partir dos dados fornecidos
data = {
    'O.C': [0, 97154, 97154, 97154, 97129, 97129, 97129],
    'Nro. Nota': [0, 0, 0, 3243126, 0, 0, 0],
    'Qtd. Tarefas': [1, 2, 3, 1, 3, 2, 9],
    'Conferente': ['CRISTIANEP', 'JONATANC', 'LEANDRO.ALBANO', 'JOAOC', 'LEANDRO.ALBANO', 'LEANDRO.ALBANO', 'LEANDRO.ALBANO'],
    'Situação': ['Concluído', 'Enviado para a separação', 'Processo de Separação', 'Concluído', 'Concluído', 'Concluído', 'Concluído'],
    'Descrição (Área de Separação)': ['SEP VAREJO 01', 'SEP TUBOS', 'SEP VOLUMES RUA 34', 'SEP VAREJO 01 - (PICKING)', 'SEP VOLUMES RUA 24', 'SEP VOLUMES RUA 21', 'SEP VOLUMES RUA 14'],
    'Enviado p/ Doca': ['Sim', 'Sim', 'Sim', 'Sim', 'Sim', 'Sim', 'Sim'],
    'Descrição (Área de Conferência)': ['<SEM AREA>', '<SEM AREA>', '<SEM AREA>', 'CONFERENCIA VAREJO 1', '<SEM AREA>', '<SEM AREA>', '<SEM AREA>']
}

df = pd.DataFrame(data)

# Criando um novo DataFrame
new_df = pd.DataFrame(columns=['O.C', 'SEP VAREJO', 'SEP TUBOS', 'SEP VOLUMES RUA 34'])

# Preenchendo o novo DataFrame
for oc in df['O.C'].unique():
    row = {'O.C': oc}
    for area in new_df.columns[1:]:
        # Filtrando a situação para a O.C atual
        situacoes = df[(df['O.C'] == oc) & (df['Descrição (Área de Separação)'] == area)]['Situação']
        
        # Verificando a situação
        if situacoes.isin(['Enviado para a separação', 'Processo de Separação']).any():
            row[area] = 'Amarelo'
        else:
            row[area] = 'Verde'
    
    new_df = new_df.append(row, ignore_index=True)

# Função para estilizar o DataFrame
def colorize_cells(value):
    if value == 'Amarelo':
        return 'background-color: yellow'
    else:  # Verde
        return 'background-color: green'

# Aplicando a estilização ao novo DataFrame
styled_new_df = new_df.style.applymap(colorize_cells)

# Exibindo o novo DataFrame estilizado
styled_new_df

# %%
import pandas as pd
import numpy as np

# Criando um DataFrame a partir dos dados fornecidos
df = pd.read_excel('Expedicao_de_Mercadorias_Varejo.xls', header=2)

df
#%%


# Criando um novo DataFrame
new_df = pd.DataFrame(columns=['O.C', 'SEP VAREJO', 'SEP TUBOS', 'SEP VOLUMES RUA 34'])

# Preenchendo o novo DataFrame
rows = []  # Lista para armazenar as linhas a serem adicionadas

for oc in df['O.C'].unique():
    if pd.isna(oc):  # Verifica se o valor é NaN
        continue  # Ignora se for NaN
    row = {'O.C': int(oc)}  # Converte O.C para int
    for area in new_df.columns[1:]:
        # Filtrando a situação para a O.C atual
        situacoes = df[(df['O.C'] == oc) & (df['Descrição (Area de Separacao)'] == area)]['Situação']
        
        # Verificando a situação
        if situacoes.isin(['Enviado para a separação', 'Processo de Separação']).any():
            row[area] = 'Andamento'
        else:
            row[area] = 'Concluído'
    
    rows.append(row)

# Criando o novo DataFrame a partir da lista de linhas
new_df = pd.DataFrame(rows)

# Ordenando o DataFrame por O.C
new_df.sort_values(by='O.C', inplace=True)

# Resetando o índice após a ordenação
new_df.reset_index(drop=True, inplace=True)

# Função para estilizar o DataFrame
def colorize_cells(value):
    if value == 'Amarelo':
        return 'background-color: yellow'
    else:  # Verde
        return 'background-color: green'

# Aplicando a estilização ao novo DataFrame
styled_new_df = new_df.style.applymap(colorize_cells)

# Exibindo o novo DataFrame estilizado
styled_new_df

# %%
import pandas as pd
import numpy as np

def validar_e_substituir(valor):
    if valor in ['SEP VAREJO 01 - (PICKING)', 'SEP CONFINADO', 'SEP VAREJO CONEXOES']:
        return valor
    else:
        return 'SEP VOLUMOSO'
    
# Carregando a planilha com a primeira linha relevante como cabeçalho
df = pd.read_excel('Expedicao_de_Mercadorias_Varejo.xls', header=2)

df['Descrição (Area de Separacao)'] = df['Descrição (Area de Separacao)'].apply(validar_e_substituir)
# Extraindo todas as áreas únicas da coluna "Descrição (Area de Separacao)"
areas = df['Descrição (Area de Separacao)'].unique()



# Criando um novo DataFrame dinâmico para conter a "O.C" e todas as áreas
new_df = pd.DataFrame(columns=['O.C'] + list(areas))

# Preenchendo o novo DataFrame
rows = []

for oc in df['O.C'].unique():
    if pd.isna(oc):  # Verifica se o valor é NaN
        continue
    row = {'O.C': int(oc)}  # Converte O.C para int
    for area in areas:
        # Filtrando a situação para a O.C atual e a área específica
        situacoes = df[(df['O.C'] == oc) & (df['Descrição (Area de Separacao)'] == area)]['Situação']
        
        # Definindo o status baseado nas situações encontradas
        if situacoes.isin(['Enviado para separação', 'Em processo separação']).any():
            row[area] = 'Andamento'
        else:
            situacoes.isin(['Concluído']).all()
            row[area] = 'Concluído'

    
    rows.append(row)

# Criando o novo DataFrame a partir da lista de linhas
new_df = pd.DataFrame(rows)

# Ordenando o DataFrame por O.C
new_df.sort_values(by='O.C', inplace=True)
new_df.reset_index(drop=True, inplace=True)

# Função para estilizar o DataFrame com cores para cada status
def colorize_cells(value):
    if value == 'Andamento':
        return 'background-color: red'
    elif value == 'Concluído':
        return 'background-color: green'
    return ''

# Aplicando a estilização ao novo DataFrame
styled_new_df = new_df.style.applymap(colorize_cells)

# Exibindo o novo DataFrame estilizado
styled_new_df

# %%

import pandas as pd
import numpy as np

def validar_e_substituir(valor):
    if valor in ['SEP VAREJO 01 - (PICKING)', 'SEP CONFINADO', 'SEP VAREJO CONEXOES']:
        return valor
    else:
        return 'SEP VOLUMOSO'
    
# Carregando a planilha com a primeira linha relevante como cabeçalho
df = pd.read_excel('Expedicao_de_Mercadorias_Varejo.xls', header=2)

# Substituindo valores na coluna "Descrição (Area de Separacao)"
df['Descrição (Area de Separacao)'] = df['Descrição (Area de Separacao)'].apply(validar_e_substituir)
# Extraindo todas as áreas únicas da coluna "Descrição (Area de Separacao)"
areas = df['Descrição (Area de Separacao)'].unique()

# Criando um novo DataFrame dinâmico para conter a "O.C", todas as áreas e a coluna "Conferência Varejo"
new_df = pd.DataFrame(columns=['O.C'] + list(areas) + ['Conferência Varejo'])

# Preenchendo o novo DataFrame
rows = []

for oc in df['O.C'].unique():
    if pd.isna(oc):  # Verifica se o valor é NaN
        continue
    row = {'O.C': int(oc)}  # Converte O.C para int
    
    # Verificando cada área
    for area in areas:
        situacoes = df[(df['O.C'] == oc) & (df['Descrição (Area de Separacao)'] == area)]['Situação']
        
        # Definindo o status baseado nas situações encontradas
        if situacoes.isin(['Enviado para a separação', 'Processo de Separação']).any():
            row[area] = 'Andamento'
        else:
            row[area] = 'Concluído'

    # Verificando a situação para "Conferência Varejo"
    situacoes_conferencia = df[(df['O.C'] == oc) & (df['Descrição (Área de Conferência)'] == 'CONFERENCIA VAREJO 1')]['Situação']
    if situacoes_conferencia.isin(['Enviado para separação', 'Em processo separação', 'Aguardando conferência', 'Em processo conferência']).any():
        row['Conferência Varejo'] = 'Andamento'
    else:
        row['Conferência Varejo'] = 'Concluído'
    
    rows.append(row)

# Criando o novo DataFrame a partir da lista de linhas
new_df = pd.DataFrame(rows)

# Ordenando o DataFrame por O.C
new_df.sort_values(by='O.C', inplace=True)
new_df.reset_index(drop=True, inplace=True)

# Função para estilizar o DataFrame com cores para cada status
def colorize_cells(value):
    if value == 'Andamento':
        return 'background-color: red'
    elif value == 'Concluído':
        return 'background-color: green'
    return ''

# Aplicando a estilização ao novo DataFrame
styled_new_df = new_df.style.applymap(colorize_cells)

# Exibindo o novo DataFrame estilizado
styled_new_df

# %%
import pandas as pd
import numpy as np

def validar_e_substituir(valor):
    if valor in ['SEP VAREJO 01 - (PICKING)', 'SEP CONFINADO', 'SEP VAREJO CONEXOES']:
        return valor
    else:
        return 'SEP VOLUMOSO'
    
# Carregando a planilha com a primeira linha relevante como cabeçalho
df = pd.read_excel('Expedicao_de_Mercadorias_Varejo.xls', header=2)

# Substituindo valores na coluna "Descrição (Area de Separacao)"
df['Descrição (Area de Separacao)'] = df['Descrição (Area de Separacao)'].apply(validar_e_substituir)
# Extraindo todas as áreas únicas da coluna "Descrição (Area de Separacao)"
areas = df['Descrição (Area de Separacao)'].unique()

# Criando um novo DataFrame dinâmico para conter a "O.C", todas as áreas e a coluna "Conferência Varejo"
new_df = pd.DataFrame(columns=['O.C'] + list(areas) + ['Conferência Varejo'])

# Preenchendo o novo DataFrame
rows = []

for oc in df['O.C'].unique():
    if pd.isna(oc):  # Verifica se o valor é NaN
        continue
    row = {'O.C': int(oc)}  # Converte O.C para int
    
    # Verificando cada área
    for area in areas:
        situacoes = df[(df['O.C'] == oc) & (df['Descrição (Area de Separacao)'] == area)]['Situação']
        
        # Ajustando a lógica para "Andamento" ou "Concluído" por área
        # if situacoes.empty:
        #     row[area] = 'Concluído'  # Marca como "Concluído" se não há registros
        if situacoes.isin(['Enviado para a separação', 'Processo de Separação']).any():
            row[area] = 'Andamento'
        else:
            row[area] = 'Concluído'

    # Verificando a situação para "Conferência Varejo"
    situacoes_conferencia = df[(df['O.C'] == oc) & (df['Descrição (Área de Conferência)'] == 'CONFERENCIA VAREJO 1')]['Situação']
    if situacoes_conferencia.isin(['Aguardando conferência volumes']).any():
        row['Conferência Varejo'] = 'Concluído'
    else:
        row['Conferência Varejo'] = 'Andamento'
    
    rows.append(row)

# Criando o novo DataFrame a partir da lista de linhas
new_df = pd.DataFrame(rows)

# Ordenando o DataFrame por O.C
new_df.sort_values(by='O.C', inplace=True)
new_df.reset_index(drop=True, inplace=True)

# Função para estilizar o DataFrame com cores para cada status
def colorize_cells(value):
    if value == 'Andamento':
        return 'background-color: yellow'
    elif value == 'Concluído':
        return 'background-color: green'
    return ''

# Aplicando a estilização ao novo DataFrame
styled_new_df = new_df.style.applymap(colorize_cells)

# Exibindo o novo DataFrame estilizado
styled_new_df

# %%
import pandas as pd
import numpy as np

def validar_e_substituir(valor):
    if valor in ['SEP VAREJO 01 - (PICKING)', 'SEP CONFINADO', 'SEP VAREJO CONEXOES']:
        return valor
    else:
        return 'SEP VOLUMOSO'
    
# Carregando a planilha com a primeira linha relevante como cabeçalho
df = pd.read_excel('Expedicao_de_Mercadorias_Varejo.xls', header=2)

# Substituindo valores na coluna "Descrição (Area de Separacao)"
df['Descrição (Area de Separacao)'] = df['Descrição (Area de Separacao)'].apply(validar_e_substituir)
# Extraindo todas as áreas únicas da coluna "Descrição (Area de Separacao)"
areas = df['Descrição (Area de Separacao)'].unique()

# Criando um novo DataFrame dinâmico para conter a "O.C", todas as áreas e a coluna "Conferência Varejo"
new_df = pd.DataFrame(columns=['O.C'] + list(areas) + ['Conferência Varejo'])

# Preenchendo o novo DataFrame
rows = []

for oc in df['O.C'].unique():
    if pd.isna(oc):  # Verifica se o valor é NaN
        continue
    row = {'O.C': int(oc)}  # Converte O.C para int
    
    # Verificando cada área
    for area in areas:
        situacoes = df[(df['O.C'] == oc) & (df['Descrição (Area de Separacao)'] == area)]['Situação']
        
        # Ajustando a lógica para "Andamento" ou "Concluído" por área
        if situacoes.isin(['Enviado para a separação', 'Processo de Separação']).any():
            row[area] = 'Andamento'
        elif situacoes.isin(['Concluído']).all():
            row[area] = 'Concluído'
        else:
            row[area] = 'Andamento'  # Caso haja outra situação que não seja "Concluído"
    
    # Verificando a situação para "Conferência Varejo"
    situacoes_conferencia = df[(df['O.C'] == oc) & (df['Descrição (Área de Conferência)'] == 'CONFERENCIA VAREJO 1')]['Situação']
    if situacoes_conferencia.isin(['Enviado para separação', 'Em processo separação', 'Aguardando conferência', 'Em processo conferência']).any():
        row['Conferência Varejo'] = 'Andamento'
    else:
        row['Conferência Varejo'] = 'Concluído'
    
    rows.append(row)

# Criando o novo DataFrame a partir da lista de linhas
new_df = pd.DataFrame(rows)

# Ordenando o DataFrame por O.C
new_df.sort_values(by='O.C', inplace=True)
new_df.reset_index(drop=True, inplace=True)

# Função para estilizar o DataFrame com cores para cada status
def colorize_cells(value):
    if value == 'Andamento':
        return 'background-color: red'
    elif value == 'Concluído':
        return 'background-color: green'
    return ''

# Aplicando a estilização ao novo DataFrame
styled_new_df = new_df.style.applymap(colorize_cells)

# Exibindo o novo DataFrame estilizado
styled_new_df

# %%
import pandas as pd
import numpy as np

def validar_e_substituir(valor):
    if valor in ['SEP VAREJO 01 - (PICKING)', 'SEP CONFINADO', 'SEP VAREJO CONEXOES']:
        return valor
    else:
        return 'SEP VOLUMOSO'
    
# Carregando a planilha com a primeira linha relevante como cabeçalho
df = pd.read_excel('Expedicao_de_Mercadorias_Varejo.xls', header=2)

# Substituindo valores na coluna "Descrição (Area de Separacao)"
df['Descrição (Area de Separacao)'] = df['Descrição (Area de Separacao)'].apply(validar_e_substituir)
# Extraindo todas as áreas únicas da coluna "Descrição (Area de Separacao)"
areas = df['Descrição (Area de Separacao)'].unique()

# Criando um novo DataFrame dinâmico para conter a "O.C", todas as áreas e a coluna "Conferência Varejo"
new_df = pd.DataFrame(columns=['O.C'] + list(areas) + ['Conferência Varejo'] + ['Conferência Confinado'])

# Preenchendo o novo DataFrame
rows = []

for oc in df['O.C'].unique():
    if pd.isna(oc):  # Verifica se o valor é NaN
        continue
    row = {'O.C': int(oc)}  # Converte O.C para int
    
    # Verificando cada área de separação
    for area in areas:
        situacoes_separacao = df[(df['O.C'] == oc) & (df['Descrição (Area de Separacao)'] == area)]['Situação']
        
        # Define status da área de separação para "Andamento" ou "Concluído"
        if situacoes_separacao.isin(['Enviado para a separação', 'Processo de Separação']).any():
            row[area] = 'Andamento'
        elif situacoes_separacao.isin(['Concluído', 'Aguardando conferência', 'Em processo conferência', 'Aguardando conferência volumes']).all():
            row[area] = 'Concluído'
        else:
            row[area] = 'Andamento'  # Caso haja outra situação que não seja "Concluído"
    

    # Verificando a situação para "Conferência Varejo"
    situacoes_conferencia = df[(df['O.C'] == oc) & (df['Descrição (Área de Conferência)'] == 'CONFERENCIA VAREJO 1')]['Situação']
    if situacoes_conferencia.isin(['Enviado para separação', 'Em processo separação', 'Aguardando conferência', 'Em processo conferência']).any():
        row['Conferência Varejo'] = 'Andamento'
    else:
        row['Conferência Varejo'] = 'Concluído'
    
    rows.append(row)

# Criando o novo DataFrame a partir da lista de linhas
new_df = pd.DataFrame(rows)

# Ordenando o DataFrame por O.C
new_df.sort_values(by='O.C', inplace=True)
new_df.reset_index(drop=True, inplace=True)

# Função para estilizar o DataFrame com cores para cada status
def colorize_cells(value):
    if value == 'Andamento':
        return 'background-color: red'
    elif value == 'Concluído':
        return 'background-color: green'
    return ''

# Aplicando a estilização ao novo DataFrame
styled_new_df = new_df.style.applymap(colorize_cells)

# Exibindo o novo DataFrame estilizado
styled_new_df

# %%
import pandas as pd
import numpy as np

def validar_e_substituir(valor):
    if valor in ['SEP VAREJO 01 - (PICKING)', 'SEP CONFINADO', 'SEP VAREJO CONEXOES']:
        return valor
    else:
        return 'SEP VOLUMOSO'
    
# Carregando a planilha com a primeira linha relevante como cabeçalho
df = pd.read_excel('Expedicao_de_Mercadorias_Varejo.xls', header=2)

# Substituindo valores na coluna "Descrição (Area de Separacao)"
df['Descrição (Area de Separacao)'] = df['Descrição (Area de Separacao)'].apply(validar_e_substituir)
# Extraindo todas as áreas únicas da coluna "Descrição (Area de Separacao)"
areas = df['Descrição (Area de Separacao)'].unique()

# Criando um novo DataFrame dinâmico para conter a "O.C", todas as áreas e as colunas de conferência
new_df = pd.DataFrame(columns=['O.C'] + list(areas) + ['Conferência Varejo', 'Conferência Confinado'])

# Preenchendo o novo DataFrame
rows = []

for oc in df['O.C'].unique():
    if pd.isna(oc):  # Verifica se o valor é NaN
        continue
    row = {'O.C': int(oc)}  # Converte O.C para int
    
    # Verificando cada área de separação
    for area in areas:
        situacoes_separacao = df[(df['O.C'] == oc) & (df['Descrição (Area de Separacao)'] == area)]['Situação']
        
        # Define status da área de separação para "Andamento" ou "Concluído"
        if situacoes_separacao.isin(['Enviado para a separação', 'Processo de Separação']).any():
            row[area] = 'Andamento'
        elif situacoes_separacao.isin(['Concluído', 'Aguardando conferência', 'Em processo conferência', 'Aguardando conferência volumes']).all():
            row[area] = 'Concluído'
        else:
            row[area] = 'Andamento'  # Caso haja outra situação que não seja "Concluído"
    
    # Verificando a situação para "Conferência Varejo"
    situacoes_conferencia_varejo = df[(df['O.C'] == oc) & (df['Descrição (Área de Conferência)'] == 'CONFERENCIA VAREJO 1')]['Situação']
    if situacoes_conferencia_varejo.isin(['Enviado para separação', 'Em processo separação', 'Aguardando conferência', 'Em processo conferência']).any():
        row['Conferência Varejo'] = 'Andamento'
    else:
        row['Conferência Varejo'] = 'Concluído'
    
    # Verificando a situação para "Conferência Confinado"
    situacoes_conferencia_confinado = df[(df['O.C'] == oc) & (df['Descrição (Área de Conferência)'] == 'CONFERENCIA CONFINADO')]['Situação']
    if situacoes_conferencia_confinado.isin(['Enviado para separação', 'Em processo separação', 'Aguardando conferência', 'Em processo conferência']).any():
        row['Conferência Confinado'] = 'Andamento'
    else:
        row['Conferência Confinado'] = 'Concluído'
    
    rows.append(row)

# Criando o novo DataFrame a partir da lista de linhas
new_df = pd.DataFrame(rows)

# Ordenando o DataFrame por O.C
new_df.sort_values(by='O.C', inplace=True)
new_df.reset_index(drop=True, inplace=True)

# Função para estilizar o DataFrame com cores para cada status
def colorize_cells(value):
    if value == 'Andamento':
        return 'background-color: red'
    elif value == 'Concluído':
        return 'background-color: green'
    return ''

# Aplicando a estilização ao novo DataFrame
styled_new_df = new_df.style.applymap(colorize_cells)

# Exibindo o novo DataFrame estilizado
styled_new_df

# %%
import pandas as pd
import numpy as np

def validar_e_substituir(valor):
    if valor in ['SEP VAREJO 01 - (PICKING)', 'SEP CONFINADO', 'SEP VAREJO CONEXOES']:
        return valor
    else:
        return 'SEP VOLUMOSO'
    
# Carregando a planilha com a primeira linha relevante como cabeçalho
df = pd.read_excel('Expedicao_de_Mercadorias_Varejo.xls', header=2)

# Substituindo valores na coluna "Descrição (Area de Separacao)"
df['Descrição (Area de Separacao)'] = df['Descrição (Area de Separacao)'].apply(validar_e_substituir)
# Extraindo todas as áreas únicas da coluna "Descrição (Area de Separacao)"
areas = df['Descrição (Area de Separacao)'].unique()

# Criando um novo DataFrame dinâmico para conter a "O.C", todas as áreas e as colunas de conferência
new_df = pd.DataFrame(columns=['O.C'] + list(areas) + ['Conferência Varejo', 'Conferência Confinado', 'Validação Varejo'])

# Preenchendo o novo DataFrame
rows = []

for oc in df['O.C'].unique():
    if pd.isna(oc):  # Verifica se o valor é NaN
        continue
    row = {'O.C': int(oc)}  # Converte O.C para int
    
    # Verificando cada área de separação
    for area in areas:
        situacoes_separacao = df[(df['O.C'] == oc) & (df['Descrição (Area de Separacao)'] == area)]['Situação']
        
        # Define status da área de separação para "Andamento" ou "Concluído"
        if situacoes_separacao.isin(['Enviado para a separação', 'Processo de Separação']).any():
            row[area] = 'Andamento'
        elif situacoes_separacao.isin(['Concluído', 'Aguardando conferência', 'Em processo conferência', 'Aguardando conferência volumes']).all():
            row[area] = 'Concluído'
        else:
            row[area] = 'Andamento'  # Caso haja outra situação que não seja "Concluído"
    
    # Verificando a situação para "Conferência Varejo"
    situacoes_conferencia_varejo = df[(df['O.C'] == oc) & (df['Descrição (Área de Conferência)'] == 'CONFERENCIA VAREJO 1')]['Situação']
    if situacoes_conferencia_varejo.isin(['Enviado para separação', 'Em processo separação', 'Aguardando conferência', 'Em processo conferência']).any():
        row['Conferência Varejo'] = 'Andamento'
    else:
        row['Conferência Varejo'] = 'Concluído'
    
    # Verificando a situação para "Conferência Confinado"
    situacoes_conferencia_confinado = df[(df['O.C'] == oc) & (df['Descrição (Área de Conferência)'] == 'CONFERENCIA CONFINADO')]['Situação']
    if situacoes_conferencia_confinado.isin(['Enviado para separação', 'Em processo separação', 'Aguardando conferência', 'Em processo conferência']).any():
        row['Conferência Confinado'] = 'Andamento'
    else:
        row['Conferência Confinado'] = 'Concluído'
    
    # Verificando a situação para "Validação Varejo"
    situacoes_validacao_varejo = df[(df['O.C'] == oc) & (df['Descrição (Área de Conferência)'] == 'CONFERENCIA VAREJO 1')]['Situação']
    if situacoes_validacao_varejo.isin(['Enviado para separação', 'Em processo separação', 'Aguardando conferência', 'Em processo conferência','Aguardando conferência volumes']).any():
        row['Validação Varejo'] = 'Andamento'
    else:
        row['Validação Varejo'] = 'Concluído'
    
    rows.append(row)

# Criando o novo DataFrame a partir da lista de linhas
new_df = pd.DataFrame(rows)

# Ordenando o DataFrame por O.C
new_df.sort_values(by='O.C', inplace=True)
new_df.reset_index(drop=True, inplace=True)

# Função para estilizar o DataFrame com cores para cada status
def colorize_cells(value):
    if value == 'Andamento':
        return 'background-color: yellow; color: black'
    elif value == 'Concluído':
        return 'background-color: green; color: white'
    return ''

# Aplicando a estilização ao novo DataFrame
styled_new_df = new_df.style.applymap(colorize_cells)

# Exibindo o novo DataFrame estilizado
styled_new_df

# %%
