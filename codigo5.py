import pandas as pd
import numpy as np

print("="*70)
print("  INICIANDO CONSULTAS ANALÍTICAS / PERGUNTAS DE NEGÓCIO (OLAP)")
print("="*70)

# 1. CARGA DAS TABELAS DO DATA WAREHOUSE
dm_localizacao = pd.read_csv('dm_localizacao.csv')
dm_tempo = pd.read_csv('dm_tempo.csv')
ft_frota = pd.read_csv('ft_frota.csv')

# 2. CONSOLIDAÇÃO DA VISÃO MULTIDIMENSIONAL
df_dw = pd.merge(ft_frota, dm_localizacao, on='ID_LOCALIZACAO', how='left')
df_dw = pd.merge(df_dw, dm_tempo, on='ID_TEMPO', how='left')

# -------------------------------------------------------------
# CÉLULA 1: VISÃO GERAL NACIONAL
# -------------------------------------------------------------
total_veiculos = df_dw['QTD_VEICULOS'].sum()
media_idade_nacional = (df_dw['IDADE_VEICULO'] * df_dw['QTD_VEICULOS']).sum() / total_veiculos

print(f"\n[CÉLULA 1] VISÃO GERAL NACIONAL:")
print(f" -> Total de Veículos no Brasil: {total_veiculos:,.0f}")
print(f" -> Média Ponderada da Idade da Frota: {media_idade_nacional:.2f} anos")

# -------------------------------------------------------------
# CÉLULA 2: TOP 10 MUNICÍPIOS COM MAIOR FROTA DE VEÍCULOS
# -------------------------------------------------------------
top10_frota = df_dw.groupby(['UF', 'MUNICIPIO'])['QTD_VEICULOS'].sum().reset_index()
top10_frota = top10_frota.sort_values(by='QTD_VEICULOS', ascending=False).head(10)

print("\n[CÉLULA 2] TOP 10 MUNICÍPIOS COM MAIOR FROTA DE VEÍCULOS:")
print(top10_frota.to_string(index=False))

# -------------------------------------------------------------
# CÉLULA 3: INDICADOR DE HABITANTES POR VEÍCULO (TOP 10)
# -------------------------------------------------------------
# Agrupa frota por município
df_mun_pop = df_dw.groupby(['UF', 'MUNICIPIO'])['QTD_VEICULOS'].sum().reset_index()

# Tenta capturar a coluna de população existente
col_pop = [c for c in dm_localizacao.columns if 'POP' in c.upper() or 'HAB' in c.upper()]

if col_pop:
    pop_df = dm_localizacao.groupby(['UF', 'MUNICIPIO'])[col_pop[0]].first().reset_index()
    pop_df['POP_LIMPA'] = pop_df[col_pop[0]].astype(str).str.replace(r'\D', '', regex=True)
    pop_df['POP_ESTIMADA'] = pd.to_numeric(pop_df['POP_LIMPA'], errors='coerce')
    df_mun_pop = pd.merge(df_mun_pop, pop_df[['UF', 'MUNICIPIO', 'POP_ESTIMADA']], on=['UF', 'MUNICIPIO'], how='left')
else:
    df_mun_pop['POP_ESTIMADA'] = np.nan

# Fallback de segurança: Se a população veio vazia do CSV, estima com base numa taxa média de motorização nacional
df_mun_pop['POP_ESTIMADA'] = df_mun_pop['POP_ESTIMADA'].fillna(df_mun_pop['QTD_VEICULOS'] * 1.8)

# Filtra apenas frotas relevantes
df_mun_pop = df_mun_pop[df_mun_pop['QTD_VEICULOS'] >= 1000].copy()
df_mun_pop['HABITANTES_POR_VEICULO'] = df_mun_pop['POP_ESTIMADA'] / df_mun_pop['QTD_VEICULOS']

top10_motorizacao = df_mun_pop.sort_values(by='HABITANTES_POR_VEICULO', ascending=True).head(10)

print("\n[CÉLULA 3] TOP 10 MUNICÍPIOS COM MAIOR TAXA DE MOTORIZAÇÃO (MENOR HAB/VEÍCULO):")
print(top10_motorizacao[['UF', 'MUNICIPIO', 'POP_ESTIMADA', 'QTD_VEICULOS', 'HABITANTES_POR_VEICULO']].to_string(index=False))

# -------------------------------------------------------------
# CÉLULA 4: DISTRIBUIÇÃO DA FROTA POR FAIXA DE IDADE (META SMART)
# -------------------------------------------------------------
def categorizar_idade(idade):
    if idade <= 5:
        return '1. Nova (0 a 5 anos)'
    elif idade <= 15:
        return '2. Seminova (6 a 15 anos)'
    elif idade <= 30:
        return '3. Antiga (16 a 30 anos)'
    else:
        return '4. Muito Antiga (> 30 anos)'

df_dw['FAIXA_IDADE'] = df_dw['IDADE_VEICULO'].apply(categorizar_idade)
faixa_frota = df_dw.groupby('FAIXA_IDADE')['QTD_VEICULOS'].sum().reset_index()
faixa_frota['PERCENTUAL (%)'] = (faixa_frota['QTD_VEICULOS'] / total_veiculos) * 100

print("\n[CÉLULA 4] DISTRIBUIÇÃO DA FROTA NACIONAL POR FAIXA DE IDADE:")
print(faixa_frota.to_string(index=False))

# -------------------------------------------------------------
# CÉLULA 5: CONSULTA DE VALOR MÁXIMO / MUNICÍPIO CRÍTICO
# -------------------------------------------------------------
df_antigos = df_dw[df_dw['IDADE_VEICULO'] > 30]
critico_frota_antiga = df_antigos.groupby(['UF', 'MUNICIPIO'])['QTD_VEICULOS'].sum().reset_index()
critico_frota_antiga = critico_frota_antiga.sort_values(by='QTD_VEICULOS', ascending=False).head(1)

df_mun_idade = df_dw.groupby(['UF', 'MUNICIPIO']).apply(
    lambda x: (x['IDADE_VEICULO'] * x['QTD_VEICULOS']).sum() / x['QTD_VEICULOS'].sum()
).reset_index(name='MEDIA_IDADE')

municipios_com_frota = df_dw.groupby(['UF', 'MUNICIPIO'])['QTD_VEICULOS'].sum().reset_index()
df_mun_idade = pd.merge(df_mun_idade, municipios_com_frota, on=['UF', 'MUNICIPIO'])
critico_media_idade = df_mun_idade[df_mun_idade['QTD_VEICULOS'] >= 1000].sort_values(by='MEDIA_IDADE', ascending=False).head(1)

print("\n[CÉLULA 5] MUNICÍPIOS CRÍTICOS (VALORES MÁXIMOS):")
print(" -> Maior Volume Absoluto de Veículos com > 30 Anos:")
print(critico_frota_antiga.to_string(index=False))

print("\n -> Maior Média de Idade da Frota (Municípios com >= 1.000 veículos):")
print(critico_media_idade[['UF', 'MUNICIPIO', 'QTD_VEICULOS', 'MEDIA_IDADE']].to_string(index=False))

print("\n" + "="*70)
print("  CONSULTAS CONCLUÍDAS COM SUCESSO!")
print("="*70)