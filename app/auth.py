"""Autenticação: cadastro, login, logout e verificação de sessão.

As senhas nunca são guardadas em texto puro: usamos generate_password_hash
(Werkzeug), que aplica um algoritmo de hash lento com "sal" aleatório.
"""
import functools

from flask import Blueprint, g, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db
from .erros import ErroApi
from .validacao import corpo_json, email, texto, verificar

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

CATEGORIAS_PADRAO = [
    ("Salário", "ENTRADA", "#059669"), ("Freelance", "ENTRADA", "#0D9488"),
    ("Outras receitas", "ENTRADA", "#65A30D"),
    ("Alimentação", "SAIDA", "#EA580C"), ("Moradia", "SAIDA", "#7C3AED"),
    ("Transporte", "SAIDA", "#2563EB"), ("Saúde", "SAIDA", "#DC2626"),
    ("Educação", "SAIDA", "#0891B2"), ("Lazer", "SAIDA", "#DB2777"),
    ("Compras", "SAIDA", "#CA8A04"), ("Outras despesas", "SAIDA", "#6B7280"),
]


def login_obrigatorio(view):
    """Decorador: bloqueia a rota se não houver usuário na sessão (HTTP 401)."""
    @functools.wraps(view)
    def envoltorio(*args, **kwargs):
        usuario_id = session.get("usuario_id")
        if usuario_id is None:
            raise ErroApi("Faça login para continuar", 401)
        usuario = get_db().execute(
            "SELECT id, nome, email FROM usuario WHERE id = ?", (usuario_id,)
        ).fetchone()
        if usuario is None:
            session.clear()
            raise ErroApi("Sessão expirada", 401)
        g.usuario = dict(usuario)
        return view(*args, **kwargs)
    return envoltorio


@bp.post("/registrar")
def registrar():
    dados = corpo_json()
    erros = {}
    nome = texto(dados, "nome", erros, 2, 80)
    mail = email(dados, "email", erros)
    senha = dados.get("senha") or ""
    if not isinstance(senha, str) or len(senha) < 8:
        erros["senha"] = "A senha deve ter pelo menos 8 caracteres"
    elif senha.isdigit() or senha.isalpha():
        erros["senha"] = "Use letras e números na senha"
    verificar(erros)

    db = get_db()
    if db.execute("SELECT 1 FROM usuario WHERE email = ?", (mail,)).fetchone():
        raise ErroApi("E-mail já cadastrado", 409, {"email": "E-mail já cadastrado"})
    cur = db.execute(
        "INSERT INTO usuario (nome, email, senha_hash) VALUES (?, ?, ?)",
        (nome, mail, generate_password_hash(senha)),
    )
    usuario_id = cur.lastrowid
    # todo usuário novo já começa com categorias sugeridas
    db.executemany(
        "INSERT INTO categoria (usuario_id, nome, tipo, cor) VALUES (?, ?, ?, ?)",
        [(usuario_id, n, t, c) for n, t, c in CATEGORIAS_PADRAO],
    )
    db.commit()
    session.clear()
    session["usuario_id"] = usuario_id
    return jsonify(mensagem="Conta criada com sucesso",
                   usuario={"id": usuario_id, "nome": nome, "email": mail}), 201


@bp.post("/login")
def login():
    dados = corpo_json()
    mail = str(dados.get("email") or "").strip().lower()
    senha = str(dados.get("senha") or "")
    usuario = get_db().execute(
        "SELECT id, nome, email, senha_hash FROM usuario WHERE email = ?", (mail,)
    ).fetchone()
    # mesma mensagem para e-mail inexistente e senha errada (não revela quais e-mails existem)
    if usuario is None or not check_password_hash(usuario["senha_hash"], senha):
        raise ErroApi("E-mail ou senha inválidos", 401)
    session.clear()
    session["usuario_id"] = usuario["id"]
    return jsonify(mensagem="Login realizado",
                   usuario={"id": usuario["id"], "nome": usuario["nome"], "email": usuario["email"]})


@bp.post("/logout")
def logout():
    session.clear()
    return jsonify(mensagem="Sessão encerrada")


@bp.get("/me")
@login_obrigatorio
def me():
    return jsonify(usuario=g.usuario)
