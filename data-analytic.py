import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import matplotlib.pyplot as plt


st.title('Análise de Abastecimentos e Desempenho dos Operadores')

# Upload do arquivo de abastecimento
uploaded_file_abastecimento = st.file_uploader("Escolha um arquivo Excel para Abastecimentos", type="xls")
if uploaded_file_abastecimento:
    df_abastecimento = pd.read_excel(uploaded_file_abastecimento, header=2)
    df_abastecimento = df_abastecimento[['CODPROD', 'DESCDESTINO', 'AREA DE SEPA ENDEREçO DESTINO']]
    df_abastecimento = df_abastecimento.drop_duplicates(subset=['CODPROD', 'DESCDESTINO'])
    df_abastecimento.sort_values(by='DESCDESTINO', inplace=True)

    def validar_e_substituir(valor):
        if valor in ['SEP VAREJO 01 - (PICKING)', 'SEP CONFINADO', 'SEP CONEXOES']:
            return valor
        else:
            return 'SEP VOLUMOSO'

    df_abastecimento['AREA DE SEPA ENDEREçO DESTINO'] = df_abastecimento['AREA DE SEPA ENDEREçO DESTINO'].apply(validar_e_substituir)

    st.subheader('Contagem de Abastecimentos por Área')
    st.write(df_abastecimento.groupby('AREA DE SEPA ENDEREçO DESTINO')['CODPROD'].count())

# Upload do arquivo de desempenho dos operadores
uploaded_file_desempenho = st.file_uploader("Escolha um arquivo Excel para Desempenho dos Operadores", type="xlsx")
if uploaded_file_desempenho:
    df_desempenho = pd.read_excel(uploaded_file_desempenho, header=2)

    # Definindo fuso
    fuso_horario = 'America/Sao_Paulo'

    # Função para trazer data e hora atualizada
    def data():
        data_atual = datetime.now(pytz.timezone(fuso_horario)).strftime('%d-%m-%Y')
        hora_atual = datetime.now(pytz.timezone(fuso_horario)).strftime('%H:%M')
        return data_atual, hora_atual

    data_atual, hora_atual = data()

    df_desempenho['Dt./Hora Inicial'] = pd.to_datetime(df_desempenho['Dt./Hora Inicial'], format='%d/%m/%Y %H:%M:%S')
    df_desempenho['Hora'] = df_desempenho['Dt./Hora Inicial'].dt.hour
    df_desempenho['Hora'] = pd.to_datetime(df_desempenho['Hora'], format='%H').dt.time

if uploaded_file_desempenho:
    tipo = ['PREVENTIVO', 'CORRETIVO', 'TRANSFERÊNCIA']
    empilhadores = ['JOSIMAR.DUTRA', 'CROI.MOURA', 'INOEL.GUIMARAES', 'ERICK.REIS', 'CLAUDIO.MARINS']

    df_desempenho = df_desempenho[df_desempenho['Tipo '].isin(tipo)]
    df_desempenho = df_desempenho[df_desempenho['Usuário'].isin(empilhadores)]

    corretivo_preventivo = df_desempenho[df_desempenho['Tipo '].isin(['CORRETIVO', 'PREVENTIVO'])]

    # Agrupando os dados pelo 'Usuário' e contando os tipos
    contagem_tipos = corretivo_preventivo.groupby('Usuário')['Tipo '].count().sort_values(ascending=False)

    # Plotando o gráfico de barras
    st.subheader('Total de Corretivos + Preventivos por Empilhador')
    plt.figure(figsize=(10, 6), dpi=600)
    contagem_tipos.plot(kind='bar', color='red')
    plt.title('Total de Corretivos + Preventivos por Empilhador')
    plt.xlabel('Empilhador')
    plt.ylabel('Total de Abastecimentos')
    plt.xticks(rotation=0)
    st.pyplot(plt)

    # Análise das tarefas por hora
    tarefas_por_hora = df_desempenho.groupby(['Usuário', 'Hora']).size().reset_index(name='Qtde Tarefas')
    tarefas_por_hora['Hora'] = tarefas_por_hora['Hora'].apply(lambda x: x.strftime('%H:%M'))
    tarefas_por_hora = tarefas_por_hora.sort_values(by=['Usuário', 'Hora'])
    tarefas_por_hora['Ordenacao'] = tarefas_por_hora['Hora'].apply(lambda x: (pd.to_datetime(str(x), format='%H:%M') + pd.DateOffset(hours=5)).time())
    tarefas_por_hora = tarefas_por_hora.sort_values(by=['Usuário', 'Ordenacao'])
    tarefas_por_hora = tarefas_por_hora.drop('Ordenacao', axis=1)
    tarefas_pivot = tarefas_por_hora.pivot_table(index='Usuário', columns='Hora', values='Qtde Tarefas', fill_value=0)
    tarefas_pivot = tarefas_pivot.reindex(columns=sorted(tarefas_pivot.columns, key=lambda x: (pd.to_datetime(str(x), format='%H:%M') + pd.DateOffset(hours=5)).time()))
    sum_values = tarefas_pivot.sum()
    tarefas_pivot.loc['Total P/ Hora'] = sum_values
    tarefas_pivot['Total'] = tarefas_pivot.sum(axis=1)
    tarefas_pivot['Total'] = tarefas_pivot['Total'].astype(int)

    st.subheader('Tarefas por Hora')
    st.write(tarefas_pivot)

    # Gráfico de total de tarefas por hora
    tarefas_pivot = tarefas_pivot.drop(columns='Total')
    total_hora_data = tarefas_pivot.loc['Total P/ Hora']

    plt.figure(figsize=(12, 6))
    plt.plot(total_hora_data.index, total_hora_data.values, marker='o', linestyle='-', color='r', label='Total de Tarefas')
       # Adicionar rótulos aos pontos de dados
    for i, value in enumerate(total_hora_data.values):
        plt.text(total_hora_data.index[i], value, str(value), ha='center', va='bottom')
    plt.title('Total de Tarefas por Hora')
    plt.xlabel('Hora')
    plt.ylabel('Quantidade Total de Tarefas')
    plt.xticks(rotation=45)
    plt.legend(loc='upper left')
    plt.grid(True)
    plt.tight_layout()


             
    st.pyplot(plt)

