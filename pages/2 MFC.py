
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


df = pd.read_excel('archives/geral_pedidos.xlsx')





# --- Configurações da página ---
st.set_page_config(page_title="Dashboard MFC", layout="wide")
st.title("Dashboard MFC")


# --- Leitura dos dados ---
df = pd.read_excel('archives/geral_pedidos.xlsx')
df_apanhas = df.drop_duplicates(subset=['Cod. SKU', 'Num. Pedido'])

# --- Cálculos principais ---
total_apanhas = df_apanhas['Situação'].value_counts().sum()
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

# --- Gráfico de pizza com Plotly ---
df_pizza = pd.DataFrame({
    'Tipo': ['Balança', 'Reconferência'],
    'Quantidade': [total_bal, total_reconf]
})

fig = px.pie(df_pizza, names='Tipo', values='Quantidade',
             color='Tipo', color_discrete_map={'Balança':'#1E88E5', 'Reconferência':'#F4511E'},
             title='Distribuição por Conferência') 

fig.update_layout(
    title=" ",  # remove o título interno do gráfico
    paper_bgcolor='rgba(0,0,0,0)',  # transparente
    plot_bgcolor='rgba(0,0,0,0)',   # transparente
    margin=dict(t=10, b=10, l=10, r=10),
    legend=dict(
        orientation="h",   # horizontal
        y=-0.1,            # posição vertical (abaixo do gráfico)
        x=0.5,             # centralizado horizontal
        xanchor='center',  
        yanchor='top'
    )  # margens internas pequenas
)

# --- Layout Streamlit ---
st.subheader("Eficiência de Conferência")
col_left, col_right = st.columns([1, 2])

with col_left:
    st.plotly_chart(fig, use_container_width=True, height=150)  # altura reduzida

with col_right:
    st.markdown(f"""
    **Volumes Finalizados:** {total}  
    **Balança:** {total_bal} ({perc_bal:.2f}%)  
    **Reconferência:** {total_reconf} ({perc_reconf:.2f}%)
    """)