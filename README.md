# DinDin Math 💰

Sistema web de **gestão de finanças pessoais** desenvolvido por **Germana Turri** no Projeto Integrador
(Desenvolvimento de Sistemas) da UCEFF – Unidade Central de Educação FAEM Faculdade, polo Frederico Westphalen (RS). Permite lançar entradas e saídas, classificar gastos em categorias,
separar o que é fatura do cartão de crédito (inclusive compras parceladas), registrar a forma de
pagamento e visualizar gráficos comparativos e demonstrativos mensais.

## Funcionalidades

- Cadastro, login e logout com senha protegida por hash
- Categorias personalizáveis (entradas e saídas, com cor)
- Lançamentos com forma de pagamento (dinheiro, PIX, débito, crédito, boleto, transferência)
- Cartões de crédito com limite, dia de fechamento e de vencimento
- Compras no crédito associadas automaticamente à fatura do mês

> Recuperação de senha, faturas detalhadas, parcelamento, dashboard, relatórios e simulador estão planejados para a Entrega 03.
- Extrato com filtros (mês, tipo, categoria, forma de pagamento, busca)

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Plataforma | Web (responsiva) |
| Back-end | Python 3.10+ e Flask 3 (API REST em JSON) |
| Banco de dados | SQLite 3 (scripts DDL/DML em `database/`) |
| Front-end | HTML5, CSS3 e JavaScript puro (Fetch API); gráficos em SVG, sem bibliotecas externas |
| Testes | collection do Postman |
| Versionamento | Git e GitHub |


## Estrutura do projeto

```
dindin-math/
├── app/
│   ├── __init__.py          # fábrica da aplicação e rotas das páginas
│   ├── db.py                # conexão com o SQLite e criação do banco
│   ├── auth.py              # cadastro, login, logout e decorador login_obrigatorio
│   ├── validacao.py         # validação e conversão do payload (dinheiro, datas...)
│   ├── erros.py             # erros padronizados em JSON
│   ├── api/                 # endpoints REST (categorias, formas de pagamento, cartões, lançamentos)
│   ├── servicos/faturas.py  # regras do cartão: fatura de cada compra, divisão de parcelas
│   └── static/              # front-end: paginas/*.html, css/, js/
├── database/                # 01_ddl.sql, 02_dml.sql, 03_consultas_exemplo.sql
├── docs/                    # documentação, diagramas e entregas de cada etapa
│   ├── API.md
│   ├── postman/
│   ├── entrega-01/ … entrega-04/
├── run.py                   # ponto de entrada
└── requirements.txt
```

## Entregas do Projeto Integrador

| Etapa | Conteúdo | Pasta |
|---|---|---|
| Entrega 01 - Planejamento | Escopo, tecnologias, diagramas UML e MER, cronograma |
| Entrega 02 - Funcionalidades básicas | Scripts DDL/DML, wireframes, API e telas iniciais |
| Entrega 03 - Funcionalidades complementares | Faturas, parcelamento, recuperação de senha, gráficos, relatórios, simulador, testes |
| Entrega 04 - Entrega final | Prints, documento final, apresentação, produção científica |
