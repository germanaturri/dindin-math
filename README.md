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

## Como executar

Pré-requisito: [Python 3.10 ou superior](https://www.python.org/downloads/) (no Windows, marque
"Add Python to PATH" na instalação).

```bash
# 1. Entrar na pasta do projeto
cd dindin-math

# 2. (opcional, recomendado) criar um ambiente virtual
python -m venv .venv
# Windows:            .venv\Scripts\activate
# Linux/macOS:        source .venv/bin/activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Iniciar (cria o banco com dados de exemplo na primeira execução)
python run.py
```

Acesse **http://127.0.0.1:5000** e entre com a conta de demonstração:

- **E-mail:** `demo@dindin.com`
- **Senha:** `Demo1234`

Para recriar o banco do zero: `python run.py --reset-db`.

### Testar a API no Postman

Importe `docs/postman/DinDinMath.postman_collection.json`, execute a requisição **Login (demo)**
e depois rode a collection inteira pelo *Collection Runner* (23 requisições com testes).
Documentação completa dos endpoints: [`docs/API.md`](docs/API.md).

## Configuração (parâmetros de conexão)

Veja `.env.example`. Principais variáveis de ambiente:

| Variável | Padrão | Descrição |
|---|---|---|
| `DINDIN_DB` | `instance/dindin.db` | Caminho do arquivo do banco SQLite |
| `DINDIN_SECRET_KEY` | (chave de desenvolvimento) | Chave que assina o cookie de sessão |
| `DINDIN_HOST` | `127.0.0.1` | Use `0.0.0.0` para acessar de outros computadores da rede |
| `DINDIN_PORTA` | `5000` | Porta do servidor |

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
| Entrega 01 - Planejamento | Escopo, tecnologias, diagramas UML e MER, cronograma | `docs/entrega-01/` |
| Entrega 02 - Funcionalidades básicas | Scripts DDL/DML, wireframes, API e telas iniciais | `docs/entrega-02/` |
| Entrega 03 - Funcionalidades complementares | Faturas, parcelamento, recuperação de senha, gráficos, relatórios, simulador, testes | (próxima etapa) |
| Entrega 04 - Entrega final | Prints, documento final, apresentação, produção científica | (próxima etapa) |
