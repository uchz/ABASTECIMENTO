import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("Menu")

# Título da Aplicação
st.title('Análise de Abastecimentos e Desempenho dos Operadores')

# Criação das abas
tab1, tab2, tab3 = st.tabs(["Abastecimento", "Desempenho dos Operadores", "Separação"])

with tab1:
    st.header("Abastecimentos")
    
    # Upload do arquivo de abastecimento
    df_abastecimento = pd.read_excel('abastecimento-por-oc.xls', header=2)
    df_abastecimento = df_abastecimento[['CODPROD', 'DESCDESTINO', 'AREA DE SEPA ENDEREçO DESTINO']]
    df_abastecimento = df_abastecimento.drop_duplicates(subset=['CODPROD', 'DESCDESTINO'])
    df_abastecimento.sort_values(by='DESCDESTINO', inplace=True)

    @st.cache_data
    def validar_e_substituir(valor):
        if valor in ['SEP VAREJO 01 - (PICKING)', 'SEP CONFINADO', 'SEP CONEXOES']:
            return valor
        else:
            return 'SEP VOLUMOSO'

    df_abastecimento['AREA DE SEPA ENDEREçO DESTINO'] = df_abastecimento['AREA DE SEPA ENDEREçO DESTINO'].apply(validar_e_substituir)

    st.subheader('Abastecimentos por Área')
    st.write(df_abastecimento.groupby('AREA DE SEPA ENDEREçO DESTINO')['CODPROD'].count())

with tab2:
    st.header("Desempenho dos Operadores")
    
    # Carga e Processamento dos Dados de Desempenho dos Operadores
    df_desempenho = pd.read_excel('Gestao_Produtividade_detalhada_WMS_2.xlsx', header=2)

    # Definindo fuso
    fuso_horario = 'America/Sao_Paulo'

    @st.cache_data
    def data():
        data_atual = datetime.now(pytz.timezone(fuso_horario)).strftime('%d-%m-%Y')
        hora_atual = datetime.now(pytz.timezone(fuso_horario)).strftime('%H:%M')
        return data_atual, hora_atual

    data_atual, hora_atual = data()

    df_desempenho['Dt./Hora Inicial'] = pd.to_datetime(df_desempenho['Dt./Hora Inicial'], format='%d/%m/%Y %H:%M:%S')
    df_desempenho['Hora'] = df_desempenho['Dt./Hora Inicial'].dt.hour
    df_desempenho['Hora'] = pd.to_datetime(df_desempenho['Hora'], format='%H').dt.time

    tipo = ['PREVENTIVO', 'CORRETIVO', 'TRANSFERÊNCIA']
    empilhadores = ['JOSIMAR.DUTRA', 'CROI.MOURA', 'INOEL.GUIMARAES', 'ERICK.REIS', 'CLAUDIO.MARINS']

    df_desempenho = df_desempenho[df_desempenho['Tipo '].isin(tipo)]
    df_desempenho = df_desempenho[df_desempenho['Usuário'].isin(empilhadores)]
    corretivo_preventivo = df_desempenho[df_desempenho['Tipo '].isin(['CORRETIVO', 'PREVENTIVO'])]

    contagem_tipos = corretivo_preventivo.groupby('Usuário')['Tipo '].count().sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=600)
    bars = contagem_tipos.plot(kind='bar', color='red', ax=ax)

    for bar in bars.patches:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3, bar.get_height(), 
                ha='center', va='bottom', fontsize=8)
    plt.title('Total de Corretivos + Preventivos por Empilhador')
    plt.xlabel('Empilhador')
    plt.ylabel('Total de Abastecimentos')
    plt.xticks(rotation=0)
    st.pyplot(plt)

    contagem_tipos = df_desempenho.groupby(['Usuário', 'Tipo ']).size().unstack(fill_value=0)
    contagem_tipos['Total'] = contagem_tipos.sum(axis=1)
    contagem_tipos.loc['Total'] = contagem_tipos.sum()

    st.title('Total de tarefas por Empilhador')
    st.write('Tarefas por empilhador:')
    st.dataframe(contagem_tipos)

    cores = sns.color_palette('afmhot', len(contagem_tipos.columns[:-1]))
    tipos = contagem_tipos.columns[:-1]

    fig, ax = plt.subplots()

    index = range(len(contagem_tipos.index)-1)
    bar_width = 0.2
    for i, (tipo, cor) in enumerate(zip(tipos, cores)):
        ax.bar([x + i * bar_width for x in index], contagem_tipos.iloc[:-1][tipo], width=bar_width, label=tipo, color=cor)

    ax.set_xlabel('Empilhador')
    ax.set_ylabel('Quantidade')
    ax.set_title('Abastecimentos por Empilhador')
    ax.set_xticks(index)
    ax.set_xticklabels(contagem_tipos.index[:-1], rotation=90)
    ax.legend()

    st.pyplot(fig)

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

    tarefas_pivot = tarefas_pivot.drop(columns='Total')
    total_hora_data = tarefas_pivot.loc['Total P/ Hora']

    plt.figure(figsize=(12, 6))
    plt.plot(total_hora_data.index, total_hora_data.values, marker='o', linestyle='-', color='black', label='Total de Tarefas')

    for i, (hora, total) in enumerate(total_hora_data.items()):
        plt.annotate(f'{int(total)}', (hora, total), textcoords="offset points", xytext=(0, 10), ha='center')

    plt.title('Total de Tarefas por Hora')
    plt.xlabel('Hora')
    plt.ylabel('Quantidade Total de Tarefas')
    plt.xticks(rotation=45)
    plt.legend(loc='upper left')
    plt.grid(True)
    plt.tight_layout()
    st.pyplot(plt)

with tab3:
    st.header("Separação")
    st.write("Conteúdo de separação aqui...")

