"""DinDin Math - fábrica da aplicação Flask.

A aplicação expõe uma API REST em /api/* (JSON) e serve o front-end
estático (HTML, CSS e JavaScript) da pasta app/static.
"""
import os

from flask import Flask, jsonify, redirect, send_from_directory

from . import db
from .erros import registrar_tratadores_de_erro


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__, static_folder="static", static_url_path="/static")

    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app.config.update(
        # Parâmetros de conexão/configuração (podem vir de variáveis de ambiente)
        DATABASE=os.environ.get("DINDIN_DB", os.path.join(raiz, "instance", "dindin.db")),
        SECRET_KEY=os.environ.get("DINDIN_SECRET_KEY", "troque-esta-chave-em-producao"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        JSON_SORT_KEYS=False,
        SCRIPTS_SQL=os.path.join(raiz, "database"),
    )
    if config:
        app.config.update(config)

    db.init_app(app)
    registrar_tratadores_de_erro(app)

    from .auth import bp as auth_bp
    from .api.categorias import bp as categorias_bp
    from .api.formas_pagamento import bp as formas_bp
    from .api.cartoes import bp as cartoes_bp
    from .api.lancamentos import bp as lancamentos_bp

    for bp in (auth_bp, categorias_bp, formas_bp, cartoes_bp, lancamentos_bp):
        app.register_blueprint(bp)

    @app.get("/api/saude")
    def saude():
        return jsonify(status="ok", aplicacao="DinDin Math")

    # ---------- Front-end ----------
    paginas = os.path.join(app.static_folder, "paginas")

    @app.get("/")
    def inicio():
        return redirect("/app/lancamentos")

    @app.get("/app/<pagina>")
    def pagina(pagina):
        return send_from_directory(paginas, f"{pagina}.html")

    return app
