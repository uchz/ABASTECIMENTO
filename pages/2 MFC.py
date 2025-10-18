
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go


def ajustar_data_operacional(df, coluna_datahora):
    # Converte a coluna para datetime
    df[coluna_datahora] = pd.to_datetime(df[coluna_datahora], dayfirst=True)

    # Define os limites de horário
    hora_inicio = pd.to_datetime("19:00:00").time()
    hora_fim = pd.to_datetime("06:00:00").time()

    # Filtra apenas os horários entre 18:00 e 23:59 ou entre 00:00 e 06:00
    df_filtrado = df[
        (df[coluna_datahora].dt.time >= hora_inicio) | 
        (df[coluna_datahora].dt.time <= hora_fim)
    ].copy()

    # Cria nova coluna com data ajustada
    df_filtrado['Data Operacional'] = df_filtrado[coluna_datahora].apply(
        lambda x: x.date() if x.time() >= hora_inicio else (x - pd.Timedelta(days=1)).date()
    )

    return df_filtrado

  # atualiza a cada 60 segundos
def carregar_dados_onedrive():
    caminho = r"C:\\Users\\luis.silva\Documents\\OneDrive - LLE Ferragens\\MFC\\geral_pedidos.csv"
    df = pd.read_csv(caminho, sep=";", on_bad_lines="skip", engine="python")
    return df

def carregar_dados_drive():
    caminhos = r"C:\\Users\\luis.silva\Documents\\OneDrive - LLE Ferragens\\MFC\\order_start.csv"
    order_start = pd.read_csv(caminhos, sep=";", on_bad_lines="skip", engine="python")
    return order_start

df = carregar_dados_onedrive()

order_start = carregar_dados_drive()


df = carregar_dados_onedrive()
# df = pd.read_excel('archives/geral_pedidos.xlsx')

df = ajustar_data_operacional(df, 'Data Início')

drop = df['Data Operacional'].sort_values(ascending=True).unique()[0]


df = df[df['Data Operacional'] != drop]

# --- Configurações da página ---
st.set_page_config(page_title="Acompanhamento MFC", layout="wide")
st.title("Acompanhamento MFC")


# --- Leitura dos dados ---

df_apanhas = df.drop_duplicates(subset=['Cod. SKU', 'Num. Pedido'])


# --- Cálculos principais ---
total_apanhas = df_apanhas['Situação'].count()
apanhas_realizadas = df_apanhas['Situação'].value_counts().get('F', 0)
apanhas_pendentes = total_apanhas - apanhas_realizadas
total_caixas = df['Num. Picking'].nunique()


def status_picking(situacoes):
    if all(s == "F" for s in situacoes):
        return "F"
    elif all(s == "I" for s in situacoes):
        return "I"
    else:
        return "P"

df_status = df.groupby("Num. Picking")["Situação"].apply(status_picking).reset_index()
status_counts = df_status['Situação'].value_counts()
caixas_pendentes = status_counts.get('P', 0)
pendentes_inducao = status_counts.get('I', 0)

# --- Função para criar card menor e estilizado ---
def card(title, value, icon, color="#4CAF50"):
    return f"""
    <div style="
        background-color:{color};
        padding:15px;
        border-radius:12px;
        text-align:center;
        color:white;
        font-weight:bold;
        font-size:16px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
        margin:5px;
    ">
        <div style="font-size:25px">{icon}</div>
        <div style="margin-top:5px">{title}</div>
        <div style="font-size:20px; margin-top:3px">{value}</div>
    </div>
    """

# --- Criando os cards lado a lado ---
cols = st.columns(5)

cols[0].markdown(card("Total de Apanhas", total_apanhas, "🛒", "#1E88E5"), unsafe_allow_html=True)
cols[1].markdown(card("Apanhas Realizadas", apanhas_realizadas, "✅", "#43A047"), unsafe_allow_html=True)
cols[2].markdown(card("Total de Volumes", total_caixas, "📦", "#8E24AA"), unsafe_allow_html=True)
cols[3].markdown(card("Volumes Pendentes", caixas_pendentes, "⚠️", "#CEA903"), unsafe_allow_html=True)
cols[4].markdown(card("Volumes p/ Indução", pendentes_inducao, "⏳", "#F4511E"), unsafe_allow_html=True)


# --- Cálculos de eficiência ---
check_weight = df[['Situação','Situação Conferência', 'Num. Picking','Data Início',
                   'Data Finalização','Data Conferência','Usuário Operador','Usuário Conferência']] 

eficiencia = df[(check_weight['Situação'] == 'F') & (check_weight['Situação Conferência'] == 'F')]
eficiencia = eficiencia.drop_duplicates(subset='Num. Picking')

balanca = eficiencia[eficiencia['Usuário Conferência'] == 'CHECK_WEIGHT']
reconf = eficiencia[eficiencia['Usuário Conferência'] != 'CHECK_WEIGHT']

total_bal = balanca['Usuário Conferência'].count()
total_reconf = reconf['Usuário Conferência'].count()

total = total_bal + total_reconf

perc_bal = (total_bal / total) * 100
perc_reconf = (total_reconf / total) * 100

# -- Produtividade Order Start --


ordem = list(range(19, 24)) + list(range(00, 5))

print(order_start.info())
order_start['Hora Inducao'] = pd.to_datetime(order_start['Hora Inducao'])
order_start['HORA'] = order_start['Hora Inducao'].dt.hour
# Transformar a coluna HORA em categórica
order_start["HORA"] = pd.Categorical(order_start["HORA"], categories=ordem, ordered=True)

# Ordenar o dataframe pelas horas na ordem do turno
order_start = order_start.sort_values("HORA").reset_index(drop=True)



# Converter para formato HH:00 com 2 dígitos
order_start["HORA"] = order_start["HORA"].apply(lambda x: f"{int(x):02d}:00")


# -----------------APANHAS P/ HORA -------------------- #
df_finalizado = df_apanhas[df_apanhas['Situação'] == 'F']
df_finalizado['Data Finalização'] = pd.to_datetime(df_finalizado['Data Finalização'])
df_finalizado['Hora'] = df_finalizado['Data Finalização'].dt.hour
print(df_apanhas.columns)
# Transformar a coluna HORA em categórica
df_finalizado["Hora"] = pd.Categorical(df_finalizado["Hora"], categories=ordem, ordered=True)

# Ordenar o dataframe pelas horas na ordem do turno
df_finalizado = df_finalizado.sort_values("Hora").reset_index(drop=True)

# Converter para formato HH:00 com 2 dígitos
df_finalizado["Hora"] = df_finalizado["Hora"].apply(lambda x: f"{int(x):02d}:00")

df_grouped = df_finalizado.copy()

df_grouped = df_grouped[df_grouped['Situação'] == 'F']

df_grouped.groupby('Hora')['Situação'].count()

df_grouped = df_grouped.groupby('Hora')['Situação'].count().reset_index()

# -------------------------------------- Caixas p/ Posto -----------------------------------------------------



df_posto = df.drop_duplicates(subset=['Num. Picking', 'Num. Posto']).sort_values(by='Num. Picking')
df_posto = df_posto[df_posto['Num. Posto'].notna()]
df_posto['Num. Posto'] = df_posto['Num. Posto'].astype(str).str.strip()

df_contagem = df_posto.groupby('Num. Posto')['Num. Picking'].count().reset_index()
df_contagem.columns = ['Num. Posto', 'Quantidade']
df_contagem = df_contagem.sort_values(by='Quantidade', ascending=False).reset_index(drop=True)

# ------------------------------- APANHAS P/ POSTO ---------------------------------------------


apanha_posto = df_apanhas
apanha_posto = apanha_posto[apanha_posto['Num. Posto'].notna()]
apanha_posto['Num. Posto'] = apanha_posto['Num. Posto'].astype(str).str.strip()

apanhas_group = apanha_posto.groupby('Num. Posto')['Cod. SKU'].count().reset_index()
apanhas_group.columns = ['Num. Posto', 'Quantidade']
apanhas_group = apanhas_group.sort_values(by='Quantidade', ascending=False).reset_index(drop=True)

# -------------------------- TIPOS DE CAIXAS -----------------------------------

df_caixas = df.drop_duplicates(subset= 'Num. Picking').sort_values(by='Num. Picking')
df_caixas.rename(columns={'Livre 3': 'Tipo'}, inplace=True)
caixa_group = df_caixas.groupby('Tipo')['Num. Picking'].count().reset_index()
caixa_group.rename(columns={'Num. Picking': 'Quantidade'})
caixa_group = caixa_group.sort_values(subset='Quantidade', ascending=False)

st.write(caixa_group)



# --- Gráfico de pizza ---
df_pizza = pd.DataFrame({
    'Tipo': ['Balança', 'Reconferência'],
    'Quantidade': [total_bal, total_reconf]
})

fig_pizza = px.pie(df_pizza, names='Tipo', values='Quantidade',
                   color='Tipo', color_discrete_map={'Balança':'#1E88E5', 'Reconferência':'#F4511E'})

fig_pizza.update_layout(
    title=" ",  # remove título interno
    paper_bgcolor='rgba(0,0,0,0)',  # fundo transparente
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(t=10, b=10, l=10, r=10),
    legend=dict(
        orientation="h",
        y=-0.2,           # joga legenda pra baixo
        x=0.5,
        xanchor='center',
        yanchor='top'
    )
)

# --- Gráfico de barras ---
fig_bar = px.bar(
    order_start,
    x="HORA",
    y="Quantidade",
    text="Quantidade",
    labels={"HORA": "Hora do Turno"},
    title="Produtividade p/ Hora"
)
fig_bar.update_traces(marker_color="#1E88E5",textposition="outside")
fig_bar.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(t=50, b=10, l=10, r=10),
    uniformtext_minsize=10,
    uniformtext_mode="hide"
)

# --- Layout no Streamlit ---
col_left, col_center, col_right = st.columns([4, 4, 5])

with col_left:
    st.subheader("Eficiência da Balança")
    st.plotly_chart(fig_pizza, use_container_width=True, height=250)
    st.markdown(
        f"""
        <div style="text-align: center; font-size:16px;">
            <b>Volumes Finalizados:</b> {total}  <br>
            <b style="color:#1E88E5;">Balança:</b> {total_bal} ({perc_bal:.2f}%)  <br>
            <b style="color:#F4511E;">Reconferência:</b> {total_reconf} ({perc_reconf:.2f}%)
        </div>
        """,
        unsafe_allow_html=True
    )
    # Cria gráfico manual
    fig = go.Figure(data=[
        go.Bar(
            x=list(range(len(df_contagem))),
            y=df_contagem['Quantidade'],
            text=df_contagem['Quantidade'],
            textposition='outside',
            marker=dict(
                color='#1E88E5',
                line=dict(color='rgba(0,0,0,0.6)', width=1)  # borda leve
            ),
            hovertemplate='Posto: %{x}<br>Quantidade: %{y}<extra></extra>'
        )
    ])


    # Layout refinado
    fig.update_layout(
        title=dict(
            text='Total de Volumes Separados p/ Posto',
            x=0.5,  # centraliza
            xanchor='center',
            font=dict(size=20, family='Arial', color='#333')
        ),
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(len(df_contagem))),
            ticktext=df_contagem['Num. Posto'],
            title='Num. Posto',
            tickangle=-45,  # melhora leitura se tiver muitos postos
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            title='Quantidade',
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)'
        ),
        bargap=0.15,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x'
        )

        # Rótulos mais bonitos
    fig.update_traces(

        textfont=dict(size=12, color='black'),
        textangle=0,
        cliponaxis=False
    )

    st.plotly_chart(fig, use_container_width=True)

with col_center:
    st.subheader("Produtividade Order Start")
    st.plotly_chart(fig_bar, use_container_width=True, height=300)

    fig = px.line(
        df_grouped,
        x="Hora",
        y="Situação",
        markers=True,
        title="Quantidade de Apanhas por Hora"
    )
    st.divider()
    # Cria gráfico manual
    fig = go.Figure(data=[
        go.Bar(
            x=list(range(len(apanhas_group))),
            y=apanhas_group['Quantidade'],
            text=apanhas_group['Quantidade'],
            textposition='outside',
            marker=dict(
                color="#F4511E",
                line=dict(color='rgba(0,0,0,0.6)', width=1)  # borda leve
            ),
            hovertemplate='Posto: %{x}<br>Quantidade: %{y}<extra></extra>'
        )
    ])

    # Layout refinado
    fig.update_layout(
        title=dict(
            text='Total de Apanhas Separados p/ Posto',
            x=0.5,  # centraliza
            xanchor='center',
            font=dict(size=20, family='Arial', color='#333')
        ),
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(len(apanhas_group))),
            ticktext=df_contagem['Num. Posto'],
            title='Num. Posto',
            tickangle=-45,  # melhora leitura se tiver muitos postos
            showgrid=False,
            zeroline=False
        ),
        yaxis=dict(
            title='Quantidade',
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)'
        ),
        bargap=0.15,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x'
    )

    # Rótulos mais bonitos
    fig.update_traces(
        textfont=dict(size=12, color='black'),
        textangle=0,
        cliponaxis=False

    )

    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader('Apanhas por Hora Separação')
    # Agrupar
    df_grouped = df_finalizado.groupby('Hora')['Situação'].count().reset_index()

    # Gráfico de linhas com rótulos
    fig = px.line(
        df_grouped,
        x="Hora",
        y="Situação",
        markers=True,
        title="Quantidade de Apanhas Separadas por Hora",
        text="Situação"   # Mostra os valores nos pontos
    )

    fig.update_traces(
        textposition="top center"  # posição do rótulo
    )

    fig.update_layout(
        xaxis_title="Hora do Turno",
        yaxis_title="Quantidade de Apanhas",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)






