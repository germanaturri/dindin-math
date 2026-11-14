"""CRUD de categorias do usuário logado (UC04 - Manter categorias)."""
from flask import Blueprint, g, jsonify, request

from ..auth import login_obrigatorio
from ..db import get_db, linha_para_dict, linhas_para_lista
from ..erros import ErroApi, NaoEncontrado
from ..validacao import corpo_json, cor, opcao, texto, verificar

bp = Blueprint("categorias", __name__, url_prefix="/api/categorias")
TIPOS = ("ENTRADA", "SAIDA")


def buscar(categoria_id):
    linha = get_db().execute(
        "SELECT id, nome, tipo, cor FROM categoria WHERE id = ? AND usuario_id = ?",
        (categoria_id, g.usuario["id"]),
    ).fetchone()
    if linha is None:
        raise NaoEncontrado("Categoria")
    return linha_para_dict(linha)


@bp.get("")
@login_obrigatorio
def listar():
    sql = """SELECT c.id, c.nome, c.tipo, c.cor,
                    (SELECT COUNT(*) FROM lancamento l WHERE l.categoria_id = c.id) AS qtd_lancamentos
               FROM categoria c WHERE c.usuario_id = ?"""
    params = [g.usuario["id"]]
    tipo = request.args.get("tipo")
    if tipo:
        if tipo.upper() not in TIPOS:
            raise ErroApi("tipo deve ser ENTRADA ou SAIDA", 422)
        sql += " AND c.tipo = ?"
        params.append(tipo.upper())
    sql += " ORDER BY c.tipo, c.nome"
    return jsonify(linhas_para_lista(get_db().execute(sql, params).fetchall()))


@bp.get("/<int:categoria_id>")
@login_obrigatorio
def obter(categoria_id):
    return jsonify(buscar(categoria_id))


def _validar(dados, parcial_de=None):
    erros = {}
    base = parcial_de or {}
    nome = texto(dados, "nome", erros, 2, 40) if ("nome" in dados or not parcial_de) else base["nome"]
    tipo = opcao(dados, "tipo", erros, TIPOS) if ("tipo" in dados or not parcial_de) else base["tipo"]
    cor_ = cor(dados, "cor", erros, base.get("cor", "#6B7280"))
    verificar(erros)
    return nome, tipo, cor_


@bp.post("")
@login_obrigatorio
def criar():
    nome, tipo, cor_ = _validar(corpo_json())
    db = get_db()
    cur = db.execute(
        "INSERT INTO categoria (usuario_id, nome, tipo, cor) VALUES (?, ?, ?, ?)",
        (g.usuario["id"], nome, tipo, cor_),
    )
    db.commit()
    return jsonify(buscar(cur.lastrowid)), 201


@bp.put("/<int:categoria_id>")
@login_obrigatorio
def atualizar(categoria_id):
    atual = buscar(categoria_id)
    nome, tipo, cor_ = _validar(corpo_json(), parcial_de=atual)
    db = get_db()
    if tipo != atual["tipo"] and db.execute(
        "SELECT 1 FROM lancamento WHERE categoria_id = ?", (categoria_id,)
    ).fetchone():
        raise ErroApi("Não é possível mudar o tipo de uma categoria que já tem lançamentos", 409)
    db.execute("UPDATE categoria SET nome = ?, tipo = ?, cor = ? WHERE id = ?",
               (nome, tipo, cor_, categoria_id))
    db.commit()
    return jsonify(buscar(categoria_id))


@bp.delete("/<int:categoria_id>")
@login_obrigatorio
def excluir(categoria_id):
    buscar(categoria_id)
    db = get_db()
    if db.execute("SELECT 1 FROM lancamento WHERE categoria_id = ?", (categoria_id,)).fetchone():
        raise ErroApi("Categoria possui lançamentos; mova-os antes de excluir", 409)
    db.execute("DELETE FROM categoria WHERE id = ?", (categoria_id,))
    db.commit()
    return jsonify(mensagem="Categoria excluída")
