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
