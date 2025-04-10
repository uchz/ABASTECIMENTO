# %%
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns      
import altair as alt

st.set_page_config(layout="wide")

df = pd.read_excel('archives/PRODUTIVIDADE VALIDAÇÃO.xls')

df.head()

filtro = ['Nome', 'Data', 'Nro. Único Nota']
df = df[filtro]


# Agrupamento
volumes_por_dia = df.groupby('Data')['Nome'].count().reset_index(name='Total de Volumes')

# Converter Data para string
volumes_por_dia['Data'] = volumes_por_dia['Data'].dt.strftime('%d/%m')


# Criar gráfico com Altair
bars = alt.Chart(volumes_por_dia).mark_bar(color='#4C78A8').encode(
    x=alt.X('Data:N', title='Data', sort=None, axis=alt.Axis(labelAngle=0)),
    y=alt.Y('Total de Volumes:Q', title='Total de Volumes'),
    tooltip=['Data:N', 'Total de Volumes:Q']
)

# Rótulo em cima das barras
text = bars.mark_text(
    align='center',
    baseline='bottom',
    dy=-5,  # desloca o texto pra cima da barra
    color='white'
).encode(
    text='Total de Volumes:Q'
)

# Combinar gráfico e rótulo
chart = (bars + text).properties(
    title=alt.TitleParams(
    text='Volumes por Dia',
    fontSize=20,
    ),
    width=700,
    height=400
)

st.altair_chart(chart, use_container_width=True)


filtro = ['DAVI.SILVA','IGOR.DERZE', 'LUIS.ALMEIDA', 'LEONARDO.PIMENTEL', 'LAURO.SILVA', 'GEOVANI.SANTOS', 'GILVAN.AYRIM']


df_equipe = df[df['Nome'].isin(filtro)]
volumes_por_pessoa = df_equipe.groupby('Nome').size().reset_index(name='Total de Volumes')

# Gráfico de barras
bars = alt.Chart(volumes_por_pessoa).mark_bar(color='#4C78A8').encode(
    x=alt.X('Nome:N', title='Validador', sort='-y', axis=alt.Axis(labelAngle=-45)),
    y=alt.Y('Total de Volumes:Q', title='Total de Volumes'),
    tooltip=['Nome:N', 'Total de Volumes:Q']
)

# Rótulo de dados
text = bars.mark_text(
    align='center',
    baseline='bottom',
    dy=-5,
    color='white',
    font='Arial',
    fontSize=10
).encode(
    text='Total de Volumes:Q'
)

# Combina tudo
chart = (bars + text).properties(
    title=alt.TitleParams(
        text='Total de Volumes por Validador 31/03 a 04/04',
        fontSize=20,
        color='white'
    ),
    width=700,
    height=400
)

st.altair_chart(chart, use_container_width=True)

apanhas = pd.DataFrame({
    'Data': ['31-03-2025','01/04/2025', '02/04/2025', '03/04/2025', '04/04/2025'],
    'Apanhas': ['8566', '7264', '7860', '8111', '6476']
})

# Padronizar separador para "/"
apanhas['Data'] = apanhas['Data'].str.replace('-', '/', regex=False)

# Converter para datetime (com ano incluso)
apanhas['Data'] = pd.to_datetime(apanhas['Data'], dayfirst=True)

# Converter Apanhas para numérico
apanhas['Apanhas'] = apanhas['Apanhas'].astype(int)

# Formatar data apenas para exibição no gráfico
apanhas['Data_label'] = apanhas['Data'].dt.strftime('%d/%m')

# Criar gráfico de barras
bars = alt.Chart(apanhas).mark_bar(color='#4C78A8').encode(
    x=alt.X('Data_label:N', title='Data'),
    y=alt.Y('Apanhas:Q', title='Volumes Apanhados')
)

# Adicionar rótulos
text = bars.mark_text(
    align='center',
    baseline='bottom',
    dy=-5,
    color='white'
).encode(
    text='Apanhas:Q'
)

# Combinar e estilizar
chart = (bars + text).properties(
    title='Total de Apanha por Dia',
    width=700,
    height=400
).configure_title(
    fontSize=20
)

chart




# %%
import streamlit as st

# Sempre primeiro!!


import pandas as pd
import altair as alt

# Dados
df = pd.read_excel('archives/PRODUTIVIDADE VALIDAÇÃO.xls')
df = df[['Nome', 'Data', 'Nro. Único Nota']]

# Tratamento
df['Data'] = pd.to_datetime(df['Data'], dayfirst=True)
df['Data_label'] = df['Data'].dt.strftime('%d/%m')
total_validado = df['Nro. Único Nota'].count()

# Separadores
produtividade_por_pessoa = df_equipe.groupby('Nome')['Nro. Único Nota'].count().reset_index(name='Total')
produtividade_por_pessoa = produtividade_por_pessoa.sort_values(by='Total', ascending=False)

# Validados por dia
produtividade_por_dia = df.groupby('Data_label')['Nro. Único Nota'].count().reset_index(name='Total Validado')

# Apanhas
apanhas = pd.DataFrame({
    'Data': ['31-03-2025', '01/04/2025', '02/04/2025', '03/04/2025', '04/04/2025'],
    'Apanhas': ['8566', '7264', '7860', '8111', '6476']
})
apanhas['Data'] = apanhas['Data'].str.replace('-', '/', regex=False)
apanhas['Data'] = pd.to_datetime(apanhas['Data'], dayfirst=True)
apanhas['Data_label'] = apanhas['Data'].dt.strftime('%d/%m')
apanhas['Apanhas'] = apanhas['Apanhas'].astype(int)

# Gráfico de produtividade por pessoa
bars_pessoa = alt.Chart(produtividade_por_pessoa).mark_bar().encode(
    x=alt.X('Nome:N', sort='-y', title='Separador'),
    y=alt.Y('Total:Q', title='Total Validado'),
    tooltip=['Nome', 'Total']
)

text_pessoa = bars_pessoa.mark_text(
    align='center',
    baseline='bottom',
    dy=-5,
    color='white'
).encode(
    text='Total:Q'
)

grafico_pessoa = (bars_pessoa + text_pessoa).properties(
    width=400,
    height=300,
    title=alt.TitleParams(text='Demanda por Validador', fontSize=20)
)

# Gráfico de produtividade por dia
bars_dia = alt.Chart(produtividade_por_dia).mark_bar().encode(
    x=alt.X('Data_label:N', title='Data'),
    y=alt.Y('Total Validado:Q', title='Total Validado'),
    tooltip=['Data_label', 'Total Validado']
)

text_dia = bars_dia.mark_text(
    align='center',
    baseline='bottom',
    dy=-5,
    color='white'
).encode(
    text='Total Validado:Q'
)

grafico_dia = (bars_dia + text_dia).properties(
    width=400,
    height=300,
    title=alt.TitleParams(text='Validados por Dia', fontSize=20)
)

# Gráfico de apanhas por dia
bars_apanhas = alt.Chart(apanhas).mark_bar(color='orange').encode(
    x=alt.X('Data_label:N', title='Data'),
    y=alt.Y('Apanhas:Q', title='Demandas Apanhas'),
    tooltip=['Data_label', 'Apanhas']
)

text_apanhas = bars_apanhas.mark_text(
    align='center',
    baseline='bottom',
    dy=-5,
    color='white'
).encode(
    text='Apanhas:Q'
)

grafico_apanhas = (bars_apanhas + text_apanhas).properties(
    width=400,
    height=300,
    title=alt.TitleParams(text='Demandas Apanhas por Dia', fontSize=20)
)

# Dashboard
st.title('Dashboard de Validação')

# Cartão total
st.write(" ")

# Layout com colunas
col1, col2 = st.columns(2)

# Primeira coluna
with col1:
    st.markdown(
        f"""
        <div style="
            padding: 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.2);
            text-align: left;
        ">
            <h2 style="color: white; margin-bottom: 10px;">Total Validado</h2>
            <p style="font-size: 48px; color: white; font-weight: bold;">{total_validado}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.altair_chart(grafico_pessoa, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.altair_chart(grafico_dia, use_container_width=True)

# Segunda coluna
with col4:
    st.altair_chart(grafico_apanhas, use_container_width=True)

