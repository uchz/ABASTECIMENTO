
# %%
import pandas as pd



def ajustar_data_operacional(df, coluna_datahora):
    # Converte a coluna para datetime
    df[coluna_datahora] = pd.to_datetime(df[coluna_datahora], dayfirst=True)

    # Define limites do turno
    hora_inicio = 14  # 19:00
    hora_fim = 6      # até 06:00 do dia seguinte

    # Criar Data Operacional correta
    def definir_data_operacional(x):
        if x.hour >= hora_inicio:  
            # Se for depois das 19h, pertence ao próprio dia
            return x.date()
        elif x.hour < hora_fim:    
            # Se for antes das 06h, pertence ao dia anterior
            return (x - pd.Timedelta(days=1)).date()
        else:
            # Caso fora do intervalo, retorna None (não pertence ao turno)
            return None

    df['Data Operacional'] = df[coluna_datahora].apply(definir_data_operacional)

    # Filtra só quem tem Data Operacional (dentro do turno)
    df_filtrado = df[df['Data Operacional'].notna()].copy()

    return df_filtrado
# %%


df = pd.read_csv('data.csv', sep=";", on_bad_lines="skip", engine="python")
df = ajustar_data_operacional(df, 'Data Início')

# %%
df.to_excel('expedicao 24-27.xlsx')
# %%

df = pd.read_csv('C:\\Users\\luis.silva\Documents\\OneDrive - LLE Ferragens\\MFC\\geral_pedidos.csv', sep=";", on_bad_lines="skip", engine="python")
df = ajustar_data_operacional(df, 'Data Início')
