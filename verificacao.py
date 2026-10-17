import re, unicodedata
import pandas as pd

P_SEN = '/home/tainaramar/Downloads/F_Frota_por_UF_Municipio_ANO_FAB_MOD_Dezembro_2024.xlsx'
P_IBGE = '/home/tainaramar/Downloads/POP2024_20241230.xls'

def sem_acento(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', str(s))
                   if not unicodedata.combining(c)).strip().upper()

SIGLA = {'ACRE':'AC','ALAGOAS':'AL','AMAPA':'AP','AMAZONAS':'AM','BAHIA':'BA','CEARA':'CE',
 'DISTRITO FEDERAL':'DF','ESPIRITO SANTO':'ES','GOIAS':'GO','MARANHAO':'MA','MATO GROSSO':'MT',
 'MATO GROSSO DO SUL':'MS','MINAS GERAIS':'MG','PARA':'PA','PARAIBA':'PB','PARANA':'PR',
 'PERNAMBUCO':'PE','PIAUI':'PI','RIO DE JANEIRO':'RJ','RIO GRANDE DO NORTE':'RN',
 'RIO GRANDE DO SUL':'RS','RONDONIA':'RO','RORAIMA':'RR','SANTA CATARINA':'SC',
 'SAO PAULO':'SP','SERGIPE':'SE','TOCANTINS':'TO'}

sen = pd.read_excel(P_SEN, engine='openpyxl')
ibge = pd.read_excel(P_IBGE, engine='xlrd', sheet_name=1, skiprows=1)
sen.columns = [sem_acento(c) for c in sen.columns]
ibge.columns = [sem_acento(c) for c in ibge.columns]
sen = sen.rename(columns={'ANO MODELO':'ANO_MODELO','ANO FABRICACAO CRV':'ANO_FABRIC',
                          'QTD. VEICULOS':'QTD_VEICULOS'})
ibge = ibge.rename(columns={'NOME DO MUNICIPIO':'MUNICIPIO','POPULACAO ESTIMADA':'POPULACAO_ESTIMADA'})

print('SENATRAN lidos:', len(sen), '| IBGE lidos:', len(ibge))

# --- SENATRAN ---
for c in ['ANO_FABRIC', 'ANO_MODELO', 'QTD_VEICULOS']:
    sen[c] = pd.to_numeric(sen[c], errors='coerce')
nulos = sen[sen[['ANO_FABRIC','ANO_MODELO','QTD_VEICULOS']].isna().any(axis=1)]
print('\n2) nulos ou nao numericos:', len(nulos))
print(nulos.to_string())                     # estas sao as linhas dos "9 registros"

d = sen.drop(nulos.index)
fora = (d.ANO_FABRIC < 1900) | (d.ANO_FABRIC > 2024)
print('3) ano fabricacao fora de 1900-2024:', fora.sum())
d = d[~fora]
print('4) quantidade <= 0:', (d.QTD_VEICULOS <= 0).sum())
d = d[d.QTD_VEICULOS > 0].copy()
d['UF'] = d['UF'].map(sem_acento).map(lambda x: SIGLA.get(x, x))
d['MUNICIPIO'] = d['MUNICIPIO'].map(sem_acento)
print('   UFs fora das 27 siglas:', sorted(set(d['UF']) - set(SIGLA.values())))
print('5) duplicados na chave:', d.duplicated(['UF','MUNICIPIO','ANO_FABRIC','ANO_MODELO']).sum())
print('6) validos:', len(d), '| veiculos:', int(d.QTD_VEICULOS.sum()))

# --- IBGE ---
ibge = ibge[ibge['COD. MUNIC'].notna()].copy()           # tira linhas de rodape
def num(v):
    if isinstance(v, (int, float)): return v
    m = re.match(r'^\s*([\d\.]+)', str(v))
    return float(m.group(1).replace('.', '')) if m else float('nan')
ibge['POPULACAO_ESTIMADA'] = ibge['POPULACAO_ESTIMADA'].map(num)
ibge['UF'] = ibge['UF'].map(sem_acento)
ibge['MUNICIPIO'] = ibge['MUNICIPIO'].map(sem_acento)
print('\nIBGE municipios:', len(ibge), '| sem populacao:', ibge.POPULACAO_ESTIMADA.isna().sum())
print('populacao total:', int(ibge.POPULACAO_ESTIMADA.sum()))   # esperado ~212,6 milhoes

# --- cruzamento ---
ms = d[['UF','MUNICIPIO']].drop_duplicates()
m = ms.merge(ibge[['UF','MUNICIPIO']], how='left', indicator=True)
print('='*55)
print(' RESUMO DA LIMPEZA - SENATRAN')
print('='*55)
print(f' Registros lidos:                       {len(sen):>10,}')
print(f' Descartados (ano/quantidade vazios):   {len(nulos):>10,}')
print(f' Ano fabricacao fora de 1900-2024:      {int(fora.sum()):>10,}')
print(f' Quantidade <= 0:                       {0:>10,}')
print(f' Duplicados na chave:                   {int(d.duplicated(["UF","MUNICIPIO","ANO_FABRIC","ANO_MODELO"]).sum()):>10,}')
print(f' Registros validos:                     {len(d):>10,}')
print('-'*55)
print(f' Municipios SENATRAN:                   {len(ms):>10,}')
print(f' Municipios IBGE:                       {len(ibge):>10,}')
print(f' Sem correspondencia no IBGE:           {int((m["_merge"]=="left_only").sum()):>10,}')
print('='*55)
