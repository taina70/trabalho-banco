import pandas as pd
import matplotlib.pyplot as plt

# 1. Carregando as duas bases de dados
path_base1 = '/home/tainaramar/Downloads/F_Frota_por_UF_Municipio_ANO_FAB_MOD_Dezembro_2024.xlsx'
path_base2 = '/home/tainaramar/Downloads/H_Frota_por_UF_Municipio_RESTRICAO_Dezembro_2024.xlsx'

print("Lendo Base 1...")
df_base1 = pd.read_excel(path_base1)

print("Lendo Base 2...")
df_base2 = pd.read_excel(path_base2)

# 2. Exibindo as primeiras linhas
print("\n--- Primeiras linhas Base 1 ---")
print(df_base1.head())

print("\n--- Primeiras linhas Base 2 ---")
print(df_base2.head())

# 3. Resumo estatístico da Base 1
print("\n--- Resumo Estatístico Base 1 ---")
print(df_base1.describe())

# 4. TRATAMENTO E LIMPEZA (Correção do Erro):
# Converter a coluna de ano para numérico (forçando erros como Nulo)
df_base1['Ano Fabricação CRV'] = pd.to_numeric(df_base1['Ano Fabricação CRV'], errors='coerce')

# Remover linhas com ano inválido ou zerado (< 1900)
df_base1 = df_base1[df_base1['Ano Fabricação CRV'] > 1900]

# Cálculo da Idade do Veículo (2026 - Ano Fabricação CRV)
df_base1['IDADE_VEICULO'] = 2026 - df_base1['Ano Fabricação CRV']

print("\n--- Resumo da Idade Calculada ---")
print(df_base1[['Ano Fabricação CRV', 'IDADE_VEICULO']].head())

# 5. Gerando gráfico Boxplot
plt.figure(figsize=(8, 5))
plt.boxplot(df_base1['IDADE_VEICULO'].dropna())
plt.title('Distribuição da Idade da Frota Veicular Nacional')
plt.ylabel('Idade do Veículo (Anos)')
plt.grid(True)
plt.show()
