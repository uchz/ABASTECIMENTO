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

st.header('MFC')

arquivo = st.file_uploader("Selecione um arquivo CSV", type=['csv'])

if arquivo is not None:
    df_mfc = pd.read_csv(arquivo, sep=';')  # ou pd.read_csv(arquivo) para CSV
    st.success("Arquivo carregado com sucesso!")
    # st.dataframe(df_mfc)

# df_mfc = pd.read_csv('archives/data (4).csv', sep=';')
# df_mfc['Hora Inducao'] = pd.to_datetime(df_mfc['Hora Inducao'])
# df_mfc.info()

    import plotly.express as px

    # Gráfico de barras com rótulos
    fig = px.bar(
        df_mfc,
        x="Hora Inducao",
        y="Quantidade",
        text="Quantidade",  # Rótulo
        title="Quantidade por Hora de Indução",
        color_discrete_sequence=["#d62727"]
    )

    fig.update_traces(textposition='outside')  # 'inside', 'outside', 'auto'
    fig.update_layout(
        xaxis_title="Hora de Indução",
        yaxis_title="Quantidade",
        width=900,
        height=500,
        # template="plotly_dark",
        xaxis_tickangle=-45
        
    )

    st.plotly_chart(fig, use_container_width=True)
 