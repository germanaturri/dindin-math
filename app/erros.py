"""Erros da API e conversão para respostas JSON padronizadas.

Formato de erro: {"erro": "mensagem", "campos": {"campo": "problema"}}
"""
import sqlite3

from flask import jsonify
from werkzeug.exceptions import HTTPException


class ErroApi(Exception):
    def __init__(self, mensagem: str, status: int = 400, campos: dict | None = None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status
        self.campos = campos or {}


class ErroValidacao(ErroApi):
    def __init__(self, campos: dict, mensagem: str = "Dados inválidos"):
        super().__init__(mensagem, 422, campos)


class NaoEncontrado(ErroApi):
    def __init__(self, recurso: str = "Registro"):
        super().__init__(f"{recurso} não encontrado", 404)


def registrar_tratadores_de_erro(app):
    @app.errorhandler(ErroApi)
    def erro_api(e: ErroApi):
        corpo = {"erro": e.mensagem}
        if e.campos:
            corpo["campos"] = e.campos
        return jsonify(corpo), e.status

    @app.errorhandler(sqlite3.IntegrityError)
    def erro_integridade(e):
        msg = str(e)
        if "UNIQUE" in msg:
            return jsonify(erro="Já existe um registro com esses dados"), 409
        if "FOREIGN KEY" in msg:
            return jsonify(erro="Registro em uso por outros dados; não pode ser alterado/excluído"), 409
        return jsonify(erro="Dados violam uma regra do banco", detalhe=msg), 422

    @app.errorhandler(HTTPException)
    def erro_http(e: HTTPException):
        return jsonify(erro=e.description or e.name), e.code
