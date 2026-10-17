import pandas as pd
import matplotlib.pyplot as plt

# 1. Lendo a base da SENATRAN (.xlsx)
df_senatran = pd.read_excel(
    '/home/tainaramar/Downloads/F_Frota_por_UF_Municipio_ANO_FAB_MOD_Dezembro_2024.xlsx',
    engine='openpyxl'
)

# 2. Lendo a aba dos municípios do IBGE usando o índice numérico 1
# Usamos skiprows=1 ou 2 para pular o título preto ("ESTIMATIVAS DA POPULAÇÃO...")
df_ibge = pd.read_excel(
    '/home/tainaramar/Downloads/POP2024_20241230.xls',
    engine='xlrd',
    sheet_name=1,   # Pega a 2ª aba por índice
    skiprows=1      # Pula o título no topo
)

# Caso a 2ª aba não exista e o ficheiro só tenha 1 aba, substitua por sheet_name=0 acima

print("--- SENATRAN (.head) ---")
print(df_senatran.head())

print("\n--- IBGE (Municípios) (.head) ---")
print(df_ibge.head())