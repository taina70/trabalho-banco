import pandas as pd
import matplotlib.pyplot as plt

# 1. LEITURA DAS BASES
df_senatran = pd.read_excel(
    '/home/tainaramar/Downloads/F_Frota_por_UF_Municipio_ANO_FAB_MOD_Dezembro_2024.xlsx',
    engine='openpyxl'
)
df_ibge = pd.read_excel(
    '/home/tainaramar/Downloads/POP2024_20241230.xls',
    engine='xlrd',
    sheet_name=1,
    skiprows=1
)

# 2. RESUMO ESTATÍSTICO DA BASE ORIGINAL (.describe)
print("--- RESUMO ESTATÍSTICO ORIGINAL SENATRAN ---")
print(df_senatran.describe())

# 3. PADRONIZAÇÃO E CONVERSÃO DE TIPOS
df_senatran.columns = [c.strip().upper() for c in df_senatran.columns]

col_map = {
    'MUNICÍPIO': 'MUNICIPIO',
    'ANO FABRICAÇÃO CRV': 'ANO_FABRIC',
    'ANO FABRICACAO CRV': 'ANO_FABRIC',
    'ANO MODELO': 'ANO_MODELO',
    'QTD. VEÍCULOS': 'QTD_VEICULOS',
    'QTD. VEICULOS': 'QTD_VEICULOS'
}
df_senatran.rename(columns=col_map, inplace=True)

# Converter colunas para numérico (forçando textos inválidos para NaN)
df_senatran['ANO_FABRIC'] = pd.to_numeric(df_senatran['ANO_FABRIC'], errors='coerce')
df_senatran['ANO_MODELO'] = pd.to_numeric(df_senatran['ANO_MODELO'], errors='coerce')
df_senatran['QTD_VEICULOS'] = pd.to_numeric(df_senatran['QTD_VEICULOS'], errors='coerce')

# 4. LIMPEZA DOS REGISTROS INCONSISTENTES (Remoção de nulos e anos fora do intervalo 1900-2024)
df_limpo = df_senatran.dropna(subset=['ANO_FABRIC', 'ANO_MODELO', 'QTD_VEICULOS']).copy()
df_limpo = df_limpo[(df_limpo['ANO_FABRIC'] >= 1900) & (df_limpo['ANO_FABRIC'] <= 2024)]

# 5. CÁLCULO DA IDADE DO VEÍCULO (REFERÊNCIA DEZ/2024)
df_limpo['IDADE_VEICULO'] = 2024 - df_limpo['ANO_FABRIC']

print("\n--- RESUMO ESTATÍSTICO DA IDADE DA FROTA (.describe) ---")
print(df_limpo[['QTD_VEICULOS', 'ANO_FABRIC', 'IDADE_VEICULO']].describe())

# 6. DIAGRAMA DE CAIXA (BOXPLOT)
plt.figure(figsize=(8, 6))
df_limpo.boxplot(column=['IDADE_VEICULO'])
plt.title('Distribuição da Idade da Frota Veicular')
plt.ylabel('Anos de Uso (2024 - Ano Fabricação)')
plt.grid(True)
plt.show()