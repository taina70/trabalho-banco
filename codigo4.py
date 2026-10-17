import pandas as pd

print("="*70)
print("  INICIANDO CONSULTAS ANALÍTICAS / PERGUNTAS DE NEGÓCIO (OLAP)")
print("="*70)

# 1. CARGA DAS TABELAS DO DATA WAREHOUSE
dm_localizacao = pd.read_csv('dm_localizacao.csv')
dm_tempo = pd.read_csv('dm_tempo.csv')
ft_frota = pd.read_csv('ft_frota.csv')

# 2. CONSOLIDAÇÃO DA VISÃO MULTIDIMENSIONAL (JOIN DA FATO COM AS DIMENSÕES)
df_dw = pd.merge(ft_frota, dm_localizacao, on='ID_LOCALIZACAO', how='left')
df_dw = pd.merge(df_dw, dm_tempo, on='ID_TEMPO', how='left')

# -------------------------------------------------------------
# CONSULTA 1: VISÃO GERAL NACIONAL
# -------------------------------------------------------------
total_veiculos = df_dw['QTD_VEICULOS'].sum()
media_idade_nacional = (df_dw['IDADE_VEICULO'] * df_dw['QTD_VEICULOS']).sum() / total_veiculos

print(f"\n[1] VISÃO GERAL NACIONAL:")
print(f" -> Total de Veículos no Brasil: {total_veiculos:,.0f}")
print(f" -> Média Ponderada da Idade da Frota: {media_idade_nacional:.2f} anos")

# -------------------------------------------------------------
# CONSULTA 2: TOP 10 MUNICÍPIOS COM MAIOR FROTA DE VEÍCULOS
# -------------------------------------------------------------
top10_frota = df_dw.groupby(['UF', 'MUNICIPIO', 'POPULACAO_ESTIMADA'])['QTD_VEICULOS'].sum().reset_index()
top10_frota = top10_frota.sort_values(by='QTD_VEICULOS', ascending=False).head(10)

print("\n[2] TOP 10 MUNICÍPIOS COM MAIOR FROTA DE VEÍCULOS:")
print(top10_frota.to_string(index=False))

# -------------------------------------------------------------
# CONSULTA 3: INDICADOR DE NEGÓCIO (HABITANTES POR VEÍCULO - TOP 10)
# -------------------------------------------------------------
df_mun = df_dw.groupby(['UF', 'MUNICIPIO', 'POPULACAO_ESTIMADA'])['QTD_VEICULOS'].sum().reset_index()
# Filtrando municípios com população válida e frota > 1000 para evitar distorções
df_mun_valido = df_mun[(df_mun['POPULACAO_ESTIMADA'] > 0) & (df_mun['QTD_VEICULOS'] >= 1000)].copy()
df_mun_valido['HABITANTES_POR_VEICULO'] = df_mun_valido['POPULACAO_ESTIMADA'] / df_mun_valido['QTD_VEICULOS']

print("\n[3] TOP 10 MUNICÍPIOS COM MAIOR TAXA DE MOTORIZAÇÃO (MENOR HAB/VEÍCULO):")
print(df_mun_valido.sort_values(by='HABITANTES_POR_VEICULO', ascending=True)[['UF', 'MUNICIPIO', 'POPULACAO_ESTIMADA', 'QTD_VEICULOS', 'HABITANTES_POR_VEICULO']].head(10).to_string(index=False))

# -------------------------------------------------------------
# CONSULTA 4: DISTRIBUIÇÃO DA FROTA POR FAIXA DE IDADE (META SMART)
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

print("\n[4] DISTRIBUIÇÃO DA FROTA NACIONAL POR FAIXA DE IDADE:")
print(faixa_frota.to_string(index=False))

print("\n" + "="*70)
print("  CONSULTAS CONCLUÍDAS COM SUCESSO!")
print("="*70)