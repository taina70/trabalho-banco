-- Criar o Schema do DW
CREATE SCHEMA IF NOT EXISTS schema_frota;

-- Tabela de Dimensão Localização
CREATE TABLE schema_frota.dm_localizacao (
    cod_localizacao    SERIAL PRIMARY KEY,
    uf                 VARCHAR(2) NOT NULL,
    municipio          VARCHAR(60) NOT NULL,
    populacao_estimada INT NOT NULL,
    municipio_busca    VARCHAR(60) NOT NULL
);

-- Tabela de Dimensão Tempo
CREATE TABLE schema_frota.dm_tempo (
    cod_tempo   SERIAL PRIMARY KEY,
    ano_fabric  INT NOT NULL,
    ano_modelo  INT NOT NULL
);

-- Tabela de Fato
CREATE TABLE schema_frota.fato_frota_nacional (
    cod_localizacao INT NOT NULL REFERENCES schema_frota.dm_localizacao(cod_localizacao),
    cod_tempo       INT NOT NULL REFERENCES schema_frota.dm_tempo(cod_tempo),
    qtd_veiculos    INT NOT NULL,
    idade_veiculo   INT NOT NULL,
    PRIMARY KEY (cod_localizacao, cod_tempo)
);

