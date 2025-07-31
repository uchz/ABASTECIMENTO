#%%
# ## ANALISAR A MÉDIA DA DURAÇÃO DAS TAREFAS
# ## ANALISAR QUANTAS TAREFAS FEITAS NA NOITE
# ## 

import pandas as pd 

df = pd.read_excel('conf_abastec.xls')



# %%
def ajustar_data_operacional(df, coluna_datahora):
    # Converte a coluna para datetime
    df[coluna_datahora] = pd.to_datetime(df[coluna_datahora], dayfirst=True)

    # Cria nova coluna com data ajustada
    df['Data Operacional'] = df[coluna_datahora].apply(lambda x: x.date() if x.time() >= pd.to_datetime("18:00:00").time() else (x - pd.Timedelta(days=1)).date())

    return df

df = ajustar_data_operacional(df, 'Data Inicial')
df['Data Operacional'] = pd.to_datetime(df['Data Operacional'])
# %%
df['Dia'] = df['Data Operacional'].dt.day
df['Mes'] = df['Data Operacional'].dt.month
df['Hora'] = df['Data Inicial'].dt.strftime('%H:%M')
# %%

df.groupby('Dia')['Descição'].count().reset_index()
# %%
import matplotlib.pyplot as plt

# Agrupa e conta as ocorrências por dia
df_dia = df.groupby('Dia')['Descição'].count().reset_index()

# Renomeia a coluna para facilitar o uso
df_dia = df_dia.rename(columns={'Descição': 'Total'})

# Plota o gráfico de linha
plt.figure(figsize=(10, 5))
plt.plot(df_dia['Dia'], df_dia['Total'], marker='o', color='blue')
plt.title('Eventos por Dia Operacional')
plt.xlabel('Dia Operacional')
plt.ylabel('Total de Eventos')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
# %%
