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
import pandas as pd



def ajustar_data_operacional(df, coluna_datahora):
    # Converte a coluna para datetime
    df[coluna_datahora] = pd.to_datetime(df[coluna_datahora], dayfirst=True)

    # Define limites do turno
    hora_inicio = 19  # 19:00
    hora_fim = 6      # até 06:00 do dia seguinte

    # Criar Data Operacional correta
    def definir_data_operacional(x):
        if x.hour >= hora_inicio:  
            # Se for depois das 19h, pertence ao próprio dia
            return x.date()
        elif x.hour < hora_fim:    
            # Se for antes das 06h, pertence ao dia anterior
            return (x - pd.Timedelta(days=1)).date()
        else:
            # Caso fora do intervalo, retorna None (não pertence ao turno)
            return None

    df['Data Operacional'] = df[coluna_datahora].apply(definir_data_operacional)

    # Filtra só quem tem Data Operacional (dentro do turno)
    df_filtrado = df[df['Data Operacional'].notna()].copy()

    return df_filtrado
# %%


def carregar_dados_onedrive():
    caminho = r"C:\\Users\\luis.silva\Documents\\OneDrive - LLE Ferragens\\MFC\\geral_pedidos.xlsx"
    df = pd.read_excel(caminho)
    return df
df = carregar_dados_onedrive()
df = ajustar_data_operacional(df, 'Data Início')

# %%
df.to_excel('Produtividade Separações.xlsx')
# %%
df[['Data Início', 'Data Operacional']].head()
# %%
