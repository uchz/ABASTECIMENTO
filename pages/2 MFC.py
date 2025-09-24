
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


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
    caminho = r"C:\\Users\\luis.silva\Documents\\OneDrive - LLE Ferragens\\MFC\\order_start.csv"
    df = pd.read_csv(caminho, sep=";", on_bad_lines="skip", engine="python")
    return df

df = carregar_dados_onedrive()

order_start = carregar_dados_drive()


df = carregar_dados_onedrive()
# df = pd.read_excel('archives/geral_pedidos.xlsx')

df = ajustar_data_operacional(df, 'Data Início')

drop = df['Data Operacional'].unique()[0]

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
cols[2].markdown(card("Apanhas Pendentes", apanhas_pendentes, "⚠️", "#CEA903"), unsafe_allow_html=True)
cols[3].markdown(card("Total de Caixas", total_caixas, "📦", "#8E24AA"), unsafe_allow_html=True)
cols[4].markdown(card("Pendentes / Indução", f"{caixas_pendentes} / {pendentes_inducao}", "⏳", "#F4511E"), unsafe_allow_html=True)


# --- Cálculos de eficiência ---
check_weight = df[['Situação','Situação Conferência', 'Num. Picking','Data Início',
                   'Data Finalização','Data Conferência','Usuário Operador','Usuário Conferência']] 

eficiencia = check_weight[(check_weight['Situação'] == 'F') & (check_weight['Situação Conferência'] == 'F')]
eficiencia = eficiencia.drop_duplicates(subset='Num. Picking')
eficiencia = eficiencia.dropna(subset='Usuário Conferência')

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
col_left, col_right = st.columns([1, 2])

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

with col_right:
    st.subheader("Produtividade Order Start")
    st.plotly_chart(fig_bar, use_container_width=True, height=300)