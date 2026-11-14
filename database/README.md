# Banco de dados - DinDin Math

| Arquivo | Conteúdo |
|---|---|
| `01_ddl.sql` | DDL: criação das tabelas, restrições (PK, FK, CHECK, UNIQUE), índices e a visão `vw_fatura_total` |
| `02_dml.sql` | DML: carga inicial (formas de pagamento e usuária de demonstração com 6 meses de dados) |
| `03_consultas_exemplo.sql` | DML: consultas e alterações usadas pela aplicação (SELECT, INSERT, UPDATE, DELETE) |

## SGBD e parâmetros de conexão

- **SGBD:** SQLite 3 (embutido no Python, não precisa instalar servidor).
- **Conexão:** o banco é um arquivo. O caminho é definido pela variável de ambiente
  `DINDIN_DB` (padrão: `instance/dindin.db`). Veja `.env.example`.
- **Conexão remota:** o SQLite **não** aceita conexões remotas diretas (não há porta de rede).
  O acesso remoto aos dados é feito pela **API REST** do sistema: iniciando o servidor com
  `DINDIN_HOST=0.0.0.0`, outros computadores da rede acessam `http://IP-DO-SERVIDOR:5000/api/...`.
- Chaves estrangeiras são ativadas em cada conexão com `PRAGMA foreign_keys = ON`.

## Como criar o banco manualmente

```bash
# opção 1: pela aplicação (recria com dados de exemplo)
python run.py --reset-db
# opção 2: pelo comando do Flask
flask --app run init-db
# opção 3: com o cliente sqlite3 (se instalado) ou DB Browser for SQLite
sqlite3 instance/dindin.db < database/01_ddl.sql
sqlite3 instance/dindin.db < database/02_dml.sql
```

## Decisões de modelagem

- **Valores em centavos (INTEGER):** evita erros de arredondamento de números de ponto flutuante.
- **Fatura como entidade própria:** permite saber em qual fatura cada compra cai, o status
  (aberta, fechada, paga) e o total por fatura.
- **Parcelamento:** uma compra em N vezes gera N lançamentos ligados pelo mesmo `grupo_parcelamento`,
  cada um com a data do seu mês e apontando para a fatura onde cai.
- **Categoria por usuário:** cada pessoa personaliza suas categorias; a exclusão é bloqueada
  (`ON DELETE RESTRICT`) se houver lançamentos.
