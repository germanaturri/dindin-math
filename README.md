# DinDin Math 💰

Sistema web de **gestão de finanças pessoais** desenvolvido no Projeto Integrador


## 1. Escopo

**Problema.** Quem usa várias formas de pagamento (dinheiro, PIX, débito, boleto e cartão de crédito)
não consegue acompanhar de forma simples quanto entra, quanto sai, em que categorias gasta e quanto
das próximas faturas do cartão já está comprometido com compras parceladas.

**Objetivo geral.** Desenvolver um sistema web que permita registrar entradas e saídas, classificar
os gastos por categoria e forma de pagamento, controlar as faturas dos cartões (inclusive compras
parceladas) e apresentar gráficos comparativos e demonstrativos mensais.

**Objetivos específicos**
- Cadastro, login e recuperação de senha por e-mail, com segurança
- Banco de dados relacional para usuários, categorias, formas de pagamento, cartões, faturas e lançamentos
- Associação automática de cada compra no crédito à fatura correta, com parcelas distribuídas pelas faturas seguintes
- API REST documentada e testada no Postman
- Dashboard com gráficos, demonstrativo mensal em CSV e simulador de compra parcelada (Tabela Price)
- Testes automatizados

**Delimitação (o que não será atendido).** Integração automática com bancos ou importação de extratos;
pagamentos ou emissão de boletos; finanças empresariais; investimentos; contas compartilhadas;
aplicativo mobile nativo (a interface web é responsiva); hospedagem em nuvem como requisito.

## 2. Plataforma e tecnologias

| Item | Escolha | Justificativa |
|---|---|---|
| Plataforma | **Web responsiva** | Funciona no computador e no celular, sem instalação |
| Back-end | **Python 3.10+ e Flask 3** (API REST em JSON) | Simples, didático e adequado para APIs |
| Banco de dados | **SQLite 3** | Não exige servidor; atende ao volume de um usuário; SQL padrão |
| Front-end | **HTML5, CSS3 e JavaScript** (Fetch API), gráficos em SVG | Leve, sem dependências externas |
| Testes | **pytest** e **Postman** | Testes automatizados e testes da API |
| Ferramentas | Git/GitHub, VS Code, Mermaid/Graphviz, Excel | Versionamento, diagramas e cronograma |

## 3. Requisitos

**Funcionais:** RF01 cadastrar usuário · RF02 login e logout · RF03 manter categorias · RF04 manter
cartões · RF05 registrar entradas · RF06 registrar saídas com forma de pagamento · RF07 associar a
compra no crédito à fatura · RF08 parcelar compras · RF09 extrato com filtros · RF10 consultar e pagar
faturas · RF11 dashboard com gráficos · RF12 demonstrativo em CSV · RF13 simulador de parcelamento ·
RF14 recuperar a senha por e-mail.

**Não funcionais:** web responsiva; Python/Flask; SQLite; HTML/CSS/JS; senhas com hash, sessão segura
e isolamento de dados por usuário; valores em centavos (sem erros de arredondamento); validação com
mensagens por campo; testes automatizados; versionamento no GitHub; execução em Windows, Linux e macOS.
