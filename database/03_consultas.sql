-- =====================================================================
-- DinDin Math - Consultas e exemplos de manipulação (DML) - PostgreSQL
-- São as mesmas regras usadas pela API, escritas em SQL puro para
-- conferência no pgAdmin / psql.
-- =====================================================================

-- 1) Extrato de novembro/2026 da usuária 1, com categoria e forma de pagamento
SELECT l.data, l.tipo, l.descricao, c.nome AS categoria, f.nome AS forma_pagamento,
       l.valor, l.parcela_atual || '/' || l.total_parcelas AS parcela
FROM   lancamento l
JOIN   categoria c       ON c.id = l.categoria_id
JOIN   forma_pagamento f ON f.id = l.forma_pagamento_id
WHERE  l.usuario_id = 1
  AND  l.data >= '2026-11-01' AND l.data < '2026-12-01'
ORDER BY l.data;

-- 2) Resumo do mês: receitas, despesas e saldo
SELECT SUM(CASE WHEN tipo = 'RECEITA' THEN valor ELSE 0 END) AS receitas,
       SUM(CASE WHEN tipo = 'DESPESA' THEN valor ELSE 0 END) AS despesas,
       SUM(CASE WHEN tipo = 'RECEITA' THEN valor ELSE -valor END) AS saldo
FROM   lancamento
WHERE  usuario_id = 1 AND data >= '2026-11-01' AND data < '2026-12-01';

-- 3) Despesas por categoria no mês (base do gráfico de rosca)
SELECT c.nome, c.cor, SUM(l.valor) AS total
FROM   lancamento l JOIN categoria c ON c.id = l.categoria_id
WHERE  l.usuario_id = 1 AND l.tipo = 'DESPESA'
  AND  l.data >= '2026-11-01' AND l.data < '2026-12-01'
GROUP BY c.nome, c.cor
ORDER BY total DESC;

-- 4) Despesas por forma de pagamento (separa o que é cartão de crédito)
SELECT f.nome, SUM(l.valor) AS total
FROM   lancamento l JOIN forma_pagamento f ON f.id = l.forma_pagamento_id
WHERE  l.usuario_id = 1 AND l.tipo = 'DESPESA'
  AND  l.data >= '2026-11-01' AND l.data < '2026-12-01'
GROUP BY f.nome
ORDER BY total DESC;

-- 5) Faturas do cartão com o total de cada uma
SELECT ft.id, ft.mes_referencia, ft.data_vencimento, ft.status,
       COALESCE(SUM(l.valor), 0) AS total
FROM   fatura ft LEFT JOIN lancamento l ON l.fatura_id = ft.id
WHERE  ft.cartao_id = 1
GROUP BY ft.id
ORDER BY ft.mes_referencia;

-- 6) Evolução mensal (view criada no DDL)
SELECT * FROM vw_resumo_mensal WHERE usuario_id = 1 ORDER BY mes;

-- 7) Limite disponível do cartão (limite - faturas não pagas)
SELECT cc.nome, cc.limite,
       cc.limite - COALESCE(SUM(l.valor), 0) AS limite_disponivel
FROM   cartao_credito cc
LEFT JOIN fatura ft    ON ft.cartao_id = cc.id AND ft.status <> 'PAGA'
LEFT JOIN lancamento l ON l.fatura_id = ft.id
WHERE  cc.id = 1
GROUP BY cc.id;

-- ---------------------------------------------------------------------
-- Exemplos de UPDATE e DELETE (executar dentro de transação para testar)
-- ---------------------------------------------------------------------
BEGIN;
-- corrigir o valor de um lançamento
UPDATE lancamento SET valor = 60.00 WHERE descricao = 'Feira' AND usuario_id = 1;
-- pagar a fatura de dezembro
UPDATE fatura SET status = 'PAGA', data_pagamento = '2026-12-09' WHERE id = 4;
-- excluir um lançamento
DELETE FROM lancamento WHERE descricao = 'Internet' AND usuario_id = 1;
ROLLBACK;  -- desfaz os testes acima (troque por COMMIT para gravar)
