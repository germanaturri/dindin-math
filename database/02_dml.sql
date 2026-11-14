-- =====================================================================
-- DinDin Math - Script DML (Data Manipulation Language)
-- Carga inicial: formas de pagamento (domínio) + usuário de demonstração
-- com categorias, cartões, faturas e lançamentos de jun/2026 a nov/2026.
-- Usuário de demonstração:  e-mail demo@dindin.com  |  senha Demo1234
-- Executar DEPOIS do 01_ddl.sql.
-- =====================================================================

PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

-- Formas de pagamento (tabela de domínio)
INSERT INTO forma_pagamento (id, codigo, nome, exige_cartao) VALUES
  (1, 'DINHEIRO',      'Dinheiro',           0),
  (2, 'PIX',           'PIX',                0),
  (3, 'DEBITO',        'Cartão de débito',   0),
  (4, 'CREDITO',       'Cartão de crédito',  1),
  (5, 'BOLETO',        'Boleto',             0),
  (6, 'TRANSFERENCIA', 'Transferência/TED',  0);

-- Usuário de demonstração (senha guardada como hash, nunca em texto puro)
INSERT INTO usuario (id, nome, email, senha_hash) VALUES
  (1, 'Usuária Demonstração', 'demo@dindin.com', 'scrypt:32768:8:1$conXKhGuMUm6YZcz$93dc360d4d6ad409cbb102ab3abf8186b655fe38dccf707f21bd07f0171b004bf5f40c5dc5bd8af928492768dff0e588eb7b541bb324349fc40164673813ab4d');

-- Categorias da usuária de demonstração
INSERT INTO categoria (id, usuario_id, nome, tipo, cor) VALUES
  (1, 1, 'Salário', 'ENTRADA', '#059669'),
  (2, 1, 'Freelance', 'ENTRADA', '#0D9488'),
  (3, 1, 'Outras receitas', 'ENTRADA', '#65A30D'),
  (4, 1, 'Alimentação', 'SAIDA', '#EA580C'),
  (5, 1, 'Moradia', 'SAIDA', '#7C3AED'),
  (6, 1, 'Transporte', 'SAIDA', '#2563EB'),
  (7, 1, 'Saúde', 'SAIDA', '#DC2626'),
  (8, 1, 'Educação', 'SAIDA', '#0891B2'),
  (9, 1, 'Lazer', 'SAIDA', '#DB2777'),
  (10, 1, 'Compras', 'SAIDA', '#CA8A04'),
  (11, 1, 'Outras despesas', 'SAIDA', '#6B7280');

-- Cartões de crédito
INSERT INTO cartao (id, usuario_id, nome, bandeira, limite_centavos, dia_fechamento, dia_vencimento) VALUES
  (1, 1, 'Nubank', 'MASTERCARD', 300000, 3, 10),
  (2, 1, 'Inter', 'VISA', 150000, 25, 5);

-- Faturas (mes_referencia = mês do vencimento). Faturas já vencidas constam como pagas.
INSERT INTO fatura (id, cartao_id, mes_referencia, data_fechamento, data_vencimento, status, data_pagamento) VALUES
  (1, 1, '2026-07', '2026-07-03', '2026-07-10', 'PAGA', '2026-07-10'),
  (2, 2, '2026-07', '2026-06-25', '2026-07-05', 'PAGA', '2026-07-05'),
  (3, 1, '2026-06', '2026-06-03', '2026-06-10', 'PAGA', '2026-06-10'),
  (4, 1, '2026-08', '2026-08-03', '2026-08-10', 'PAGA', '2026-08-10'),
  (5, 2, '2026-08', '2026-07-25', '2026-08-05', 'PAGA', '2026-08-05'),
  (6, 1, '2026-09', '2026-09-03', '2026-09-10', 'PAGA', '2026-09-10'),
  (7, 2, '2026-09', '2026-08-25', '2026-09-05', 'PAGA', '2026-09-05'),
  (8, 1, '2026-10', '2026-10-03', '2026-10-10', 'PAGA', '2026-10-10'),
  (9, 2, '2026-10', '2026-09-25', '2026-10-05', 'PAGA', '2026-10-05'),
  (10, 1, '2026-11', '2026-11-03', '2026-11-10', 'PAGA', '2026-11-10'),
  (11, 2, '2026-11', '2026-10-25', '2026-11-05', 'PAGA', '2026-11-05'),
  (12, 1, '2026-12', '2026-12-03', '2026-12-10', 'ABERTA', NULL),
  (13, 1, '2027-01', '2027-01-03', '2027-01-10', 'ABERTA', NULL),
  (14, 1, '2027-02', '2027-02-03', '2027-02-10', 'ABERTA', NULL),
  (15, 1, '2027-03', '2027-03-03', '2027-03-10', 'ABERTA', NULL),
  (16, 2, '2026-12', '2026-11-25', '2026-12-05', 'ABERTA', NULL),
  (17, 2, '2027-01', '2026-12-25', '2027-01-05', 'ABERTA', NULL),
  (18, 2, '2027-02', '2027-01-25', '2027-02-05', 'ABERTA', NULL);

-- Lançamentos (valores em centavos)
INSERT INTO lancamento (usuario_id, tipo, descricao, valor_centavos, data, categoria_id, forma_pagamento_id, cartao_id, fatura_id, parcela_numero, parcela_total, grupo_parcelamento, observacao) VALUES
  (1, 'SAIDA', 'Curso online', 7990, '2026-06-02', 8, 4, 1, 3, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 11375, '2026-06-03', 4, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'ENTRADA', 'Salário', 320000, '2026-06-05', 1, 6, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Farmácia', 3435, '2026-06-07', 7, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Passe de ônibus', 12000, '2026-06-08', 6, 2, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Aluguel', 95000, '2026-06-10', 5, 5, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 15125, '2026-06-11', 4, 4, 1, 1, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Conta de luz', 13656, '2026-06-12', 5, 2, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Lanche com amigos', 7222, '2026-06-14', 9, 4, 2, 2, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Internet', 9990, '2026-06-15', 5, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 14348, '2026-06-19', 4, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Cinema', 6677, '2026-06-21', 9, 1, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Consulta médica', 18000, '2026-06-22', 7, 2, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 22047, '2026-06-26', 4, 4, 1, 1, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Curso online', 7990, '2026-07-02', 8, 4, 1, 1, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 12405, '2026-07-03', 4, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'ENTRADA', 'Salário', 320000, '2026-07-05', 1, 6, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Farmácia', 5098, '2026-07-07', 7, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Passe de ônibus', 12000, '2026-07-08', 6, 2, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Aluguel', 95000, '2026-07-10', 5, 5, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 14490, '2026-07-11', 4, 4, 1, 4, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Conta de luz', 9707, '2026-07-12', 5, 2, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Lanche com amigos', 7438, '2026-07-14', 9, 4, 2, 5, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Internet', 9990, '2026-07-15', 5, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'ENTRADA', 'Projeto freelance de site', 60000, '2026-07-18', 2, 2, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 20030, '2026-07-19', 4, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Cinema', 6104, '2026-07-21', 9, 1, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 19419, '2026-07-26', 4, 4, 1, 4, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Curso online', 7990, '2026-08-02', 8, 4, 1, 4, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 15173, '2026-08-03', 4, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'ENTRADA', 'Salário', 320000, '2026-08-05', 1, 6, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Farmácia', 4077, '2026-08-07', 7, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Passe de ônibus', 12000, '2026-08-08', 6, 2, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Aluguel', 95000, '2026-08-10', 5, 5, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 24040, '2026-08-11', 4, 4, 1, 6, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Conta de luz', 12420, '2026-08-12', 5, 2, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Lanche com amigos', 5824, '2026-08-14', 9, 4, 2, 7, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Internet', 9990, '2026-08-15', 5, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'ENTRADA', 'Venda de livro usado', 6000, '2026-08-17', 3, 1, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 22382, '2026-08-19', 4, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Cinema', 4834, '2026-08-21', 9, 1, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 13395, '2026-08-26', 4, 4, 1, 6, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Curso online', 7990, '2026-09-02', 8, 4, 1, 6, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 16699, '2026-09-03', 4, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'ENTRADA', 'Salário', 320000, '2026-09-05', 1, 6, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Farmácia', 3624, '2026-09-07', 7, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Passe de ônibus', 12000, '2026-09-08', 6, 2, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Aluguel', 95000, '2026-09-10', 5, 5, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 16385, '2026-09-11', 4, 4, 1, 8, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Conta de luz', 10164, '2026-09-12', 5, 2, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Notebook para estudos (1/6)', 40000, '2026-09-12', 10, 4, 1, 8, 1, 6, 'G0080', 'Compra parcelada em 6x sem juros'),
  (1, 'SAIDA', 'Lanche com amigos', 3739, '2026-09-14', 9, 4, 2, 9, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Internet', 9990, '2026-09-15', 5, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'ENTRADA', 'Projeto freelance de site', 60000, '2026-09-18', 2, 2, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 16159, '2026-09-19', 4, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Cinema', 5378, '2026-09-21', 9, 1, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Consulta médica', 18000, '2026-09-22', 7, 2, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 14968, '2026-09-26', 4, 4, 1, 8, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Curso online', 7990, '2026-10-02', 8, 4, 1, 8, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 15398, '2026-10-03', 4, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'ENTRADA', 'Salário', 320000, '2026-10-05', 1, 6, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Farmácia', 6306, '2026-10-07', 7, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Passe de ônibus', 12000, '2026-10-08', 6, 2, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Aluguel', 95000, '2026-10-10', 5, 5, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 20430, '2026-10-11', 4, 4, 1, 10, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Conta de luz', 10012, '2026-10-12', 5, 2, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Notebook para estudos (2/6)', 40000, '2026-10-12', 10, 4, 1, 10, 2, 6, 'G0080', 'Compra parcelada em 6x sem juros'),
  (1, 'SAIDA', 'Lanche com amigos', 4558, '2026-10-14', 9, 4, 2, 11, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Internet', 9990, '2026-10-15', 5, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'ENTRADA', 'Projeto freelance de site', 60000, '2026-10-18', 2, 2, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 24282, '2026-10-19', 4, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Cinema', 4209, '2026-10-21', 9, 1, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 16425, '2026-10-26', 4, 4, 1, 10, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Tênis (1/3)', 12998, '2026-10-28', 10, 4, 2, 16, 1, 3, 'G0086', NULL),
  (1, 'SAIDA', 'Curso online', 7990, '2026-11-02', 8, 4, 1, 10, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 25778, '2026-11-03', 4, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'ENTRADA', 'Salário', 320000, '2026-11-05', 1, 6, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Farmácia', 7332, '2026-11-07', 7, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Passe de ônibus', 12000, '2026-11-08', 6, 2, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Aluguel', 95000, '2026-11-10', 5, 5, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Supermercado', 23830, '2026-11-11', 4, 4, 1, 12, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Conta de luz', 14525, '2026-11-12', 5, 2, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Notebook para estudos (3/6)', 40000, '2026-11-12', 10, 4, 1, 12, 3, 6, 'G0080', 'Compra parcelada em 6x sem juros'),
  (1, 'SAIDA', 'Internet', 9990, '2026-11-15', 5, 3, NULL, NULL, 1, 1, NULL, NULL),
  (1, 'SAIDA', 'Tênis (2/3)', 12996, '2026-11-28', 10, 4, 2, 17, 2, 3, 'G0086', NULL),
  (1, 'SAIDA', 'Notebook para estudos (4/6)', 40000, '2026-12-12', 10, 4, 1, 13, 4, 6, 'G0080', 'Compra parcelada em 6x sem juros'),
  (1, 'SAIDA', 'Tênis (3/3)', 12996, '2026-12-28', 10, 4, 2, 18, 3, 3, 'G0086', NULL),
  (1, 'SAIDA', 'Notebook para estudos (5/6)', 40000, '2027-01-12', 10, 4, 1, 14, 5, 6, 'G0080', 'Compra parcelada em 6x sem juros'),
  (1, 'SAIDA', 'Notebook para estudos (6/6)', 40000, '2027-02-12', 10, 4, 1, 15, 6, 6, 'G0080', 'Compra parcelada em 6x sem juros');

COMMIT;
