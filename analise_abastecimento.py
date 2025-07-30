#%%
# ## ANALISAR A MÉDIA DA DURAÇÃO DAS TAREFAS
# ## ANALISAR QUANTAS TAREFAS FEITAS NA NOITE
# ## 

import pandas as pd 

df = pd.read_excel('conf_abastec.xls')
df


# %%
df['Data Inicial']
# %%
itens = df.groupby('Descição')['Descição'].count().reset_index(name='Total')
# %%
itens.sort_values(by='Total', ascending=False)
# %%
