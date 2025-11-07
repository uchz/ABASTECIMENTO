import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

import re

def definir_cancela(rua):
    if 1 <= rua <= 23:
        return 1
    elif 24 <= rua <= 48:
        return 2
    else:
        return 3


df = pd.read_excel('archives/abastecimento-por-oc.xls', header=2)


df = df[~df['DESCDESTINO'].str.contains('CNX', na=False)]
df = df[~df['AREA DE SEPA ENDEREçO DESTINO'].str.contains('PNC|VOLUMOSO', na=False)]

# --- 1️⃣ normaliza strings ---
df['DESCDESTINO'] = (
    df['DESCDESTINO']
    .astype(str)              # garante que é string
    .str.strip()              # remove espaços e \n
    .str.replace(',', '.')    # troca vírgula por ponto, se existir
)



# --- 3️⃣ extrai o número após "46." ---
df['Rua'] = df['DESCDESTINO'].str.extract(r'46\.0*?(\d{2})', expand=False)
df = df.fillna(0)
df['Cancela'] = df['Rua'].astype(int).apply(definir_cancela)


c1 = df.loc[df['Cancela'] == 1, 'NUTAREFA'].reset_index(drop=True)
c2 = df.loc[df['Cancela'] == 2, 'NUTAREFA'].reset_index(drop=True)
c3 = df.loc[df['Cancela'] == 3, 'NUTAREFA'].reset_index(drop=True)

df_tarefas = pd.concat([c1, c2, c3], axis=1)


df_tarefas.columns = ['Cancela 1', 'Cancela 2', 'Cancela 3']

df_tarefas = df_tarefas.fillna("")

# converte cada coluna em string, removendo o .0
for col in df_tarefas.columns:
    df_tarefas[col] = (
        df_tarefas[col]
        .astype(str)
        .str.replace('.0', '', regex=False)  # remove o .0
        .replace('nan', '')                  # remove 'nan' caso apareça
        .replace('None', '')
    )




st.write(df_tarefas)
