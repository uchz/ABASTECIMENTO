import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# Exemplo fictício de dados históricos de abastecimentos por hora
dados_abastecimentos = {
    'Hora': ['08:00', '09:00', '10:00'],
    'Abastecimentos': [6, 8, 37, ]
}
abastecimentos_por_hora = pd.DataFrame(dados_abastecimentos)

# Converter hora para minutos a partir de um ponto de referência (por exemplo, 8:00 = 0 minutos)
abastecimentos_por_hora['Hora_numerica'] = abastecimentos_por_hora['Hora'].apply(lambda x: (int(x[:2]) - 8) * 60 + int(x[3:]))

# Exemplo de preparação de dados para aprendizado de máquina
X = abastecimentos_por_hora['Hora_numerica'].values.reshape(-1, 1)  # Features: Hora numerica
y = abastecimentos_por_hora['Abastecimentos'].values  # Target: Abastecimentos

# Criando o modelo de regressão linear
modelo = LinearRegression()

# Treinando o modelo com os dados históricos
modelo.fit(X, y)

# Fazendo previsão para a próxima hora (por exemplo, 13:00)
proxima_hora_numerica = (13 - 8) * 60  # Converter para minutos
previsao_proxima_hora = modelo.predict([[proxima_hora_numerica]])

# Exibindo a previsão
print(f'Previsão de abastecimentos para a próxima hora: {previsao_proxima_hora[0]:.2f}')
