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
from streamlit_extras.grid import grid

def validar_e_substituir(valor):
    if valor in ['SEP VAREJO 01 - (PICKING)', 'SEP CONFINADO', 'SEP VAREJO CONEXOES']:
        return valor
    else:
        return 'SEP VOLUMOSO'


    
pedidos = pd.read_excel('archives/Expedicao_de_Mercadorias_Varejo.xls', header=2)





colunas = ['Nro. Nota', 'Conferente', 'Enviado p/ Doca', 'Descrição (Área de Conferência)', 'Nro. Sep.', 'Nro. Único',
            'Descrição (Doca do WMS)', 'Cód. Doca', 'Peso Bruto', 'M3 Bruto', 'Área', 'Cód. Emp OC', 'Cód. Área Sep', 'Triagem Realizada', 'Cod. Conferente' ]


area_confinado = ['SEP CONFINADO']
situacao = ['Enviado para separação', 'Em processo separação','Aguardando conferência', 'Em processo conferência', 'Aguardando conferência volumes']

status_confinado = pedidos[pedidos['Descrição (Area de Separacao)'].isin(area_confinado)]
status_confinado = status_confinado[status_confinado['Situação'].isin(situacao)]

status_confinado.drop(columns=colunas, inplace=True)

status_confinado['O.C'] = status_confinado['O.C'].astype(int)
status_confinado['O.C'] = status_confinado['O.C'].astype(str)

status_confinado = status_confinado.groupby('Situação').agg(Qtd_Pedidos = ('O.C', 'count'), OC = ('O.C', 'min'))

area_varejo = ['SEP VAREJO 01 - (PICKING)']
situacao = ['Enviado para separação', 'Em processo separação','Aguardando conferência', 'Em processo conferência', 'Aguardando conferência volumes']

status_var = pedidos[pedidos['Descrição (Area de Separacao)'].isin(area_varejo)]
status_var = status_var[status_var['Situação'].isin(situacao)]

status_var['O.C'] = status_var['O.C'].astype(int)
status_var['O.C'] = status_var['O.C'].astype(str)

status_varejo = status_var.groupby('Situação').agg(Qtd_Pedidos = ('O.C', 'count'), OC = ('O.C', 'min'))

area_varejo = ['SEP VAREJO 01 - (PICKING)']
situacao = ['Enviado para separação', 'Em processo separação','Aguardando conferência', 'Em processo conferência', 'Aguardando conferência volumes']

# st.markdown("# Expedição")


pedidos['Qtd. Tarefas'] = pd.to_numeric(pedidos['Qtd. Tarefas'], errors='coerce')

agrupado = pedidos.groupby(['Situação', 'Descrição (Area de Separacao)'])['Qtd. Tarefas'].sum().reset_index()

varejo = agrupado[agrupado['Descrição (Area de Separacao)'] == 'SEP VAREJO 01 - (PICKING)'].reset_index()


expedicao = pd.read_excel('archives/Expedicao_de_Mercadorias.xls', header=2)

expedicao.drop(columns=colunas, inplace=True)

expedicao = expedicao[expedicao['Situação'] == 'Enviado para separação']
expedicao['O.C'] = expedicao['O.C'].astype(int)
expedicao['O.C'] = expedicao['O.C'].astype(str)

status = expedicao.groupby('Descrição (Area de Separacao)').agg(Qtd_Ocs = ('O.C', 'count'), OC = ('O.C', 'min')).reset_index()



feito = ['Em processo conferência','Conferência validada','Conferência com divergência','Aguardando recontagem','Aguardando conferência volumes','Aguardando conferência', 'Concluído', 'Pedido totalmente cortado']
varejo_feito = varejo[varejo['Situação'].isin(feito)].copy()
varejo_feito['Situação'] = 'Apanhas Realizadas'


confinado = agrupado[agrupado['Descrição (Area de Separacao)'] == 'SEP CONFINADO'].reset_index()
confinado_feito = confinado[confinado['Situação'].isin(feito)].copy()
confinado_feito['Situação'] = 'Apanhas Realizadas'

# conexoes = agrupado[agrupado['Descrição (Area de Separacao)'] == 'SEP VAREJO CONEXOES'].reset_index()
# conexoes_feito = conexoes[conexoes['Situação'].isin(feito)].copy()
# conexoes_feito['Situação'] = 'Apanhas Realizadas'
agrupado = agrupado.loc[agrupado['Descrição (Area de Separacao)'] != 'SEP TUBOS']
agrupado['Descrição (Area de Separacao)'] = agrupado['Descrição (Area de Separacao)'].apply(validar_e_substituir)
volumoso = agrupado[agrupado['Descrição (Area de Separacao)'] == 'SEP VOLUMOSO'].reset_index()
volumoso_feito = volumoso[volumoso['Situação'].isin(feito)].copy()
volumoso_feito['Situação'] = 'Apanhas Realizadas'


df_feito_total = pd.DataFrame({
    'Situação': ['Apanhas Feitas'],
    'Varejo': [int(varejo_feito['Qtd. Tarefas'].sum())],
    'Confinado': [int(confinado_feito['Qtd. Tarefas'].sum())],
    'Volumoso': [int(volumoso_feito['Qtd. Tarefas'].sum())],
    # 'Conexões': [int(conexoes_feito['Qtd. Tarefas'].sum())]
    })

df_importados = pd.DataFrame({
    'Situação': ['Apanhas Importadas'],
    'Varejo': [int(varejo['Qtd. Tarefas'].sum())],
    'Confinado': [int(confinado['Qtd. Tarefas'].sum())],
    'Volumoso': [int(volumoso['Qtd. Tarefas'].sum())] ,
    # 'Conexões': [int(conexoes['Qtd. Tarefas'].sum())]

    })
df_feito_total[['Varejo', 'Confinado', 'Volumoso', ]] = df_feito_total[['Varejo', 'Confinado', 'Volumoso']].apply(pd.to_numeric, errors='coerce')
df_importados[['Varejo', 'Confinado', 'Volumoso', ]] = df_importados[['Varejo', 'Confinado', 'Volumoso']].apply(pd.to_numeric, errors='coerce')

percent_varejo = (df_feito_total['Varejo'].values[0] / df_importados['Varejo'].values[0]) * 100
percent_confinado = (df_feito_total['Confinado'].values[0] / df_importados['Confinado'].values[0]) * 100
percent_volumoso = (df_feito_total['Volumoso'].values[0] / df_importados['Volumoso'].values[0]) * 100




    # 3. Adicionar uma linha com as porcentagens
df_percent = pd.DataFrame({
        'Situação': ['Concluído'],
        'Varejo': [f'{percent_varejo:.2f}%'],
        'Confinado': [f'{percent_confinado:.2f}%'],
        'Volumoso': [f'{percent_volumoso:.2f}%'],
        
        })

def get_value(df, key):

    return df.loc[key][0] if key in df.index else 0

# Construindo o DataFrame com tratamento de valores ausentes e chaves não existentes
df_pedidos = pd.DataFrame({
    'Situação': ['Enviados para Separação'],
    'Varejo': [get_value(status_varejo, 'Enviado para separação')],
    'Confinado': [get_value(status_confinado, 'Enviado para separação')],
    'Volumoso': [status['Qtd_Ocs'].sum() if not pd.isna(status['Qtd_Ocs'].sum()) else 0]
})



resultado_final = pd.concat([df_feito_total, df_importados, df_percent, df_pedidos], ignore_index=True)


# Converter as colunas do DataFrame final para o formato numérico (excluindo a coluna 'Situação')

# Função para aplicar gráfico de barras apenas na l

# Supondo que 'resultado_final' seja seu DataFrame
resultado_final.set_index('Situação', inplace=True)

# st.dataframe(resultado_final)





# my_grid = grid(4, vertical_align='center')


# #SETORES E SITUAÇÃO
# my_grid.subheader(str(df_feito_total.columns[0]))
# my_grid.subheader(str(df_feito_total.columns[1]))
# my_grid.subheader(str(df_feito_total.columns[2]))
# my_grid.subheader(str(df_feito_total.columns[3]))

# #SITUAÇÕES IMPORTADOS
# my_grid.subheader(df_importados['Situação'][0])
# my_grid.subheader(df_importados['Varejo'][0])
# my_grid.subheader(df_importados['Confinado'][0])
# my_grid.subheader(df_importados['Volumoso'][0])

# #SITUAÇÃO FEITOS
# my_grid.subheader(df_feito_total['Situação'][0])
# my_grid.subheader(df_feito_total['Varejo'][0])
# my_grid.subheader(df_feito_total['Confinado'][0])
# my_grid.subheader(df_feito_total['Volumoso'][0])

# #Situação porcentagem

# my_grid.subheader(df_percent['Situação'][0])
# my_grid.subheader(df_percent['Varejo'][0])
# my_grid.subheader(df_percent['Confinado'][0])
# my_grid.subheader(df_percent['Volumoso'][0])

# #Situação Pedidos

# my_grid.subheader(df_pedidos['Situação'][0])
# my_grid.subheader(df_pedidos['Varejo'][0])
# my_grid.subheader(df_pedidos['Confinado'][0])
# my_grid.subheader(df_pedidos['Volumoso'][0])


def create_dashboard_row(df, col_labels):
    cols = st.columns(len(col_labels))  # Cria colunas no layout
    for idx, col in enumerate(col_labels):
        with cols[idx]:
            st.markdown(
                f"""
                <div style="
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    height: 100px;
                    width: 100%;
                    background-color: #f4f4f4;
                    border-radius: 10px;
                    box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
                    font-size: 16px;
                    font-weight: bold;
                    color: #333333;
                    text-align: center;
                    padding: 10px;">
                    <div>{col}</div>
                    <div>{df[col].iloc[0] if col in df.columns else "N/A"}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

# Listando DataFrames e colunas que serão exibidas
dataframes = [df_importados,    df_feito_total, df_percent, df_pedidos]
columns = [ "Varejo", "Confinado", "Volumoso"]

st.title("Expedição")
for df in dataframes:
    st.subheader(f"{df['Situação'].iloc[0]}")
    create_dashboard_row(df, columns)


st.divider()
st.divider()



def validar_e_substituir(valor):
    if valor in ['SEP VAREJO 01 - (PICKING)', 'SEP CONFINADO', 'SEP VAREJO CONEXOES']:
        return valor
    else:
        return 'SEP VOLUMOSO'
    
# Carregando a planilha com a primeira linha relevante como cabeçalho
df = pd.read_excel('archives/Expedicao_de_Mercadorias_Varejo.xls', header=2)

# Substituindo valores na coluna "Descrição (Area de Separacao)"
df['Descrição (Area de Separacao)'] = df['Descrição (Area de Separacao)'].apply(validar_e_substituir)
# Extraindo todas as áreas únicas da coluna "Descrição (Area de Separacao)"
areas = df['Descrição (Area de Separacao)'].unique()

# Criando um novo DataFrame dinâmico para conter a "O.C", todas as áreas e as colunas de conferência
new_df = pd.DataFrame(columns=['O.C'] + list(areas) + ['Conferência Varejo', 'Conferência Confinado', 'Validação Varejo'])

# Preenchendo o novo DataFrame
rows = []

for oc in df['O.C'].unique():
    if pd.isna(oc):  # Verifica se o valor é NaN
        continue
    row = {'O.C': int(oc)}  # Converte O.C para int
    
    # Verificando cada área de separação
    for area in areas:
        situacoes_separacao = df[(df['O.C'] == oc) & (df['Descrição (Area de Separacao)'] == area)]['Situação']
        
        # Define status da área de separação para "Andamento" ou "Concluído"
        if situacoes_separacao.isin(['Enviado para a separação', 'Processo de Separação']).any():
            row[area] = 'Andamento'
        elif situacoes_separacao.isin(['Concluído', 'Aguardando conferência', 'Em processo conferência', 'Aguardando conferência volumes','Conferência validada', 'Conferência com divergência','Aguardando recontagem','Pedido totalmente cortado']).all():
            row[area] = 'Concluído'
        else:
            row[area] = 'Andamento'  # Caso haja outra situação que não seja "Concluído"
    
    # Verificando a situação para "Conferência Varejo"
    situacoes_conferencia_varejo = df[(df['O.C'] == oc) & (df['Descrição (Área de Conferência)'] == 'CONFERENCIA VAREJO 1')]['Situação']
    if situacoes_conferencia_varejo.isin(['Enviado para separação', 'Em processo separação', 'Aguardando conferência', 'Em processo conferência','Conferência com divergência']).any():
        row['Conferência Varejo'] = 'Andamento'
    else:
        row['Conferência Varejo'] = 'Concluído'
    
    # Verificando a situação para "Conferência Confinado"
    situacoes_conferencia_confinado = df[(df['O.C'] == oc) & (df['Descrição (Área de Conferência)'] == 'CONFERENCIA CONFINADO')]['Situação']
    if situacoes_conferencia_confinado.isin(['Enviado para separação', 'Em processo separação', 'Aguardando conferência', 'Em processo conferência', 'Conferência com divergência']).any():
        row['Conferência Confinado'] = 'Andamento'
    else:
        row['Conferência Confinado'] = 'Concluído'
    
    # Verificando a situação para "Validação Varejo"
    situacoes_validacao_varejo = df[(df['O.C'] == oc) & (df['Descrição (Área de Conferência)'] == 'CONFERENCIA VAREJO 1')]['Situação']
    if situacoes_validacao_varejo.isin(['Enviado para separação', 'Em processo separação', 'Aguardando conferência', 'Em processo conferência','Aguardando conferência volumes','Conferência com divergência']).any():
        row['Validação Varejo'] = 'Andamento'
    else:
        row['Validação Varejo'] = 'Concluído'
    
    rows.append(row)

# Criando o novo DataFrame a partir da lista de linhas
new_df = pd.DataFrame(rows)

# Ordenando o DataFrame por O.C
new_df.sort_values(by='O.C', inplace=True)
new_df.reset_index(drop=True, inplace=True)

# Função para estilizar o DataFrame com cores para cada status
def colorize_cells(value):
    if value == 'Andamento' or value == 'Em Separação' or value == 'Em Conferência':
        return 'background-color: red; color: white'
    elif value == 'Concluído':
        return 'background-color: green; color: white'
    return ''


# Aplicando a estilização ao novo DataFrame
styled_new_df = new_df.style.applymap(colorize_cells)


st.header("Acompanhamento das OC's")

st.write(styled_new_df)

# row1_col1, row1_col2 = st.columns(2)

# with row1_col1:
#     st.header('Varejo')

#     st.subheader('Feito')

#     st.subheader(df_feito_total['Varejo'][0])

# with row1_col2:
#     st.header("Apanhas")
#     st.subheader(df_feito_total['Varejo'][0])

# # Segunda linha
# row2_col1, row2_col2, row2_col3 = st.columns(3)

# with row2_col1:
#     st.write("Linha 2, Coluna 1")

# with row2_col2:
#     st.write("Linha 2, Coluna 2")

# with row2_col3:
#     st.write("Linha 2, Coluna 3")

# CSS para o estilo dos quadrados

# Função para criar quadrados no layout
