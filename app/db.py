"""Conexão com o banco SQLite.

Cada requisição abre uma conexão (guardada em flask.g) e ela é fechada
automaticamente ao fim da requisição.
"""
import os
import sqlite3

import click
from flask import current_app, g


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = conectar(current_app.config["DATABASE"])
    return g.db


def conectar(caminho: str) -> sqlite3.Connection:
    conexao = sqlite3.connect(caminho, detect_types=sqlite3.PARSE_DECLTYPES)
    conexao.row_factory = sqlite3.Row          # linhas acessíveis por nome da coluna
    conexao.execute("PRAGMA foreign_keys = ON")  # o SQLite exige ativar as FKs por conexão
    return conexao


def fechar_db(_erro=None):
    conexao = g.pop("db", None)
    if conexao is not None:
        conexao.close()


def executar_script(conexao: sqlite3.Connection, arquivo: str):
    with open(arquivo, encoding="utf-8") as f:
        conexao.executescript(f.read())


def criar_banco(com_dados_exemplo: bool = True):
    """Executa o DDL (estrutura) e, opcionalmente, o DML (dados de exemplo)."""
    caminho = current_app.config["DATABASE"]
    if caminho != ":memory:":
        os.makedirs(os.path.dirname(caminho), exist_ok=True)
    conexao = conectar(caminho)
    pasta = current_app.config["SCRIPTS_SQL"]
    executar_script(conexao, os.path.join(pasta, "01_ddl.sql"))
    if com_dados_exemplo:
        executar_script(conexao, os.path.join(pasta, "02_dml.sql"))
    conexao.commit()
    conexao.close()


def linha_para_dict(linha):
    return dict(linha) if linha is not None else None


def linhas_para_lista(linhas):
    return [dict(l) for l in linhas]


@click.command("init-db")
@click.option("--sem-exemplos", is_flag=True, help="Cria só a estrutura, sem dados de exemplo.")
def init_db_comando(sem_exemplos):
    """Apaga e recria o banco de dados."""
    criar_banco(com_dados_exemplo=not sem_exemplos)
    click.echo(f"Banco criado em {current_app.config['DATABASE']}")


def init_app(app):
    app.teardown_appcontext(fechar_db)
    app.cli.add_command(init_db_comando)
