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
    
with st.sidebar:
    st.header("📂 Enviar arquivo")
    arquivo = st.file_uploader("Selecione o arquivo XLS", type=["xls", "xlsx"])

if arquivo is None:
    st.warning("Adicione o arquivo para continuar.")
    st.stop()



df = pd.read_excel(arquivo, header=2)
df['NUTAREFA'] = df['NUTAREFA'].astype(str).str.replace('.0', '', regex=False).replace('nan', '') + ','


def definir_cancela(rua):
    if 1 <= rua <= 23:
        return 1
    elif 24 <= rua <= 48:
        return 2
    else:
        return 3

# Filtros
df47 = df[df['DESCDESTINO'].str.contains('5.47', na=False)]
df = df[~df['DESCDESTINO'].str.contains('CNX', na=False)]
df = df[~df['DESCDESTINO'].str.contains('47', na=False)]
df47 = df47[~df47['DESCDESTINO'].str.contains('5.46', na=False)]
df = df[~df['AREA DE SEPA ENDEREçO DESTINO'].str.contains('PNC|VOLUMOSO', na=False)]

# Normalização
df['DESCDESTINO'] = (
    df['DESCDESTINO']
    .astype(str)
    .str.strip()
    .str.replace(',', '.')
)

# Extrai rua
df['Rua'] = df['DESCDESTINO'].str.extract(r'46\.0*?(\d{2})', expand=False)
df = df.fillna(0)
df['Cancela'] = df['Rua'].astype(int).apply(definir_cancela)

df47['Rua'] = df47['DESCDESTINO'].str.extract(r'47\.0*?(\d{2})', expand=False)
df47 = df47.fillna(0)
df47['Cancela'] = 47

# Distribui por cancela
c1 = df.loc[df['Cancela'] == 1, 'NUTAREFA'].reset_index(drop=True)
c2 = df.loc[df['Cancela'] == 2, 'NUTAREFA'].reset_index(drop=True)
c3 = df.loc[df['Cancela'] == 3, 'NUTAREFA'].reset_index(drop=True)
c47 = df47.loc[df47['Cancela'] == 47, 'NUTAREFA'].reset_index(drop=True)

df_tarefas = pd.concat([c1, c2, c3, c47], axis=1)
df_tarefas.columns = ['Cancela 1', 'Cancela 2', 'Cancela 3', 'Cancela 47']
df_tarefas = df_tarefas.fillna("")

for col in df_tarefas.columns:
    df_tarefas[col] = (
        df_tarefas[col]
        .astype(str)
        .str.replace('.0', '', regex=False)
        .replace('nan', '')
        .replace('None', '')
    )

st.subheader("📊 Tarefas por Cancela")
st.write(df_tarefas)

