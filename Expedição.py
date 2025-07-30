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
    if valor in ['ESTEIRA MFC', 'SEP PNC 26 E 27 - XR', 'SEP VAREJO CONEXOES']:
        return valor
    else:
        return 'SEP VOLUMOSO'


st.header('Expedição')

pedidos = pd.read_excel('archives/Expedicao_de_Mercadorias_Varejo.xls', header=2)



colunas = ['Nro. Nota', 'Conferente', 'Enviado p/ Doca', 'Descrição (Área de Conferência)', 'Nro. Sep.', 'Nro. Único',
            'Descrição (Doca do WMS)', 'Cód. Doca', 'Peso Bruto', 'M3 Bruto', 'Área', 'Cód. Emp OC', 'Cód. Área Sep', 'Triagem Realizada', 'Cod. Conferente' ]


area_varejo = ['ESTEIRA MFC']
situacao = ['Enviado para separação', 'Em processo separação','Aguardando conferência', 'Em processo conferência', 'Aguardando conferência volumes']

status_var = pedidos[pedidos['Descrição (Area de Separacao)'].isin(area_varejo)]
status_var = status_var[status_var['Situação'].isin(situacao)]

status_var['O.C'] = status_var['O.C'].astype(int)
status_var['O.C'] = status_var['O.C'].astype(str)

status_varejo = status_var.groupby('Situação').agg(Qtd_Pedidos = ('O.C', 'count'), OC = ('O.C', 'min'))

area_conferencia = ['CONFERENCIA MFC']
situacao = ['Aguardando conferência']

status_confe = pedidos[pedidos['Descrição (Área de Conferência)'].isin(area_conferencia)]
status_confe = status_confe[status_confe['Situação'].isin(situacao)]

status_confe['O.C'] = status_confe['O.C'].astype(int)
status_confe['O.C'] = status_confe['O.C'].astype(str)

status_conferencia = status_confe.groupby('Situação').agg(Qtd_Pedidos = ('O.C', 'count'), OC = ('O.C', 'min'))

area_varejo = ['ESTEIRA MFC']
situacao = ['Enviado para separação', 'Em processo separação','Aguardando conferência', 'Em processo conferência', 'Aguardando conferência volumes']

# st.markdown("# Expedição")


pedidos['Qtd. Tarefas'] = pd.to_numeric(pedidos['Qtd. Tarefas'], errors='coerce')

agrupado = pedidos.groupby(['Situação', 'Descrição (Area de Separacao)'])['Qtd. Tarefas'].sum().reset_index()

varejo = agrupado[agrupado['Descrição (Area de Separacao)'] == 'ESTEIRA MFC'].reset_index()


expedicao = pd.read_excel('archives/Expedicao_de_Mercadorias.xls', header=2)

expedicao.drop(columns=colunas, inplace=True)

expedicao = expedicao[expedicao['Situação'] == 'Enviado para separação']
expedicao['O.C'] = expedicao['O.C'].astype(int)
expedicao['O.C'] = expedicao['O.C'].astype(str)

status = expedicao.groupby('Descrição (Area de Separacao)').agg(Qtd_Ocs = ('O.C', 'count'), OC = ('O.C', 'min')).reset_index()



feito = ['Em processo conferência','Conferência validada','Conferência com divergência','Aguardando recontagem','Pedido parcialmente cortado','Aguardando conferência volumes','Aguardando conferência', 'Concluído', 'Pedido totalmente cortado']
varejo_feito = varejo[varejo['Situação'].isin(feito)].copy()
varejo_feito['Situação'] = 'Apanhas Realizadas'


# confinado = agrupado[agrupado['Descrição (Area de Separacao)'] == 'SEP CONFINADO'].reset_index()
# confinado_feito = confinado[confinado['Situação'].isin(feito)].copy()
# confinado_feito['Situação'] = 'Apanhas Realizadas'

# conexoes = agrupado[agrupado['Descrição (Area de Separacao)'] == 'SEP VAREJO CONEXOES'].reset_index()
# conexoes_feito = conexoes[conexoes['Situação'].isin(feito)].copy()
# conexoes_feito['Situação'] = 'Apanhas Realizadas'
agrupado = agrupado.loc[agrupado['Descrição (Area de Separacao)'] != 'SEP TUBOS']
agrupado['Descrição (Area de Separacao)'] = agrupado['Descrição (Area de Separacao)'].apply(validar_e_substituir)
volumoso = agrupado[agrupado['Descrição (Area de Separacao)'] == 'SEP VOLUMOSO'].reset_index()
volumoso_feito = volumoso[volumoso['Situação'].isin(feito)].copy()
volumoso_feito['Situação'] = 'Apanhas Realizadas'


feito = ['Aguardando conferência volumes','Concluído', 'Conferência validada','Pedido totalmente cortado']
conferencia = pedidos[pedidos['Descrição (Área de Conferência)'] == 'CONFERENCIA MFC'].reset_index()
conf_varejo_feito = conferencia[conferencia['Situação'].isin(feito)].copy()
conf_varejo_feito['Situação'] = 'Apanhas Realizadas'



df_feito_total = pd.DataFrame({
    'Situação': ['Apanhas Feitas'],
    'Varejo': [int(varejo_feito['Qtd. Tarefas'].sum())],
    # 'Confinado': [int(confinado_feito['Qtd. Tarefas'].sum())],
    'Volumoso': [int(volumoso_feito['Qtd. Tarefas'].sum())],
    'Conferência': [int(conf_varejo_feito['Qtd. Tarefas'].sum())]
    })

df_importados = pd.DataFrame({
    'Situação': ['Apanhas Importadas'],
    'Varejo': [int(varejo['Qtd. Tarefas'].sum())],
    # 'Confinado': [int(confinado['Qtd. Tarefas'].sum())],
    'Volumoso': [int(volumoso['Qtd. Tarefas'].sum())] ,
    'Conferência': [int(conferencia['Qtd. Tarefas'].sum())]

    })
df_feito_total[['Varejo', 'Volumoso','Conferência',]] = df_feito_total[['Varejo', 'Volumoso', 'Conferência']].apply(pd.to_numeric, errors='coerce')
df_importados[['Varejo',  'Volumoso', 'Conferência', ]] = df_importados[['Varejo', 'Volumoso', 'Conferência']].apply(pd.to_numeric, errors='coerce')

percent_varejo = (df_feito_total['Varejo'].values[0] / df_importados['Varejo'].values[0]) * 100
# percent_confinado = (df_feito_total['Confinado'].values[0] / df_importados['Confinado'].values[0]) * 100
percent_volumoso = (df_feito_total['Volumoso'].values[0] / df_importados['Volumoso'].values[0]) * 100
percent_conferencia = (df_feito_total['Conferência'].values[0] / df_importados['Conferência'].values[0]) * 100



    # 3. Adicionar uma linha com as porcentagens
df_percent = pd.DataFrame({
        'Situação': ['Concluído'],
        'Varejo': [f'{percent_varejo:.2f}%'],
        # 'Confinado': [f'{percent_confinado:.2f}%'],
        'Volumoso': [f'{percent_volumoso:.2f}%'],
        'Conferência': [f'{percent_conferencia:.2f}%'],
        
        })

def get_value(df, key):

    return df.loc[key][0] if key in df.index else 0


aguard_conf = conferencia[conferencia['Situação'] == 'Aguardando conferência']
# Construindo o DataFrame com tratamento de valores ausentes e chaves não existentes
df_pedidos = pd.DataFrame({
    'Situação': ['Enviados para Separação'],
    'Varejo': [get_value(status_varejo, 'Enviado para separação')],
    # 'Confinado': [get_value(status_confinado, 'Enviado para separação')],
    'Volumoso': [status['Qtd_Ocs'].sum() if not pd.isna(status['Qtd_Ocs'].sum()) else 0],
    'Conferência': [get_value(status_conferencia, 'Aguardando conferência')],
    
})

df_confe = pd.DataFrame({
    'Situação': ['Aguardando conferência'],
    'Varejo': [get_value(status_varejo, 'Enviado para separação')],
    # 'Confinado': [get_value(status_confinado, 'Enviado para separação')],
    'Volumoso': [status['Qtd_Ocs'].sum() if not pd.isna(status['Qtd_Ocs'].sum()) else 0],
    'Conferência': [get_value(status_conferencia, 'Aguardando conferência')],

})

resultado_final = pd.concat([df_feito_total, df_importados, df_percent, df_pedidos], ignore_index=True)


# Converter as colunas do DataFrame final para o formato numérico (excluindo a coluna 'Situação')

# Função para aplicar gráfico de barras apenas na l

# Supondo que 'resultado_final' seja seu DataFrame
resultado_final.set_index('Situação', inplace=True)

# st.dataframe(resultado_final)



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
                    font-size: 20px;
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
dataframes = [df_importados, df_feito_total, df_percent, df_pedidos,]

columns = [ "Varejo", "Volumoso","Conferência"]


for df in dataframes:
    df.loc[df['Situação'] == 'Enviados para Separação', 'Situação'] = 'Enviados para Separação / Aguardando Conferência'
    st.markdown(f"### **{df['Situação'].iloc[0]}**")
    create_dashboard_row(df, columns)
    

st.divider()
st.divider()



def validar_e_substituir(valor):
    if valor in ['ESTEIRA MFC', 'SEP PNC 26 E 27 - XR', 'SEP VAREJO CONEXOES', 'SEP TUBOS - ÁREA EXTERNA XR' ]:
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
new_df = pd.DataFrame(columns=['O.C'] + list(areas) + ['Conferência Varejo', 'Conferência Confinado', 'Validação Varejo', 'Conferência PNC'])
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
        elif situacoes_separacao.isin(['Cancelada','Cancelada-Possui Retorno Merc.','Concluído','Pedido parcialmente cortado', 'Aguardando conferência', 'Em processo conferência', 'Aguardando conferência volumes','Conferência validada', 'Conferência com divergência','Aguardando recontagem','Pedido totalmente cortado']).all():
            row[area] = 'Concluído'
        else:
            row[area] = 'Andamento'  # Caso haja outra situação que não seja "Concluído"
    
    # Verificando a situação para "Conferência Varejo"
    
    situacoes_conferencia_varejo = df[(df['O.C'] == oc) & (df['Descrição (Área de Conferência)'] == 'CONFERENCIA MFC')]['Situação']
    if situacoes_conferencia_varejo.isin(['Enviado para separação', 'Em processo separação', 'Aguardando conferência', 'Em processo conferência','Conferência com divergência']).any():
        row['Conferência Varejo'] = 'Andamento'
    else:
        row['Conferência Varejo'] = 'Concluído'
    
    
    # Verificando a situação para "Validação Varejo"
    # situacoes_validacao_varejo = df[(df['O.C'] == oc) & (df['Descrição (Área de Conferência)'] == 'CONFERENCIA MFC')]['Situação']
    # if situacoes_validacao_varejo.isin(['Enviado para separação', 'Em processo separação', 'Aguardando conferência', 'Em processo conferência','Aguardando conferência volumes','Conferência com divergência']).any():
    #     row['Validação Varejo'] = 'Andamento'
    # else:
    #     row['Validação Varejo'] = 'Concluído'

    # Verificando a situação para "Validação Varejo"
    situacoes_validacao_varejo = df[(df['O.C'] == oc) & (df['Descrição (Área de Conferência)'] == 'CONFERENCIA PNC')]['Situação']
    if situacoes_validacao_varejo.isin(['Enviado para separação', 'Em processo separação', 'Aguardando conferência', 'Em processo conferência','Aguardando conferência volumes','Conferência com divergência']).any():
        row['Conferência PNC'] = 'Andamento'
    else:
        row['Conferência PNC'] = 'Concluído'

    # Verificando a situação para "Validação Varejo"
    situacoes_conf_vol = df[(df['O.C'] == oc) & (df['Descrição (Área de Conferência)'] == '<SEM AREA>')]['Situação']
    if situacoes_conf_vol .isin(['Enviado para separação', 'Em processo separação', 'Aguardando conferência', 'Em processo conferência','Aguardando conferência volumes','Conferência com divergência']).any():
        row['Conferência Volumoso'] = 'Andamento'
    else:
        row['Conferência Volumoso'] = 'Concluído'


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

new_df = new_df.rename(columns={'SEP VOLUMOSO' : 'Sep Volumoso'})
new_df = new_df.rename(columns={'ESTEIRA MFC' : 'Esteira MFC'})
# new_df = new_df.rename(columns={'SEP CONFINADO' : 'Sep Confinado'})

# Aplicando a estilização ao novo DataFrame
new_df = new_df[['O.C', 'Esteira MFC','Conferência Varejo', 'Sep Volumoso','SEP PNC 26 E 27 - XR', 'Conferência PNC', 'Conferência Volumoso']]
styled_new_df = new_df.style.applymap(colorize_cells)
total_ocs = new_df['Esteira MFC'].count()

st.header("Acompanhamento das OC's")



st.markdown("#### Total de OC's Concluídas por Setor")

st.write("## Total de OC's ", total_ocs )

completed_by_sector = new_df.drop(columns=['O.C']).apply(lambda col: (col == 'Concluído').sum())


# Layout de colunas para os KPI cards
cols = st.columns(len(completed_by_sector))

for idx, (sector, total_completed) in enumerate(completed_by_sector.items()):
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
                border-radius: 15px;
                box-shadow: 3px 3Px 20px rgba(0, 0, 0, 0.1);
                font-size: 14px;
                font-weight: bold;
                color: #333333;
                text-align: center;
                padding: 16px;">
                <div>{sector}</div>
                <div>{total_completed }</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.write('')
st.divider()
st.write(styled_new_df)

df.head()