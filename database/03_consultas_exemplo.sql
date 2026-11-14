-- =====================================================================
-- DinDin Math - Exemplos de DML usados pela aplicação (consultas/alterações)
-- Execute após 01_ddl.sql e 02_dml.sql. Valores em centavos.
-- =====================================================================

-- 1) Extrato de novembro/2026 da usuária 1
SELECT l.data, l.tipo, l.descricao, l.valor_centavos / 100.0 AS valor, c.nome AS categoria, fp.nome AS forma
  FROM lancamento l
  JOIN categoria c        ON c.id = l.categoria_id
  JOIN forma_pagamento fp ON fp.id = l.forma_pagamento_id
 WHERE l.usuario_id = 1 AND substr(l.data, 1, 7) = '2026-11'
 ORDER BY l.data;

-- 2) Resumo do mês: entradas, saídas e saldo
SELECT SUM(CASE WHEN tipo = 'ENTRADA' THEN valor_centavos ELSE 0 END) / 100.0 AS entradas,
       SUM(CASE WHEN tipo = 'SAIDA'   THEN valor_centavos ELSE 0 END) / 100.0 AS saidas,
       SUM(CASE WHEN tipo = 'ENTRADA' THEN valor_centavos ELSE -valor_centavos END) / 100.0 AS saldo
  FROM lancamento
 WHERE usuario_id = 1 AND substr(data, 1, 7) = '2026-11';

-- 3) Gastos por categoria no mês (base do gráfico de pizza)
SELECT c.nome, c.cor, SUM(l.valor_centavos) / 100.0 AS total
  FROM lancamento l JOIN categoria c ON c.id = l.categoria_id
 WHERE l.usuario_id = 1 AND l.tipo = 'SAIDA' AND substr(l.data, 1, 7) = '2026-11'
 GROUP BY c.id ORDER BY total DESC;

-- 4) Gastos por forma de pagamento no mês
SELECT fp.nome, SUM(l.valor_centavos) / 100.0 AS total
  FROM lancamento l JOIN forma_pagamento fp ON fp.id = l.forma_pagamento_id
 WHERE l.usuario_id = 1 AND l.tipo = 'SAIDA' AND substr(l.data, 1, 7) = '2026-11'
 GROUP BY fp.id ORDER BY total DESC;

-- 5) Total de cada fatura do cartão Nubank (visão vw_fatura_total)
SELECT mes_referencia, data_vencimento, status, total_centavos / 100.0 AS total
  FROM vw_fatura_total WHERE cartao_id = 1 ORDER BY mes_referencia;

-- 6) Evolução mensal (últimos meses) - base do gráfico de barras
SELECT substr(data, 1, 7) AS mes,
       SUM(CASE WHEN tipo = 'ENTRADA' THEN valor_centavos ELSE 0 END) / 100.0 AS entradas,
       SUM(CASE WHEN tipo = 'SAIDA'   THEN valor_centavos ELSE 0 END) / 100.0 AS saidas
  FROM lancamento WHERE usuario_id = 1
 GROUP BY mes ORDER BY mes;

-- 7) Inserir uma nova despesa no PIX
INSERT INTO lancamento (usuario_id, tipo, descricao, valor_centavos, data, categoria_id, forma_pagamento_id)
VALUES (1, 'SAIDA', 'Padaria', 1850, '2026-11-12', 4, 2);

-- 8) Corrigir o valor de um lançamento
UPDATE lancamento SET valor_centavos = 1990 WHERE descricao = 'Padaria' AND usuario_id = 1;

-- 9) Marcar a fatura de dezembro do Nubank como paga
UPDATE fatura SET status = 'PAGA', data_pagamento = '2026-12-10'
 WHERE cartao_id = 1 AND mes_referencia = '2026-12';

-- 10) Excluir o lançamento de teste
DELETE FROM lancamento WHERE descricao = 'Padaria' AND usuario_id = 1;
