import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.plotting import table


# Título da Aplicação
st.title('Análise de Abastecimentos e Desempenho dos Operadores')

# Criação das abas
tab1, tab2, tab3 = st.tabs(["Abastecimento", "Separação Volumoso", "Separação"])

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

    df_abastecimento.rename(columns={"AREA DE SEPA ENDEREçO DESTINO" : "Area", 'CODPROD' : 'Qtd Códigos'}, inplace=True)

    st.subheader('Abastecimentos por Área')
    st.write(df_abastecimento.groupby('Area')['Qtd Códigos'].count(), height=200)


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

with tab2:
    # Título da Aplicação
    st.title('Acompanhamento da Operação Volumoso')

    expedicao = pd.read_excel('Expedicao_de_Mercadorias.xls', header=2)

    colunas = ['Nro. Nota', 'Conferente', 'Enviado p/ Doca', 'Descrição (Área de Conferência)', 'Nro. Sep.', 'Nro. Único',
            'Descrição (Doca do WMS)', 'Cód. Doca', 'Peso Bruto', 'M3 Bruto', 'Área', 'Cód. Emp OC', 'Cód. Área Sep', 'Triagem Realizada', 'Cod. Conferente' ]

    expedicao.drop(columns=colunas, inplace=True)

    expedicao = expedicao[expedicao['Situação'] == 'Enviado para separação']
    expedicao['O.C'] = expedicao['O.C'].astype(int)
    expedicao['O.C'] = expedicao['O.C'].astype(str)

    status = expedicao.groupby('Descrição (Area de Separacao)').agg(Qtd_Ocs = ('O.C', 'count'), OC = ('O.C', 'min')).reset_index()


    st.write(status)

    df = pd.read_excel('Gestao_Produtividade_detalhada_WMS_2.xlsx', header=2)

    #Função para trazer data e hora atualizada
def data ():
  data_atual = datetime.now(pytz.timezone(fuso_horario)).strftime('%d-%m-%Y')
  hora_atual = datetime.now(pytz.timezone(fuso_horario)).strftime('%H:%M')

  return data_atual, hora_atual

data, hora = data()

df['Dt./Hora Inicial'] = pd.to_datetime( df['Dt./Hora Inicial'], format='%d/%m/%Y %H:%M:%S')

df['Hora'] = df['Dt./Hora Inicial'].dt.hour

df['Hora'] = pd.to_datetime(df['Hora'], format='%H').dt.time

df = df[df['Tipo '] == 'SEPARAÇÃO']

def validar_e_substituir(valor):
    if valor == 'SEP VAREJO 01 - (PICKING)' or valor == 'SEP CONFINADO' or valor == 'SEP VAREJO CONEXOES' or valor == 'CONFERENCIA CONFINADO' or valor == 'CONFERENCIA VAREJO 1' or valor == 'CONF VOLUMOSO' or valor == 'SEP TUBOS' or valor == 'SEP AUDITORIO FL - (PICKING)':
           return valor
    else:
        return 'SEP VOLUMOSO'
            

    
       
       
       

df['Area Separação'] = df['Area Separação'].apply(validar_e_substituir)


st.subheader('Produtividade Separação')

    #Filtrando apenas por Separação do varejo
area_var = ['SEP VOLUMOSO' ]

varejo = df[df['Area Separação'].isin(area_var)]

#Produtividade Varejo. Ordenado por apanhas
prod_varejo = varejo[['Usuário','Qtde Tarefas']].groupby('Usuário').agg(Apanhas=('Qtde Tarefas', 'count'), Pedidos=('Qtde Tarefas', 'nunique'))

prod_varejo = prod_varejo.sort_values(by=('Apanhas'), ascending=False)

data_atual = pd.DataFrame({"Apanhas": data, 'Pedidos': hora},index=['Data'], columns=prod_varejo.columns)

#Somando o total de apanhas e pedidos
total = pd.DataFrame({'Apanhas': prod_varejo['Apanhas'].sum(), 'Pedidos': prod_varejo['Pedidos'].sum()}, index=['Apanhas Feitas'])
#apanhas_totais = prod_varejo.loc[prod_varejo['Usuário'] != 'Total', 'Apanhas'].sum()
#total_apanhas = prod_varejo.loc['Total', 'Apanhas']
#prod_varejo['Representividade'] = prod_varejo['Apanhas'] / total_apanhas

data_atual = pd.DataFrame({"Apanhas": data, 'Pedidos': hora },index=['Data'], columns=prod_varejo.columns)

#prod_varejo = pd.merge(prod_varejo, on='Usuário', how='left')
prod_varejo.fillna(0, inplace=True)
# Concatenar as linhas ao DataFrame original
prod_varejo = pd.concat([prod_varejo, total, data_atual])

#prod_varejo.fillna('', inplace=True)

#Tabela para impressão/visualização
prod_varejo['Usuário'] = prod_varejo.index

# Criar figura e eixos
fig, ax = plt.subplots(figsize=(10, 4))

# Esconder eixos
ax.axis('off')

# Adicionar tabela e personalizar estilo
tab = table(ax, prod_varejo[['Apanhas', 'Pedidos']], loc='center', cellLoc='center', colWidths=[0.15, 0.15, 0.15, 0.15])

# Adicionar título

# Adicionar cores alternadas às células
colors = ['white', 'lightgray']
for i, key in enumerate(tab.get_celld().keys()):
    cell = tab.get_celld()[key]
    if key[0] == 0:  # Ignorar a linha de cabeçalho
        continue
    cell.set_facecolor(colors[i % len(colors)])

# Adicionar estilo aos nomes dos usuários
tab.auto_set_font_size(False)
tab.set_fontsize(10)
tab.scale(1.2, 1.2)

# Salvar a imagem
#plt.savefig('Produtividade Varejo.png', bbox_inches='tight', pad_inches=0.5)
st.pyplot(fig)
