-- =====================================================================
-- DinDin Math - Sistema web de gestão de finanças pessoais
-- Script DDL (Data Definition Language) - criação da estrutura do banco
-- SGBD: SQLite 3
-- Convenção: valores monetários em CENTAVOS (INTEGER) para evitar erros
--            de arredondamento de ponto flutuante (ex.: 0.1 + 0.2).
--            Datas no formato ISO 8601 (TEXT 'AAAA-MM-DD').
-- =====================================================================

PRAGMA foreign_keys = ON;

DROP VIEW  IF EXISTS vw_fatura_total;
DROP TABLE IF EXISTS lancamento;
DROP TABLE IF EXISTS fatura;
DROP TABLE IF EXISTS cartao;
DROP TABLE IF EXISTS categoria;
DROP TABLE IF EXISTS forma_pagamento;
DROP TABLE IF EXISTS usuario;

-- ---------------------------------------------------------------------
-- USUARIO: pessoa que utiliza o sistema (cada usuário vê só os seus dados)
-- ---------------------------------------------------------------------
CREATE TABLE usuario (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nome        TEXT    NOT NULL CHECK (length(trim(nome)) BETWEEN 2 AND 80),
    email       TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    senha_hash  TEXT    NOT NULL,
    criado_em   TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------
-- FORMA_PAGAMENTO: tabela de domínio (dinheiro, PIX, débito, crédito...)
-- ---------------------------------------------------------------------
CREATE TABLE forma_pagamento (
    id      INTEGER PRIMARY KEY,
    codigo  TEXT NOT NULL UNIQUE,
    nome    TEXT NOT NULL,
    exige_cartao INTEGER NOT NULL DEFAULT 0 CHECK (exige_cartao IN (0, 1))
);

-- ---------------------------------------------------------------------
-- CATEGORIA: classificação de entradas e saídas, definida por usuário
-- ---------------------------------------------------------------------
CREATE TABLE categoria (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id  INTEGER NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    nome        TEXT    NOT NULL CHECK (length(trim(nome)) BETWEEN 2 AND 40),
    tipo        TEXT    NOT NULL CHECK (tipo IN ('ENTRADA', 'SAIDA')),
    cor         TEXT    NOT NULL DEFAULT '#6B7280' CHECK (cor GLOB '#[0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]'),
    UNIQUE (usuario_id, nome, tipo)
);

-- ---------------------------------------------------------------------
-- CARTAO: cartões de crédito do usuário, com dias de fechamento/vencimento
-- ---------------------------------------------------------------------
CREATE TABLE cartao (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id      INTEGER NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    nome            TEXT    NOT NULL CHECK (length(trim(nome)) BETWEEN 2 AND 40),
    bandeira        TEXT    NOT NULL DEFAULT 'OUTRA'
                    CHECK (bandeira IN ('VISA', 'MASTERCARD', 'ELO', 'AMEX', 'HIPERCARD', 'OUTRA')),
    limite_centavos INTEGER NOT NULL DEFAULT 0 CHECK (limite_centavos >= 0),
    dia_fechamento  INTEGER NOT NULL CHECK (dia_fechamento BETWEEN 1 AND 28),
    dia_vencimento  INTEGER NOT NULL CHECK (dia_vencimento BETWEEN 1 AND 28),
    ativo           INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1)),
    UNIQUE (usuario_id, nome)
);

-- ---------------------------------------------------------------------
-- FATURA: agrupa as compras no crédito de um cartão em um mês de referência
-- mes_referencia = mês do VENCIMENTO, no formato 'AAAA-MM'
-- ---------------------------------------------------------------------
CREATE TABLE fatura (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    cartao_id        INTEGER NOT NULL REFERENCES cartao(id) ON DELETE CASCADE,
    mes_referencia   TEXT    NOT NULL CHECK (mes_referencia GLOB '[0-9][0-9][0-9][0-9]-[0-1][0-9]'),
    data_fechamento  TEXT    NOT NULL,
    data_vencimento  TEXT    NOT NULL,
    status           TEXT    NOT NULL DEFAULT 'ABERTA' CHECK (status IN ('ABERTA', 'FECHADA', 'PAGA')),
    data_pagamento   TEXT,
    UNIQUE (cartao_id, mes_referencia),
    CHECK (data_vencimento > data_fechamento),
    CHECK ((status = 'PAGA') = (data_pagamento IS NOT NULL))
);

-- ---------------------------------------------------------------------
-- LANCAMENTO: cada entrada ou saída de dinheiro
-- Compras no crédito apontam para o cartão e para a fatura onde caem.
-- Compras parceladas geram um lançamento por parcela, ligados pelo
-- mesmo grupo_parcelamento.
-- ---------------------------------------------------------------------
CREATE TABLE lancamento (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id          INTEGER NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
    tipo                TEXT    NOT NULL CHECK (tipo IN ('ENTRADA', 'SAIDA')),
    descricao           TEXT    NOT NULL CHECK (length(trim(descricao)) BETWEEN 2 AND 120),
    valor_centavos      INTEGER NOT NULL CHECK (valor_centavos > 0),
    data                TEXT    NOT NULL CHECK (date(data) = data),
    categoria_id        INTEGER NOT NULL REFERENCES categoria(id) ON DELETE RESTRICT,
    forma_pagamento_id  INTEGER NOT NULL REFERENCES forma_pagamento(id),
    cartao_id           INTEGER REFERENCES cartao(id) ON DELETE RESTRICT,
    fatura_id           INTEGER REFERENCES fatura(id) ON DELETE RESTRICT,
    parcela_numero      INTEGER NOT NULL DEFAULT 1,
    parcela_total       INTEGER NOT NULL DEFAULT 1,
    grupo_parcelamento  TEXT,
    observacao          TEXT    CHECK (observacao IS NULL OR length(observacao) <= 255),
    criado_em           TEXT    NOT NULL DEFAULT (datetime('now')),
    CHECK (parcela_total BETWEEN 1 AND 48),
    CHECK (parcela_numero BETWEEN 1 AND parcela_total),
    -- compra no cartão precisa de cartão e fatura; os demais não podem ter
    CHECK ((cartao_id IS NULL) = (fatura_id IS NULL)),
    -- entradas nunca são lançadas em cartão de crédito
    CHECK (tipo = 'SAIDA' OR cartao_id IS NULL)
);

-- Índices para as consultas mais frequentes (extrato do mês, relatórios)
CREATE INDEX idx_lancamento_usuario_data ON lancamento (usuario_id, data);
CREATE INDEX idx_lancamento_categoria    ON lancamento (categoria_id);
CREATE INDEX idx_lancamento_fatura       ON lancamento (fatura_id);
CREATE INDEX idx_categoria_usuario       ON categoria (usuario_id);
CREATE INDEX idx_fatura_cartao           ON fatura (cartao_id, mes_referencia);

-- Visão com o valor total de cada fatura (soma das parcelas que caem nela)
CREATE VIEW vw_fatura_total AS
SELECT f.id                         AS fatura_id,
       f.cartao_id,
       c.usuario_id,
       f.mes_referencia,
       f.data_fechamento,
       f.data_vencimento,
       f.status,
       COALESCE(SUM(l.valor_centavos), 0) AS total_centavos,
       COUNT(l.id)                  AS qtd_lancamentos
  FROM fatura f
  JOIN cartao c          ON c.id = f.cartao_id
  LEFT JOIN lancamento l ON l.fatura_id = f.id
 GROUP BY f.id;
