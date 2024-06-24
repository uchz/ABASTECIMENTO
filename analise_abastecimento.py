## ANALISAR A MÉDIA DA DURAÇÃO DAS TAREFAS
## ANALISAR QUANTAS TAREFAS FEITAS NA NOITE
## 

# %% 
import pandas as pd

df = pd.read_excel('produtividade_abastecimento.xlsx', header=2)
# %%
df.rename(columns={'Tipo ': 'Tipo'}, inplace=True)
# %%
tipo = ['PREVENTIVO','CORRETIVO']

df = df[df['Tipo'].isin(tipo)]
# %%
df.Usuário.unique()
# %%
empilhadores = ['CLAUDIO.MARINS', 'ERICK.REIS', 'CROI.MOURA',
                 'JOSIMAR.DUTRA', 'INOEL.GUIMARAES' ]

df = df[df['Usuário'].isin(empilhadores)]
# %%
df.info()
# %%
df['Dt./Hora Inicial'] = pd.to_datetime(df['Dt./Hora Inicial'])
# %%
df.info()
# %%
df['Hora Final'] = df['Dt./Hora Final'].dt.time


# %%
df.head()
# %%
df.sort_values(by='Dt./Hora Inicial', ascending=True, inplace=True)
# %%
media_duracao = df['Time'].mean()
# %%
media_duracao_horas = media_duracao.total_seconds() // 3600
media_duracao_minutos = (media_duracao.total_seconds() % 3600) // 60
# %%
print(f'Média da duração: {int(media_duracao_horas)}h {int(media_duracao_minutos)}m')
# %%
media_empilhador = df.groupby('Usuário')['Time'].mean()
# %%
media = media_empilhador.apply( lambda x: f"{int(x.total_seconds() // 3600)}h {int((x.total_seconds() % 3600) // 60)}m")
# %%
media_empilhador
# %%
import matplotlib.pyplot as plt

# Plotar os dados
plt.figure(figsize=(10, 6))
ax = media_empilhador.plot(kind='bar', color='red')
plt.xlabel('Empilhador')
plt.ylabel('Média de Duração (Minutos)')
plt.title('Média de Duração das Tarefas por Empilhador')
plt.xticks(rotation=0)
plt.grid(axis='y')

for i in ax.containers:
    ax.bar_label(i, label_type='edge')
# Exibir o gráfico
plt.show()
# %%
