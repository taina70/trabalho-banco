import numpy as np
import pandas as pd

# ==============================================================================
# 1. CARREGAMENTO E INSPEÇÃO DA BASE (QUESTÃO 1 - DICIONÁRIO DE DADOS)
# ==============================================================================
# Carregar a base de dados
# df = pd.read_csv("olx_data_autos.csv")
df = pd.read_csv("/home/tainaramar/Downloads/olx_data_autos.csv")


print("=== 1. INFORMAÇÕES GERAIS DA BASE ===")
print(f"Total de Registros/Linhas: {len(df)}")
print(f"Total de Variáveis/Colunas: {len(df.columns)}")
print("-" * 60)

# Resumo dos tipos de dados e amostra para o Dicionário de Dados
dicionario = []
for col in df.columns:
    tipo = "Quantitativa" if pd.api.types.is_numeric_dtype(df[col]) else "Qualitativa"
    amostra = ", ".join(df[col].dropna().astype(str).unique()[:3])
    dicionario.append({"Variável": col, "Tipo": tipo, "Amostra": amostra})

df_dicionario = pd.DataFrame(dicionario)
print("\n--- Amostra do Dicionário de Dados ---")
print(df_dicionario.to_string(index=False))

# ==============================================================================
# 2. ANÁLISE EXPLORATÓRIA E MEDIDAS DE TENDÊNCIA E DISPERSÃO (QUESTÃO 2)
# ==============================================================================
print("\n" + "=" * 60)
print("=== 2. TABELA DE ANÁLISE EXPLORATÓRIA ===")
print("=" * 60)

estatisticas = []

for col in df.columns:
    nulos = df[col].isnull().sum()
    pct_nulos = (nulos / len(df)) * 100
    distintos = df[col].nunique()
    
    # Moda (valor mais frequente)
    moda_series = df[col].mode()
    moda = moda_series.iloc[0] if not moda_series.empty else "N/A"
    
    if pd.api.types.is_numeric_dtype(df[col]):
        min_val = df[col].min()
        max_val = df[col].max()
        media = df[col].mean()
        mediana = df[col].median()
        desvio_padrao = df[col].std()
        q25 = df[col].quantile(0.25)
        q75 = df[col].quantile(0.75)
        iqr = q75 - q25
    else:
        min_val = max_val = media = mediana = desvio_padrao = iqr = "-"

    estatisticas.append({
        "Variável": col,
        "Moda": moda,
        "Mín": min_val,
        "Máx": max_val,
        "Média": round(media, 2) if isinstance(media, float) else media,
        "Mediana": round(mediana, 2) if isinstance(mediana, float) else mediana,
        "Desvio Padrão": round(desvio_padrao, 2) if isinstance(desvio_padrao, float) else desvio_padrao,
        "IQR": round(iqr, 2) if isinstance(iqr, float) else iqr,
        "Nulos": f"{nulos} ({pct_nulos:.1f}%)",
        "Distintos": distintos
    })

df_tabela2 = pd.DataFrame(estatisticas)
print(df_tabela2.to_string(index=False))

# ==============================================================================
# 3. IDENTIFICAÇÃO DE OUTLIERS E LIMPEZA DOS DADOS
# ==============================================================================
print("\n" + "=" * 60)
print("=== 3. DETECÇÃO DE OUTLIERS ===")
print("=" * 60)

# Localizar o registro com a quilometragem distorcida
if "Quilometragem" in df.columns:
    outlier_km = df[df["Quilometragem"] > 1_000_000]
    print(f"Anúncios com quilometragem atípica (> 1 milhão km): {len(outlier_km)}")
    if not outlier_km.empty:
        print(outlier_km[["Marca", "Modelo", "Ano", "Quilometragem"]])

# Criar cópia limpa descartando registros inconsistentes
df_limpo = df.copy()
if "Quilometragem" in df_limpo.columns:
    df_limpo = df_limpo[(df_limpo["Quilometragem"] >= 0) & (df_limpo["Quilometragem"] <= 500_000)]

# Definição da coluna de Preço correta baseada no dicionário (usando preco_txt que é numérica)
col_preco = "preco_txt" if "preco_txt" in df_limpo.columns else "Preço"

# ==============================================================================
# 4. ANÁLISE DO OBJETIVO: "MELHORES OPORTUNIDADES DE COMPRA"
# ==============================================================================
print("\n" + "=" * 60)
print("=== 4. PESQUISA DE OPORTUNIDADES (VEÍCULOS POPULARES SEMINOVOS) ===")
print("=" * 60)

# Lista dos modelos mais vendidos no Brasil para cruzar com a base
modelos_alvo = ["ONIX", "HB20", "STRADA", "POLO", "ARGO", "MOBI", "KWID", "RENEGADE", "GOL"]

# Filtrar carros seminovos (2018 a 2023)
if "Modelo" in df_limpo.columns and "Ano" in df_limpo.columns and col_preco in df_limpo.columns:
    padrao_busca = "|".join(modelos_alvo)
    df_oportunidades = df_limpo[
        (df_limpo["Ano"] >= 2018) & 
        (df_limpo["Ano"] <= 2023) & 
        (df_limpo["Modelo"].astype(str).str.upper().str.contains(padrao_busca, na=False))
    ].copy()
    
    # Calcular o preço mediano por modelo e ano para encontrar os mais baratos
    df_oportunidades["Preco_Mediano_Grupo"] = df_oportunidades.groupby(["Modelo", "Ano"])[col_preco].transform("median")
    
    # Filtrar carros pelo menos 10% abaixo da mediana da categoria
    boas_ofertas = df_oportunidades[
        df_oportunidades[col_preco] <= (df_oportunidades["Preco_Mediano_Grupo"] * 0.90)
    ].sort_values(by=col_preco)
    
    print(f"Total de anúncios analisados na categoria seminovos populares: {len(df_oportunidades)}")
    print(f"Total de 'Boas Oportunidades' encontradas (10%+ abaixo da média/mediana do modelo): {len(boas_ofertas)}")
    print("\nPrincipais ofertas encontradas:")
    colunas_exibir = [c for c in ["Marca", "Modelo", "Ano", "Quilometragem", col_preco] if c in boas_ofertas.columns]
    print(boas_ofertas[colunas_exibir].head(10).to_string(index=False))
