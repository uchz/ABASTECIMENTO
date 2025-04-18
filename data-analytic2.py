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




def hora_para_float(hora_str):
    if isinstance(hora_str, str):  # Verifica se o valor é string
        h, m = map(int, hora_str.split(':'))
        return h + m / 60.0  # Converte minutos para fração de hora
    return hora_str  # Se já for número, retorna como está

# Título da Aplicação
st.title('Acompanhamento Operação Noturno')

#st.markdown('ATUALIZAÇÕES AS: **21:15** / 22:15 / 23:15 / 00:15 / 01:15 / 02:15 / 03:15 / 04:15')
# Criação das abas
tab5, tab1, tab2, tab3, tab4, tab6  = st.tabs(['Apanhas',"Abastecimento", "Volumoso", "Varejo", "Confinado", 'Conexões'])



with tab1:

    st.header("Abastecimentos")

    #Upload do arquivo de abastecimento
    df_abastecimento = pd.read_excel('abastecimento-por-oc.xls', header=2)
    df_abastecimento = df_abastecimento[['CODPROD', 'DESCDESTINO', 'AREA DE SEPA ENDEREçO DESTINO']]
    df_abastecimento = df_abastecimento.drop_duplicates(subset=['CODPROD', 'DESCDESTINO'])
    df_abastecimento.sort_values(by='DESCDESTINO', inplace=True)

    @st.cache_data
    def validar_e_substituir(valor):
        if valor in ['SEP VAREJO 01 - (PICKING)', 'SEP CONFINADO', 'SEP VAREJO CONEXOES']:
            return valor
        else:
            return 'SEP VOLUMOSO'

    df_abastecimento['AREA DE SEPA ENDEREçO DESTINO'] = df_abastecimento['AREA DE SEPA ENDEREçO DESTINO'].apply(validar_e_substituir)

    df_abastecimento.rename(columns={"AREA DE SEPA ENDEREçO DESTINO" : "Area", 'CODPROD' : 'Qtd Códigos'}, inplace=True)

    st.subheader('Abastecimentos por Área')

    abastecimento_area = df_abastecimento.groupby('Area')['Qtd Códigos'].count().reset_index()

    total = abastecimento_area['Qtd Códigos'].sum()
    total_row = pd.DataFrame({'Area': ['Total'], 'Qtd Códigos': [total]})
    abastecimento_area = pd.concat([abastecimento_area, total_row], ignore_index=True)

    abastecimento_area = abastecimento_area.set_index('Area')
    
    st.dataframe(abastecimento_area)


    st.title("Desempenho dos Operadores")

    # Carga e Processamento dos Dados de Desempenho dos Operadores
    df_desempenho = pd.read_excel('Gestao_Produtividade_detalhada_WMS_2.xlsx', header=2)

    df = df_desempenho

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
    empilhadores = ['JOSIMAR.DUTRA', 'CROI.MOURA', 'LUIZ.BRAZ', 'ERICK.REIS','IGOR.VIANA', 'CLAUDIO.MARINS', 'THIAGO.SOARES', 'LUCAS.FARIAS', 'FABRICIO.SILVA']

    df_desempenho = df_desempenho[df_desempenho['Tipo '].isin(tipo)]
    df_desempenho = df_desempenho[df_desempenho['Usuário'].isin(empilhadores)]
    corretivo_preventivo = df_desempenho[df_desempenho['Tipo '].isin(['CORRETIVO', 'PREVENTIVO'])]

    contagem_tipos = corretivo_preventivo.groupby('Usuário')['Tipo '].count().sort_values(ascending=False)


    contagem_tipos = df_desempenho.groupby(['Usuário', 'Tipo ']).size().unstack(fill_value=0)
    contagem_tipos['Total'] = contagem_tipos.sum(axis=1)
    contagem_tipos.loc['Total'] = contagem_tipos.sum()

    st.header('Abastecimentos por Empilhador')
    st.dataframe(contagem_tipos)

    cores = sns.color_palette('afmhot', len(contagem_tipos.columns[:-1]))
    tipos = contagem_tipos.columns[:-1]

    # fig, ax = plt.subplots()

    # index = range(len(contagem_tipos.index)-1)
    # bar_width = 0.2
    # for i, (tipo, cor) in enumerate(zip(tipos, cores)):
    #     ax.bar([x + i * bar_width for x in index], contagem_tipos.iloc[:-1][tipo], width=bar_width, label=tipo, color=cor)

    # ax.set_xlabel('Empilhador')
    # ax.set_ylabel('Quantidade')
    # ax.set_title('Abastecimentos por Empilhador')
    # ax.set_xticks(index)
    # ax.set_xticklabels(contagem_tipos.index[:-1], rotation=90)
    # ax.legend()

        # Agrupando por 'Usuário' e 'Tipo', e criando a tabela de contagem
    contagem_tipos = df_desempenho.groupby(['Usuário', 'Tipo ']).size().unstack(fill_value=0)


    # Transformando os dados para formato long (necessário para Altair)
    df_long = contagem_tipos.reset_index().melt(id_vars='Usuário', var_name='Tipo', value_name='Quantidade')

    # Criando o gráfico de barras com Altair
    bar_chart = alt.Chart(df_long).mark_bar().encode(
        x=alt.X('Usuário:N', title='Empilhador'),
        y=alt.Y('Quantidade:Q', title='Quantidade'),
        color=alt.Color('Tipo:N'),  # O Altair define automaticamente as cores
    ).properties(
        title='Abastecimentos por Empilhador'
    ).configure_axis(
        labelAngle=90  # Rotaciona os labels do eixo X
    )

    # Exibindo no Streamlit o gráfico sem a linha 'Total'
    st.altair_chart(bar_chart, use_container_width=True)

    # Exibindo a tabela completa, incluindo a linha 'Total'
    # st.write("Tabela de contagem com Totais:")


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



    st.subheader('Evolução p/ Hora')

    plt.figure(figsize=(13, 7), dpi=800 )
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



with tab2:
    # Título da Aplicação
    st.subheader('Quantidade de Pedidos Pendentes por Rua')

    expedicao = pd.read_excel('Expedicao_de_Mercadorias.xls', header=2)

    colunas = ['Nro. Nota', 'Conferente', 'Enviado p/ Doca', 'Descrição (Área de Conferência)', 'Nro. Sep.', 'Nro. Único',
            'Descrição (Doca do WMS)', 'Cód. Doca', 'Peso Bruto', 'M3 Bruto', 'Área', 'Cód. Emp OC', 'Cód. Área Sep', 'Triagem Realizada', 'Cod. Conferente' ]

    expedicao.drop(columns=colunas, inplace=True)

    expedicao = expedicao[expedicao['Situação'] == 'Enviado para separação']
    expedicao['O.C'] = expedicao['O.C'].astype(int)
    expedicao['O.C'] = expedicao['O.C'].astype(str)

    status = expedicao.groupby('Descrição (Area de Separacao)').agg(Qtd_Ocs = ('O.C', 'count'), OC = ('O.C', 'min')).reset_index()


    st.write(status)

    #df = pd.read_excel('Gestao_Produtividade_detalhada_WMS_2.xlsx', header=2)

    #Função para trazer data e hora atualizada
    @st.cache_data
    def data ():

        data_atual = datetime.now(pytz.timezone(fuso_horario)).strftime('%d-%m-%Y')
        hora_atual = datetime.now(pytz.timezone(fuso_horario)).strftime('%H:%M')

        return data_atual, hora_atual

    data, hora = data()

    df['Dt./Hora Inicial'] = pd.to_datetime( df['Dt./Hora Inicial'], format='%d/%m/%Y %H:%M:%S')

    df['Hora'] = df['Dt./Hora Inicial'].dt.hour

    df['Hora'] = pd.to_datetime(df['Hora'], format='%H').dt.time

    df_conf = df
    df = df[df['Tipo '] == 'SEPARAÇÃO']

    def validar_e_substituir(valor):
        if valor == 'SEP VAREJO 01 - (PICKING)' or valor == 'SEP CONFINADO' or valor == 'SEP VAREJO CONEXOES' or valor == 'CONFERENCIA CONFINADO' or valor == 'CONFERENCIA VAREJO 1' or valor == 'CONF VOLUMOSO' or valor == 'SEP TUBOS' or valor == 'SEP FORA DE LINHA RUA 36':
            return valor
        else:
            return 'SEP VOLUMOSO'




    df['Area Separação'] = df['Area Separação'].apply(validar_e_substituir)


    st.subheader('Produtividade Separação')

        #Filtrando apenas por Separação do varejo
    area_var = ['SEP VOLUMOSO']

    volumoso = df[df['Area Separação'].isin(area_var)]

    #Produtividade Varejo. Ordenado por apanhas
    prod_volumoso = volumoso[['Usuário','Qtde Tarefas']].groupby('Usuário').agg(Apanhas=('Qtde Tarefas', 'count'), Pedidos=('Qtde Tarefas', 'nunique'))

    prod_volumoso = prod_volumoso.sort_values(by=('Apanhas'), ascending=False)

    data_atual = pd.DataFrame({"Apanhas": data, 'Pedidos': hora},index=['Data'], columns=prod_volumoso.columns)

    #Somando o total de apanhas e pedidos
    total = pd.DataFrame({'Apanhas': prod_volumoso['Apanhas'].sum(), 'Pedidos': prod_volumoso['Pedidos'].sum()}, index=['Apanhas Feitas'])

    data_atual = pd.DataFrame({"Apanhas": data, 'Pedidos': hora },index=['Data'], columns=prod_volumoso.columns)

    #prod_varejo = pd.merge(prod_varejo, on='Usuário', how='left')
    prod_volumoso.fillna(0, inplace=True)
    # Concatenar as linhas ao DataFrame original
    prod_volumoso = pd.concat([prod_volumoso, total, data_atual])

    #prod_varejo.fillna('', inplace=True)

    #Tabela para impressão/visualização
    prod_volumoso['Usuário'] = prod_volumoso.index
    prod_volumoso.drop(columns="Usuário", inplace=True)
    prod_volumoso.index.name = "Usuário"

    st.write(prod_volumoso, width=1000, height=500)

    # Função para ajustar os horários para ordenação correta
    def ajustar_horario(horario):
        hora = pd.to_datetime(horario, format='%H:%M').time()
        if hora >= pd.to_datetime('19:00', format='%H:%M').time():
            return pd.to_datetime(horario, format='%H:%M') - pd.DateOffset(hours=24)
        else:
            return pd.to_datetime(horario, format='%H:%M')

    # Calculando as tarefas por hora como você já fez
    tarefas_por_hora = volumoso.groupby(['Usuário', 'Hora']).size().reset_index(name='Qtde Tarefas')
    tarefas_por_hora['Hora'] = tarefas_por_hora['Hora'].apply(lambda x: x.strftime('%H:%M'))
    tarefas_por_hora = tarefas_por_hora.sort_values(by=['Usuário', 'Hora'])

    # Criar coluna de ordenação temporária
    tarefas_por_hora['Ordenacao'] = tarefas_por_hora['Hora'].apply(ajustar_horario)

    # Ordenar o DataFrame usando a coluna de ordenação
    tarefas_por_hora = tarefas_por_hora.sort_values(by=['Usuário', 'Ordenacao']).drop('Ordenacao', axis=1)

    # Pivotando os dados
    tarefas_pivot = tarefas_por_hora.pivot_table(index='Usuário', columns='Hora', values='Qtde Tarefas', fill_value=0)

    # Ordenando as colunas corretamente
    tarefas_pivot = tarefas_pivot.reindex(columns=sorted(tarefas_pivot.columns, key=ajustar_horario))

    # Calculando o total por hora e adicionando uma linha de total
    sum_values = tarefas_pivot.sum()
    tarefas_pivot.loc['Total P/ Hora'] = sum_values

    # Convertendo os valores para inteiros
    tarefas_pivot = tarefas_pivot.astype(int)

    # Definindo funções para aplicar cores com base em condições
    def apply_color(val):
        color = '#038a09' if val > 40 else '#ff5733'
        return f'background-color: {color}; color: white'

    def apply_color2(valor):
        color = 'green' if valor > 750 else 'red'
        return f'background-color: {color}; color: white'

    # Adicionando a coluna de total
    tarefas_pivot['Total'] = tarefas_pivot.sum(axis=1)

    # Aplicando estilo de cor à tabela dinâmica
    tarefas_pivot_styled = tarefas_pivot.style.applymap(apply_color)

    # Exibindo a tabela estilizada no Streamlit
    st.write("Tarefas por Hora:")
    st.dataframe(tarefas_pivot_styled)

    tarefas_por_hora = volumoso.groupby(['Usuário', 'Hora']).size().reset_index(name='Qtde Tarefas')
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

    st.subheader("Acompanhamento Separação Varejo")


    pedidos = pd.read_excel('Expedicao_de_Mercadorias_Varejo.xls', header=2)

    area_varejo = ['SEP VAREJO 01 - (PICKING)']
    situacao = ['Enviado para separação', 'Em processo separação','Aguardando conferência', 'Em processo conferência', 'Aguardando conferência volumes']

    pedidos.drop(columns=colunas)

    status_var = pedidos[pedidos['Descrição (Area de Separacao)'].isin(area_varejo)]
    status_var = status_var[status_var['Situação'].isin(situacao)]

    status_var['O.C'] = status_var['O.C'].astype(int)
    status_var['O.C'] = status_var['O.C'].astype(str)

    status_varejo = status_var.groupby('Situação').agg(Qtd_Pedidos = ('O.C', 'count'), OC = ('O.C', 'min'))

    st.write(status_varejo)


    st.header("Produtividade Separação")
    #Filtrando apenas por Separação do varejo


    varejo = df[df['Area Separação'].isin(area_varejo)]

    #Produtividade Varejo. Ordenado por apanhas
    prod_varejo = varejo[['Usuário','Qtde Tarefas']].groupby('Usuário').agg(Apanhas=('Qtde Tarefas', 'count'), Pedidos=('Qtde Tarefas', 'nunique'))

    prod_varejo = prod_varejo.sort_values(by=('Apanhas'), ascending=False)

    data_atual = pd.DataFrame({"Apanhas": data, 'Pedidos': hora},index=['Data'], columns=prod_varejo.columns)

    #Somando o total de apanhas e pedidos
    total = pd.DataFrame({'Apanhas': prod_varejo['Apanhas'].sum(), 'Pedidos': prod_varejo['Pedidos'].sum()}, index=['Total'])

    data_atual = pd.DataFrame({"Apanhas": data, 'Pedidos': hora },index=['Data'], columns=prod_varejo.columns)

    prod_varejo.fillna(0, inplace=True)
    # Concatenar as linhas ao DataFrame original
    prod_varejo = pd.concat([prod_varejo, total, data_atual])

    prod_varejo.fillna('', inplace=True)

    #Tabela para impressão/visualização
    prod_varejo['Usuário'] = prod_varejo.index

    prod_varejo.drop(columns="Usuário", inplace=True)
    prod_varejo.index.name = "Usuário"

    st.write(prod_varejo)
    ## TAREFAS POR HORA

    st.subheader('Tarefas por Hora:')

    tarefas_por_hora_var = varejo.groupby(['Usuário', 'Hora']).size().reset_index(name='Qtde Tarefas')

    tarefas_por_hora_var['Hora'] = tarefas_por_hora_var['Hora'].apply(lambda x: x.strftime('%H:%M'))

    tarefas_por_hora_var = tarefas_por_hora_var.sort_values(by=['Usuário', 'Hora'])

    tarefas_por_hora_var['Ordenacao'] = tarefas_por_hora_var['Hora'].apply(lambda x: (pd.to_datetime(str(x), format='%H:%M') + pd.DateOffset(hours=5)).time())

    tarefas_por_hora_var = tarefas_por_hora_var.sort_values(by=['Usuário', 'Ordenacao'])

    # Remover a coluna de ordenação temporária
    tarefas_por_hora_var = tarefas_por_hora_var.drop('Ordenacao', axis=1)

    tarefas_pivot_var = tarefas_por_hora_var.pivot_table(index='Usuário', columns='Hora', values='Qtde Tarefas', fill_value=0)

    # Ordenar o DataFrame pelas horas
    tarefas_pivot_var = tarefas_pivot_var.reindex(columns=sorted(tarefas_pivot_var.columns, key=lambda x: (pd.to_datetime(str(x), format='%H:%M') + pd.DateOffset(hours=5)).time()))

    # Calculando a média de cada coluna de horas
    #mean_values = tarefas_pivot.mean()

    #mean_values = mean_values.round(0).astype(int)

    # Adicionando as médias como uma nova linha ao DataFrame tarefas_pivot
    #tarefas_pivot.loc['Média Hora'] = mean_values

    #mean_total  = mean_values.mean().mean()

    sum_values = tarefas_pivot_var.sum()

    #sum_values = tarefas_pivot.drop('Média Hora').sum()


    tarefas_pivot_var.loc['Total P/ Hora'] = sum_values
    tarefas_pivot_var = tarefas_pivot_var.fillna(0)
    tarefas_pivot_var = tarefas_pivot_var.astype(int)

    # Definir uma função para aplicar as cores com base nas condições
    def apply_color(val):
        color = '#038a09' if val > 76 else '#ff5733'
        return f'background-color: {color}; color: white'


    tarefas_pivot_var['Total'] = tarefas_pivot_var.sum(axis=1)
    #tarefas_pivot['Total'] = tarefas_pivot['Total'].drop('Média Hora')

    #tarefas_pivot['Total'].fillna(mean_total, inplace=True)

    tarefas_pivot_var['Total'] = tarefas_pivot_var['Total'].astype(int)

    # Aplicar a função de cor à tabela dinâmica
    tarefas_pivot_styled_var = tarefas_pivot_var.style.applymap(apply_color)


       # Exibir a tabela dinâmica com estilos de cor
    st.write(tarefas_pivot_styled_var)


    st.subheader('Tarefas por Hora')

    #st.write(tarefas_pivot)

    tarefas_pivot_var = tarefas_pivot_var.drop(columns='Total')
    total_hora_data = tarefas_pivot_var.loc['Total P/ Hora']
    

    df_total = total_hora_data.reset_index()
    df_total.columns = ['Hora', 'Total']

    # plt.figure(figsize=(12, 6))
    # plt.plot(total_hora_data.index, total_hora_data.values, marker='o', linestyle='-', color='black', label='Total de Tarefas')

    # for i, (hora, total) in enumerate(total_hora_data.items()):
    #     plt.annotate((total), (hora, total), textcoords="offset points", xytext=(0, 10), ha='center')

    # plt.title('Total de Tarefas por Hora')
    # plt.xlabel('Hora')
    # plt.ylabel('Quantidade Total de Tarefas')
    # plt.xticks(rotation=45)
    # plt.legend(loc='upper left')
    # plt.grid(True)
    # plt.tight_layout()
    #st.pyplot(plt)
#     df_total['Hora_float'] = pd.to_datetime(df_total['Hora'], format='%H:%M').dt.hour + pd.to_datetime(df_total['Hora'], format='%H:%M').dt.minute / 60

#     X = df_total['Hora_float'].values.reshape(-1, 1)
#     y = df_total['Total'].values
#     model = LinearRegression()
#     model.fit(X, y)

#     # Previsão para a próxima hora
#     ultima_hora = df_total['Hora'].iloc[-1]  # Pegando a última hora da lista
#     proxima_hora_float = hora_para_float(ultima_hora) + 1  # Adiciona 1 hora
#     proxima_tarefa_prevista = model.predict([[proxima_hora_float]])

#     # Exibir a previsão
    

#     # Plotar os dados históricos e a projeção
#     plt.figure(figsize=(12, 6))
#     plt.plot(total_hora_data.index, total_hora_data.values, marker='o', linestyle='-', color='black', label='Total de Tarefas')
#     for i, (hora, total) in enumerate(total_hora_data.items()):
#         plt.annotate((total), (hora, total), textcoords="offset points", xytext=(0, 10), ha='center')
#     meta_valores = []
#     for hora in total_hora_data.index:
#         if hora in ['19:00', '00:00', '01:00']:
#             meta_valores.append(675)  # Exemplo de meta nesses horários
#         else:
#             meta_valores.append(1350)  # Exemplo de meta para os outros horários

# # Traçar a linha de meta
#     plt.plot(total_hora_data.index, meta_valores, linestyle='--', color='red', label='Meta')
    
#     plt.plot([ultima_hora, f'{int(proxima_hora_float)}:00'], [df_total['Total'].iloc[-1], proxima_tarefa_prevista[0]], 
#             label='Projeção', linestyle='--', marker='x', color='red')
#     plt.xlabel('Hora')
#     plt.ylabel('Tarefas')
#     plt.title('Projeção de Tarefas para a Próxima Hora')
#     plt.xticks(rotation=45)
#     plt.legend()
#     plt.grid(True)
#     plt.show()
#     st.pyplot(plt)

    df_total = total_hora_data.reset_index()
    df_total.columns = ['Hora', 'Total']

    # Converter Hora para valores numéricos para fazer a projeção
    df_total['Hora_float'] = pd.to_datetime(df_total['Hora'], format='%H:%M').dt.hour + pd.to_datetime(df_total['Hora'], format='%H:%M').dt.minute / 60

    # Criar modelo de regressão linear
    X = df_total['Hora_float'].values.reshape(-1, 1)
    y = df_total['Total'].values
    #Treinamento do modelo
    model = LinearRegression()
    model.fit(X, y)

    # Previsão para a próxima hora
    ultima_hora = df_total['Hora_float'].iloc[-1]
    proxima_hora_float = ultima_hora + 1  # Adiciona 1 hora
    proxima_tarefa_prevista = model.predict([[proxima_hora_float]])

    # Adicionar a projeção ao DataFrame
    df_projecao = pd.DataFrame({
        'Hora': [f'{int(proxima_hora_float)}:00'],
        'Total': [proxima_tarefa_prevista[0]],
        'Projecao': ['Sim']  # Indicando que esse valor é projetado
    })

    # Combinar o DataFrame original com a projeção
    df_total['Projecao'] = 'Não'  # Indicando dados reais
    df_full = pd.concat([df_total, df_projecao], ignore_index=True)

    # Criar o gráfico usando Matplotlib
    plt.figure(figsize=(10, 6))

    # Gráfico das tarefas reais
    plt.plot(df_total['Hora'], df_total['Total'], label='Tarefas Reais', color='black', marker='o')

    # Adicionar a projeção
    plt.plot(df_projecao['Hora'], df_projecao['Total'], label='Projeção', color='red', linestyle='--', marker='o')
    meta_valores = []
    for hora in total_hora_data.index:
        if hora in ['19:00', '00:00', '01:00']:
            meta_valores.append(621)  # Exemplo de meta nesses horários
        else:
            meta_valores.append(1242)  # Exemplo de meta para os outros horários

# Traçar a linha de meta
    plt.plot(total_hora_data.index, meta_valores, linestyle='--', color='blue', label='Meta')

    # Adicionar rótulos para os dados reais
    for i, txt in enumerate(df_total['Total']):
        plt.text(df_total['Hora'].iloc[i], df_total['Total'].iloc[i] + 0.2, f'{txt:.2f}', color='black')

    plt.plot([df_total['Hora'].iloc[-1], f'{int(proxima_hora_float)}:00'], 
         [df_total['Total'].iloc[-1], proxima_tarefa_prevista[0]], 
         label='Projeção', linestyle='--', marker='x', color='red')

    # Adicionar rótulos para a projeção
    plt.text(df_projecao['Hora'].iloc[0], df_projecao['Total'].iloc[0] + 0.2, f'{df_projecao["Total"].iloc[0]:.2f}', color='red')

    # Configurar os rótulos e título do gráfico
    plt.xlabel('Hora')
    plt.ylabel('Total de Tarefas')
    plt.title('Projeção de Tarefas por Hora')
    plt.legend(['Total de Tarefas', 'Total Projetado', 'Meta'])
    plt.grid(True)

    # Exibir o gráfico
    st.pyplot(plt)

# Configurando layout do gráfico
    df_conf = pd.read_excel('Gestao_Produtividade_detalhada_WMS_2.xlsx', header=2)

    #Função para trazer data e hora atualizada
    @st.cache_data
    def data ():

        data_atual = datetime.now(pytz.timezone(fuso_horario)).strftime('%d-%m-%Y')
        hora_atual = datetime.now(pytz.timezone(fuso_horario)).strftime('%H:%M')

        return data_atual, hora_atual

    data, hora = data()

    df_conf['Dt./Hora Inicial'] = pd.to_datetime( df_conf['Dt./Hora Inicial'], format='%d/%m/%Y %H:%M:%S')

    df_conf['Hora'] = df_conf['Dt./Hora Inicial'].dt.hour

    df_conf['Hora'] = pd.to_datetime(df_conf['Hora'], format='%H').dt.time

    #st.pyplot(fig)

    st.header('Produtividade Conferência')

    area_conf = ['CONFERENCIA VAREJO 1']

    conferencia = df_conf[df_conf['Area Separação'].isin(area_conf)]

    prod_conferencia = conferencia[['Usuário','Qtde Tarefas']].groupby('Usuário').agg(Apanhas=('Qtde Tarefas', 'count'), Pedidos=('Qtde Tarefas', 'nunique'))

    prod_conferencia = prod_conferencia.sort_values(by=('Apanhas'), ascending=False)

    data_atual = pd.DataFrame({"Apanhas": data, 'Pedidos': hora},index=['Data'], columns=prod_conferencia.columns)

    #Somando o total de apanhas e pedidos
    total = pd.DataFrame({'Apanhas': prod_conferencia['Apanhas'].sum(), 'Pedidos': prod_conferencia['Pedidos'].sum()}, index=['Total'])

    # Concatenar as linhas ao DataFrame original
    prod_conferencia = pd.concat([prod_conferencia, total, data_atual])

    prod_conferencia['Usuário'] = prod_conferencia.index
    prod_conferencia.drop(columns="Usuário", inplace=True)
    prod_conferencia.index.name = "Usuário"

    st.write(prod_conferencia)

    ## TAREFAS POR HORA

    st.subheader('Tarefas por Hora:')

    tarefas_por_hora = conferencia.groupby(['Usuário', 'Hora']).size().reset_index(name='Qtde Tarefas')

    tarefas_por_hora['Hora'] = tarefas_por_hora['Hora'].apply(lambda x: x.strftime('%H:%M'))

    tarefas_por_hora = tarefas_por_hora.sort_values(by=['Usuário', 'Hora'])

    tarefas_por_hora['Ordenacao'] = tarefas_por_hora['Hora'].apply(lambda x: (pd.to_datetime(str(x), format='%H:%M') + pd.DateOffset(hours=5)).time())

    tarefas_por_hora = tarefas_por_hora.sort_values(by=['Usuário', 'Ordenacao'])

    # Remover a coluna de ordenação temporária
    tarefas_por_hora = tarefas_por_hora.drop('Ordenacao', axis=1)

    tarefas_pivot = tarefas_por_hora.pivot_table(index='Usuário', columns='Hora', values='Qtde Tarefas', fill_value=0)

    # Ordenar o DataFrame pelas horas
    tarefas_pivot = tarefas_pivot.reindex(columns=sorted(tarefas_pivot.columns, key=lambda x: (pd.to_datetime(str(x), format='%H:%M') + pd.DateOffset(hours=5)).time()))

    # Calculando a média de cada coluna de horas
    mean_values = tarefas_pivot.mean()

    mean_values = mean_values.round(0).astype(int)

    # Adicionando as médias como uma nova linha ao DataFrame tarefas_pivot
    # tarefas_pivot.loc['Média Hora'] = mean_values

    # mean_total  = mean_values.mean().mean()

    sum_values = tarefas_pivot.sum()

    # sum_values = tarefas_pivot.drop('Média Hora').sum()


    tarefas_pivot.loc['Total P/ Hora'] = sum_values

    tarefas_pivot = tarefas_pivot.astype(int)

    # Definir uma função para aplicar as cores com base nas condições
    def apply_color(val):
        color = '#038a09' if val > 80 else '#ff5733'
        return f'background-color: {color}; color: white'


    tarefas_pivot['Total'] = tarefas_pivot.sum(axis=1)
    # tarefas_pivot['Total'] = tarefas_pivot['Total'].drop('Média Hora')

    # tarefas_pivot['Total'].fillna(mean_total, inplace=True)

    tarefas_pivot['Total'] = tarefas_pivot['Total'].astype(int)

    # Aplicar a função de cor à tabela dinâmica
    tarefas_pivot_styled = tarefas_pivot.style.applymap(apply_color)


       # Exibir a tabela dinâmica com estilos de cor
    st.write(tarefas_pivot_styled)

    tarefas_pivot = tarefas_pivot.drop(columns='Total')
    total_hora_data = tarefas_pivot.loc['Total P/ Hora']
    

    df_total = total_hora_data.reset_index()
    df_total.columns = ['Hora', 'Total']

    # Criar o DataFrame para a linha de meta
    meta_hora_filtrado = df_total[df_total['Hora'].isin(['20:00','21:00','22:00','23:00','00:00','01:00','02:00','03:00','04:00','05:00'])].copy()

    meta_valores = []
    for hora in meta_hora_filtrado['Hora']:
        if hora in ['20:00', '00:00', '01:00']:
            meta_valores.append(750)  # Meta para horários específicos
        else:
            meta_valores.append(1500)  # Meta para os outros horários

    # Adicionar a coluna de meta no DataFrame
    meta_hora_filtrado['Meta'] = meta_valores

    # === Cálculo da Projeção para a Próxima Hora ===
    # Converter Hora para valores numéricos para prever a próxima hora
    df_total['Hora_float'] = pd.to_datetime(df_total['Hora'], format='%H:%M').dt.hour + pd.to_datetime(df_total['Hora'], format='%H:%M').dt.minute / 60

    # Criar modelo de regressão linear
    X = df_total['Hora_float'].values.reshape(-1, 1)
    y = df_total['Total'].values
    model = LinearRegression()
    model.fit(X, y)

    # Previsão para a próxima hora
    ultima_hora = df_total['Hora_float'].iloc[-1]
    proxima_hora_float = ultima_hora + 1  # Adiciona 1 hora
    proxima_tarefa_prevista = model.predict([[proxima_hora_float]])

    # Adicionar a projeção ao DataFrame
    df_projecao = pd.DataFrame({
        'Hora': [f'{int(proxima_hora_float)}:00'],
        'Total': [proxima_tarefa_prevista[0]],
        'Projecao': ['Sim']  # Indicando que esse valor é projetado
    })

    # Combinar o DataFrame original com a projeção
    df_total['Projecao'] = 'Não'  # Indicando dados reais
    df_full = pd.concat([df_total, df_projecao], ignore_index=True)

    # Gráfico principal: Total de tarefas por hora
    grafico_total = alt.Chart(df_full).mark_line(point=True).encode(
        x=alt.X('Hora:N', sort=None, title='Hora'),
        y=alt.Y('Total:Q', title='Total de Tarefas'),
        color=alt.Color('Projecao:N', legend=None, scale=alt.Scale(domain=['Não', 'Sim'], range=['black', 'red'])),  # Diferença visual entre real e projetado
        tooltip=['Hora', 'Total']
    ).properties(
        title='Total de Apanhas por Hora',
        width=600,
        height=400
    )
    linha_pontilhada = alt.Chart(df_full[df_full['Projecao'] == 'Sim']).mark_line(
    point=True,
    strokeDash=[5, 5],  # Define a linha como pontilhada
    color='red'
    ).encode(
        x=alt.X('Hora:N', sort=None),
        y=alt.Y('Total:Q'),
        tooltip=['Hora', 'Total']
    )
    # Rótulos dos dados no gráfico de total de tarefas
    rotulos_total = alt.Chart(df_full).mark_text(align='left', dx=5, dy=-5, color='black').encode(
        x=alt.X('Hora:N', sort=None),
        y=alt.Y('Total:Q'),
        text=alt.Text('Total:Q')
    )

    # Gráfico da meta
    grafico_meta = alt.Chart(meta_hora_filtrado).mark_line(strokeDash=[5, 5], color='blue').encode(
        x=alt.X('Hora:N', sort=None, title='Hora'),
        y=alt.Y('Meta:Q'),
        tooltip=['Hora', 'Meta']
    )

    # Combinar ambos os gráficos (total de tarefas e meta), incluindo rótulos e projeção
    grafico_final = (grafico_total + linha_pontilhada + rotulos_total + grafico_meta )

    # Exibir no Streamlit
    st.altair_chart(grafico_final, use_container_width=True)

        # Converter horas para valores numéricos
    df_total['Hora_float'] = df_total['Hora'].apply(hora_para_float)

    # Criar o modelo de regressão linear
    X = df_total['Hora_float'].values.reshape(-1, 1)
    y = df_total['Total'].values

    model = LinearRegression()
    model.fit(X, y)

    # Previsão para a próxima hora
    ultima_hora = df_total['Hora_float'].iloc[-1]  # Pegando o valor numérico da última hora
    proxima_hora_float = ultima_hora + 1  # Adiciona 1 hora
    proxima_tarefa_prevista = model.predict([[proxima_hora_float]])

    # Adicionar a previsão ao DataFrame
    df_projecao = pd.DataFrame({
        'Hora': [f'{int(proxima_hora_float)}:00'],
        'Tarefas': [proxima_tarefa_prevista[0]],
        'Tipo': ['Previsão']
    })

    df_total['Tipo'] = 'Real'  # Marcando dados reais
    df_full = pd.concat([df_total, df_projecao], ignore_index=True)  # Unindo os dados reais com a projeção

    # Criar o gráfico com Altair
    chart = alt.Chart(df_full).mark_line().encode(
        x='Hora',
        y='Tarefas',
        color='Tipo'
    ).properties(
        title='Projeção de Tarefas para a Próxima Hora'
    )

    # Adicionar pontos aos dados
    points = chart.mark_point().encode(
        shape=alt.Shape('Tipo:N', legend=None)
    )

    # Adicionar rótulos de dados
    labels = alt.Chart(df_full).mark_text(align='left', dx=5, dy=-5).encode(
        x='Hora',
        y='Tarefas',
        text=alt.Text('Tarefas:Q', format='.2f'),  # Formato de duas casas decimais para os rótulos
        color=alt.Color('Tipo:N', legend=None)
    )

    # Exibir o gráfico com os rótulos
    (points + labels + chart).interactive()
    
    
#ABA CONFINADO
with tab4:
    area_confinado = ['SEP CONFINADO']

    status_confinado = pedidos[pedidos['Descrição (Area de Separacao)'].isin(area_confinado)]
    status_confinado = status_confinado[status_confinado['Situação'].isin(situacao)]

    status_confinado.drop(columns=colunas, inplace=True)

    status_confinado['O.C'] = status_confinado['O.C'].astype(int)
    status_confinado['O.C'] = status_confinado['O.C'].astype(str)

    status_confinado = status_confinado.groupby('Situação').agg(Qtd_Pedidos = ('O.C', 'count'), OC = ('O.C', 'min'))

    st.write(status_confinado)


    #Filtrando apenas por Confinado
    confinado = df[df['Area Separação'] == 'SEP CONFINADO' ]

    #Soma de apanhas e pedidos
    prod_conf = confinado[['Usuário','Qtde Tarefas']].groupby('Usuário').agg(Apanhas=('Qtde Tarefas', 'count'), Pedidos=('Qtde Tarefas', 'nunique'))

    #Ordernando por Apanhas.
    prod_conf = prod_conf.sort_values(by='Apanhas', ascending=False)

    data_confinado = pd.DataFrame({"Apanhas": data, 'Pedidos': hora},index=['Data'], columns=prod_conf.columns)

    #Somando o total de apanhas e pedidos
    total_confinado = pd.DataFrame({'Apanhas': prod_conf['Apanhas'].sum(), 'Pedidos': prod_conf['Pedidos'].sum()}, index=['Total'])

    #Juntando os DF
    prod_conf = pd.concat([prod_conf, total_confinado, data_confinado])

    prod_conf.index.name = "Usuário"

    st.write(prod_conf)

    tarefas_por_hora = confinado.groupby(['Usuário', 'Hora']).size().reset_index(name='Qtde Tarefas')
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

    #st.subheader('Tarefas por Hora')
    #st.write(tarefas_pivot)

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
with tab6:
    area_conexoes = ['SEP VAREJO CONEXOES']

    status_conexoes = pedidos[pedidos['Descrição (Area de Separacao)'].isin(area_conexoes)]
    status_conexoes = status_conexoes[status_conexoes['Situação'].isin(situacao)]

    status_conexoes.drop(columns=colunas, inplace=True)

    status_conexoes['O.C'] = status_conexoes['O.C'].astype(int)
    status_conexoes['O.C'] = status_conexoes['O.C'].astype(str)

    status_conexoes = status_conexoes.groupby('Situação').agg(Qtd_Pedidos = ('O.C', 'count'), OC = ('O.C', 'min'))

    st.write(status_conexoes)


    #Filtrando apenas por Confinado
    conexoes = df[df['Area Separação'] == 'SEP VAREJO CONEXOES' ]

    #Soma de apanhas e pedidos
    prod_conexoes = conexoes[['Usuário','Qtde Tarefas']].groupby('Usuário').agg(Apanhas=('Qtde Tarefas', 'count'), Pedidos=('Qtde Tarefas', 'nunique'))

    #Ordernando por Apanhas.
    prod_conexoes = prod_conexoes.sort_values(by='Apanhas', ascending=False)

    data_conexoes = pd.DataFrame({"Apanhas": data, 'Pedidos': hora},index=['Data'], columns=prod_conexoes.columns)

    #Somando o total de apanhas e pedidos
    total_conexoes = pd.DataFrame({'Apanhas': prod_conexoes['Apanhas'].sum(), 'Pedidos': prod_conexoes['Pedidos'].sum()}, index=['Total'])

    #Juntando os DF
    prod_conexoes = pd.concat([prod_conexoes, total_conexoes, data_conexoes])

    prod_conexoes.index.name = "Usuário"

    st.write(prod_conexoes)

    tarefas_por_hora = conexoes.groupby(['Usuário', 'Hora']).size().reset_index(name='Qtde Tarefas')
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

    #st.subheader('Tarefas por Hora')
    #st.write(tarefas_pivot)

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

    df_total = total_hora_data.reset_index()
    df_total.columns = ['Hora', 'Total']

    # Converter Hora para valores numéricos para fazer a projeção
    df_total['Hora_float'] = pd.to_datetime(df_total['Hora'], format='%H:%M').dt.hour + pd.to_datetime(df_total['Hora'], format='%H:%M').dt.minute / 60

    # Criar modelo de regressão linear
    X = df_total['Hora_float'].values.reshape(-1, 1)
    y = df_total['Total'].values
    #Treinamento do modelo
    model = LinearRegression()
    model.fit(X, y)

    # Previsão para a próxima hora
    ultima_hora = df_total['Hora_float'].iloc[-1]
    proxima_hora_float = ultima_hora + 1  # Adiciona 1 hora
    proxima_tarefa_prevista = model.predict([[proxima_hora_float]])

    # Adicionar a projeção ao DataFrame
    df_projecao = pd.DataFrame({
        'Hora': [f'{int(proxima_hora_float)}:00'],
        'Total': [proxima_tarefa_prevista[0]],
        'Projecao': ['Sim']  # Indicando que esse valor é projetado
    })

    # Combinar o DataFrame original com a projeção
    df_total['Projecao'] = 'Não'  # Indicando dados reais
    df_full = pd.concat([df_total, df_projecao], ignore_index=True)

    # Criar o gráfico usando Matplotlib
    plt.figure(figsize=(10, 6))

    # Gráfico das tarefas reais
    plt.plot(df_total['Hora'], df_total['Total'], label='Tarefas Reais', color='black', marker='o')

    # Adicionar a projeção
    plt.plot(df_projecao['Hora'], df_projecao['Total'], label='Projeção', color='red', linestyle='--', marker='o')
    meta_valores = []
    for hora in total_hora_data.index:
        if hora in ['19:00', '00:00', '01:00']:
            meta_valores.append(675)  # Exemplo de meta nesses horários
        else:
            meta_valores.append(1350)  # Exemplo de meta para os outros horários

# Traçar a linha de meta
    plt.plot(total_hora_data.index, meta_valores, linestyle='--', color='blue', label='Meta')

    # Adicionar rótulos para os dados reais
    for i, txt in enumerate(df_total['Total']):
        plt.text(df_total['Hora'].iloc[i], df_total['Total'].iloc[i] + 0.2, f'{txt:.2f}', color='black')

    plt.plot([df_total['Hora'].iloc[-1], f'{int(proxima_hora_float)}:00'], 
         [df_total['Total'].iloc[-1], proxima_tarefa_prevista[0]], 
         label='Projeção', linestyle='--', marker='x', color='red')

    # Adicionar rótulos para a projeção
    plt.text(df_projecao['Hora'].iloc[0], df_projecao['Total'].iloc[0] + 0.2, f'{df_projecao["Total"].iloc[0]:.2f}', color='red')

    # Configurar os rótulos e título do gráfico
    plt.xlabel('Hora')
    plt.ylabel('Total de Tarefas')
    plt.title('Projeção de Tarefas por Hora')
    plt.legend(['Total de Tarefas', 'Total Projetado', 'Meta'])
    plt.grid(True)
with tab5:
 #QUANTIDADE DE APANHAS REALIZADAS
    st.header('Expedição')

    pedidos['Qtd. Tarefas'] = pd.to_numeric(pedidos['Qtd. Tarefas'], errors='coerce')

    agrupado = pedidos.groupby(['Situação', 'Descrição (Area de Separacao)'])['Qtd. Tarefas'].sum().reset_index()

    varejo = agrupado[agrupado['Descrição (Area de Separacao)'] == 'SEP VAREJO 01 - (PICKING)'].reset_index()



    feito = ['Em processo conferência','Conferência validada','Conferência com divergência','Aguardando recontagem','Aguardando conferência volumes','Aguardando conferência', 'Concluído', 'Pedido totalmente cortado']
    varejo_feito = varejo[varejo['Situação'].isin(feito)].copy()
    varejo_feito['Situação'] = 'Apanhas Realizadas'


    confinado = agrupado[agrupado['Descrição (Area de Separacao)'] == 'SEP CONFINADO'].reset_index()
    confinado_feito = confinado[confinado['Situação'].isin(feito)].copy()
    confinado_feito['Situação'] = 'Apanhas Realizadas'

    conexoes = agrupado[agrupado['Descrição (Area de Separacao)'] == 'SEP VAREJO CONEXOES'].reset_index()
    conexoes_feito = conexoes[conexoes['Situação'].isin(feito)].copy()
    conexoes_feito['Situação'] = 'Apanhas Realizadas'

    agrupado['Descrição (Area de Separacao)'] = agrupado['Descrição (Area de Separacao)'].apply(validar_e_substituir)
    volumoso = agrupado[agrupado['Descrição (Area de Separacao)'] == 'SEP VOLUMOSO'].reset_index()
    volumoso_feito = volumoso[volumoso['Situação'].isin(feito)].copy()
    volumoso_feito['Situação'] = 'Apanhas Realizadas'


    df_feito_total = pd.DataFrame({
        'Situação': ['Apanhas Feitas'],
        'Varejo': [int(varejo_feito['Qtd. Tarefas'].sum())],
        'Confinado': [int(confinado_feito['Qtd. Tarefas'].sum())],
        'Volumoso': [int(volumoso_feito['Qtd. Tarefas'].sum())],
        'Conexões': [int(conexoes_feito['Qtd. Tarefas'].sum())]
        })

    df_importados = pd.DataFrame({
        'Situação': ['Apanhas Importadas'],
        'Varejo': [int(varejo['Qtd. Tarefas'].sum())],
        'Confinado': [int(confinado['Qtd. Tarefas'].sum())],
        'Volumoso': [int(volumoso['Qtd. Tarefas'].sum())] ,
        'Conexões': [int(conexoes['Qtd. Tarefas'].sum())]

        })
    df_feito_total[['Varejo', 'Confinado', 'Volumoso', 'Conexões']] = df_feito_total[['Varejo', 'Confinado', 'Volumoso', 'Conexões']].apply(pd.to_numeric, errors='coerce')
    df_importados[['Varejo', 'Confinado', 'Volumoso', 'Conexões']] = df_importados[['Varejo', 'Confinado', 'Volumoso', 'Conexões']].apply(pd.to_numeric, errors='coerce')

    percent_varejo = (df_feito_total['Varejo'].values[0] / df_importados['Varejo'].values[0]) * 100
    percent_confinado = (df_feito_total['Confinado'].values[0] / df_importados['Confinado'].values[0]) * 100
    percent_volumoso = (df_feito_total['Volumoso'].values[0] / df_importados['Volumoso'].values[0]) * 100
    percent_conexoes = (df_feito_total['Conexões'].values[0] / df_importados['Conexões'].values[0]) * 100

    

     # 3. Adicionar uma linha com as porcentagens
    df_percent = pd.DataFrame({
         'Situação': ['Porcentagem Feito'],
         'Varejo': [f'{percent_varejo:.2f}%'],
         'Confinado': [f'{percent_confinado:.2f}%'],
         'Volumoso': [f'{percent_volumoso:.2f}%'],
         'Conexões' : [f'{percent_conexoes:.2f}%']
         })

    def get_value(df, key):

        return df.loc[key][0] if key in df.index else 0

    # Construindo o DataFrame com tratamento de valores ausentes e chaves não existentes
    df_pedidos = pd.DataFrame({
        'Situação': ['Pedidos Enviados para Separação'],
        'Varejo': [get_value(status_varejo, 'Enviado para separação')],
        'Confinado': [get_value(status_confinado, 'Enviado para separação')],
        'Conexões': [get_value(status_conexoes, 'Enviado para separação')],
        'Volumoso': [status['Qtd_Ocs'].sum() if not pd.isna(status['Qtd_Ocs'].sum()) else 0]
    })

    print(df_pedidos)


    resultado_final = pd.concat([df_feito_total, df_importados, df_percent, df_pedidos], ignore_index=True)

    # Converter as colunas do DataFrame final para o formato numérico (excluindo a coluna 'Situação')

    # Função para aplicar gráfico de barras apenas na l

    # Supondo que 'resultado_final' seja seu DataFrame

    st.write(resultado_final)



