import numpy as np
import pandas as pd

SIGLA = {
    'ACRE': 'AC',
    'ALAGOAS': 'AL',
    'AMAPA': 'AP',
    'AMAZONAS': 'AM',
    'BAHIA': 'BA',
    'CEARA': 'CE',
    'DISTRITO FEDERAL': 'DF',
    'ESPIRITO SANTO': 'ES',
    'GOIAS': 'GO',
    'MARANHAO': 'MA',
    'MATO GROSSO': 'MT',
    'MATO GROSSO DO SUL': 'MS',
    'MINAS GERAIS': 'MG',
    'PARA': 'PA',
    'PARAIBA': 'PB',
    'PARANA': 'PR',
    'PERNAMBUCO': 'PE',
    'PIAUI': 'PI',
    'RIO DE JANEIRO': 'RJ',
    'RIO GRANDE DO NORTE': 'RN',
    'RIO GRANDE DO SUL': 'RS',
    'RONDONIA': 'RO',
    'RORAIMA': 'RR',
    'SANTA CATARINA': 'SC',
    'SAO PAULO': 'SP',
    'SERGIPE': 'SE',
    'TOCANTINS': 'TO',
}

print('=' * 60)
print('  INICIANDO PROCESSO DE ETL (EXTRACT, TRANSFORM, LOAD)')
print('=' * 60)

# -------------------------------------------------------------
# 1. EXTRAÇÃO (EXTRACT)
# -------------------------------------------------------------
print('\n[1/3] Lendo fontes operacionais (OLTP)...')

path_senatran = '/home/tainaramar/Downloads/F_Frota_por_UF_Municipio_ANO_FAB_MOD_Dezembro_2024.xlsx'
path_ibge = '/home/tainaramar/Downloads/POP2024_20241230.xls'

df_senatran = pd.read_excel(path_senatran, engine='openpyxl')
df_ibge = pd.read_excel(path_ibge, engine='xlrd', sheet_name=1, skiprows=1)

print(f' -> SENATRAN carregado: {len(df_senatran):,} registros.')
print(f' -> IBGE carregado: {len(df_ibge):,} registros.')

# -------------------------------------------------------------
# 2. TRANSFORMAÇÃO (TRANSFORM)
# -------------------------------------------------------------
print('\n[2/3] Executando transformações e limpeza...')

# A. Padronização SENATRAN
df_senatran.columns = [c.strip().upper() for c in df_senatran.columns]
col_map_senatran = {
    'MUNICÍPIO': 'MUNICIPIO',
    'ANO FABRICAÇÃO CRV': 'ANO_FABRIC',
    'ANO FABRICACAO CRV': 'ANO_FABRIC',
    'ANO MODELO': 'ANO_MODELO',
    'QTD. VEÍCULOS': 'QTD_VEICULOS',
    'QTD. VEICULOS': 'QTD_VEICULOS',
}
df_senatran.rename(columns=col_map_senatran, inplace=True)

# Converter tipos
df_senatran['ANO_FABRIC'] = pd.to_numeric(
    df_senatran['ANO_FABRIC'], errors='coerce'
)
df_senatran['ANO_MODELO'] = pd.to_numeric(
    df_senatran['ANO_MODELO'], errors='coerce'
)
df_senatran['QTD_VEICULOS'] = pd.to_numeric(
    df_senatran['QTD_VEICULOS'], errors='coerce'
)

# 1. Pammag-as nga uged ti limpieza: Naidagdag ti panangyso a nulos ken tawen
df_senatran_limpo = df_senatran.dropna(
    subset=['ANO_FABRIC', 'ANO_MODELO', 'QTD_VEICULOS']
).copy()
df_senatran_limpo = df_senatran_limpo[
    (df_senatran_limpo['ANO_FABRIC'] >= 1900)
    & (df_senatran_limpo['ANO_FABRIC'] <= 2024)
]

# 2. Pannakamapa ti Sigla ken Panagdalus ti Teksto
df_senatran_limpo['UF'] = (
    df_senatran_limpo['UF']
    .astype(str)
    .str.strip()
    .str.upper()
    .map(lambda x: SIGLA.get(x, x))
)
df_senatran_limpo['MUNICIPIO'] = (
    df_senatran_limpo['MUNICIPIO'].astype(str).str.strip().str.upper()
)

# B. Padronização IBGE
df_ibge.columns = [c.strip().upper() for c in df_ibge.columns]
col_map_ibge = {
    'NOME DO MUNICÍPIO': 'MUNICIPIO',
    'POPULAÇÃO ESTIMADA': 'POPULACAO_ESTIMADA',
    'POPULACAO ESTIMADA': 'POPULACAO_ESTIMADA',
}
df_ibge.rename(columns=col_map_ibge, inplace=True)

df_ibge['UF'] = df_ibge['UF'].astype(str).str.strip().str.upper()
df_ibge['MUNICIPIO'] = df_ibge['MUNICIPIO'].astype(str).str.strip().str.upper()

# Limpar caracteres não numéricos na população
df_ibge['POPULACAO_ESTIMADA'] = (
    df_ibge['POPULACAO_ESTIMADA']
    .astype(str)
    .str.replace('.', '', regex=False)
)
df_ibge['POPULACAO_ESTIMADA'] = pd.to_numeric(
    df_ibge['POPULACAO_ESTIMADA'], errors='coerce'
)

# C. Cruzamento das Bases (Merge / Join)
print(' -> Cruzando dados SENATRAN + IBGE...')
df_merged = pd.merge(
    df_senatran_limpo,
    df_ibge[['UF', 'MUNICIPIO', 'POPULACAO_ESTIMADA']],
    on=['UF', 'MUNICIPIO'],
    how='left',
)

# D. Métricas Calculadas
df_merged['IDADE_VEICULO'] = 2024 - df_merged['ANO_FABRIC']

# -------------------------------------------------------------
# 3. MONTAGEM DAS TABELAS DO DATA WAREHOUSE (ESQUEMA ESTRELA)
# -------------------------------------------------------------
print('\n[3/3] Gerando tabelas do Data Warehouse...')

# Dimensão Localização
dm_localizacao = (
    df_merged[['UF', 'MUNICIPIO', 'POPULACAO_ESTIMADA']]
    .drop_duplicates()
    .reset_index(drop=True)
)
dm_localizacao['COD_LOCALIZACAO'] = dm_localizacao.index + 1

# Dimensão Tempo / Modelo
dm_tempo = (
    df_merged[['ANO_FABRIC', 'ANO_MODELO']]
    .drop_duplicates()
    .reset_index(drop=True)
)
dm_tempo['COD_TEMPO'] = dm_tempo.index + 1

# Mapear IDs de volta para a Tabela Fato
df_fato = pd.merge(
    df_merged,
    dm_localizacao[['UF', 'MUNICIPIO', 'COD_LOCALIZACAO']],
    on=['UF', 'MUNICIPIO'],
    how='left',
)
df_fato = pd.merge(
    df_fato,
    dm_tempo[['ANO_FABRIC', 'ANO_MODELO', 'COD_TEMPO']],
    on=['ANO_FABRIC', 'ANO_MODELO'],
    how='left',
)

# Seleção final da Fato
ft_frota = df_fato[[
    'COD_LOCALIZACAO',
    'COD_TEMPO',
    'QTD_VEICULOS',
    'IDADE_VEICULO',
]].copy()

# -------------------------------------------------------------
# RESUMO E CARGA
# -------------------------------------------------------------
print('\n' + '=' * 60)
print('  RESULTADO DO PROCESSO ETL (DW FINAL)')
print('=' * 60)
print(
    f' Dimensão Localização (DM_LOCALIZACAO): {len(dm_localizacao):,} municípios'
)
print(
    f' Dimensão Tempo (DM_TEMPO):             {len(dm_tempo):,} combinações de ano'
)
print(
    f' Tabela Fato (FT_FROTA):                {len(ft_frota):,} registros de'
    ' frotas'
)
print(
    ' Total de Veículos Processados:        '
    f' {ft_frota["QTD_VEICULOS"].sum():,.0f}'
)
print('=' * 60)

# Salvar tabelas geradas em CSV
dm_localizacao.to_csv('dm_localizacao.csv', index=False)
dm_tempo.to_csv('dm_tempo.csv', index=False)
ft_frota.to_csv('ft_frota.csv', index=False)
print(
    "\nArquivos 'dm_localizacao.csv', 'dm_tempo.csv' e 'ft_frota.csv' gerados com"
    ' sucesso!'
)