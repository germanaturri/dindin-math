"""CRUD de cartões de crédito (UC05 - Manter cartões de crédito)."""
from flask import Blueprint, g, jsonify

from ..auth import login_obrigatorio
from ..db import get_db, linha_para_dict, linhas_para_lista
from ..erros import ErroApi, NaoEncontrado
from ..validacao import (centavos_para_reais, corpo_json, dinheiro_em_centavos, inteiro,
                         opcao, texto, verificar)

bp = Blueprint("cartoes", __name__, url_prefix="/api/cartoes")
BANDEIRAS = ("VISA", "MASTERCARD", "ELO", "AMEX", "HIPERCARD", "OUTRA")

SQL_CARTAO = """
SELECT c.id, c.nome, c.bandeira, c.limite_centavos, c.dia_fechamento, c.dia_vencimento, c.ativo,
       COALESCE((SELECT SUM(l.valor_centavos)
                   FROM lancamento l JOIN fatura f ON f.id = l.fatura_id
                  WHERE l.cartao_id = c.id AND f.status <> 'PAGA'), 0) AS usado_centavos
  FROM cartao c
 WHERE c.usuario_id = ?"""


def _formatar(c: dict) -> dict:
    c["ativo"] = bool(c["ativo"])
    c["limite"] = centavos_para_reais(c["limite_centavos"])
    c["usado"] = centavos_para_reais(c["usado_centavos"])
    c["disponivel"] = centavos_para_reais(c["limite_centavos"] - c["usado_centavos"])
    return c


def buscar(cartao_id) -> dict:
    linha = get_db().execute(SQL_CARTAO + " AND c.id = ?", (g.usuario["id"], cartao_id)).fetchone()
    if linha is None:
        raise NaoEncontrado("Cartão")
    return _formatar(linha_para_dict(linha))


@bp.get("")
@login_obrigatorio
def listar():
    linhas = get_db().execute(SQL_CARTAO + " ORDER BY c.ativo DESC, c.nome", (g.usuario["id"],)).fetchall()
    return jsonify([_formatar(c) for c in linhas_para_lista(linhas)])


@bp.get("/<int:cartao_id>")
@login_obrigatorio
def obter(cartao_id):
    return jsonify(buscar(cartao_id))


def _validar(dados, atual=None):
    atual = atual or {}
    erros = {}
    def pega(campo, func):
        return func() if (campo in dados or not atual) else atual[campo]
    nome = pega("nome", lambda: texto(dados, "nome", erros, 2, 40))
    bandeira = pega("bandeira", lambda: opcao(dados, "bandeira", erros, BANDEIRAS, padrao="OUTRA"))
    limite = (dinheiro_em_centavos(dados, "limite", erros, permitir_zero=True)
              if ("limite" in dados or not atual) else atual["limite_centavos"])
    fech = pega("dia_fechamento", lambda: inteiro(dados, "dia_fechamento", erros, 1, 28))
    venc = pega("dia_vencimento", lambda: inteiro(dados, "dia_vencimento", erros, 1, 28))
    ativo = bool(dados.get("ativo", atual.get("ativo", True)))
    if fech is not None and fech == venc:
        erros["dia_vencimento"] = "Vencimento deve ser diferente do fechamento"
    verificar(erros)
    return nome, bandeira, limite, fech, venc, int(ativo)


@bp.post("")
@login_obrigatorio
def criar():
    nome, bandeira, limite, fech, venc, ativo = _validar(corpo_json())
    db = get_db()
    cur = db.execute(
        """INSERT INTO cartao (usuario_id, nome, bandeira, limite_centavos, dia_fechamento, dia_vencimento, ativo)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (g.usuario["id"], nome, bandeira, limite, fech, venc, ativo))
    db.commit()
    return jsonify(buscar(cur.lastrowid)), 201


@bp.put("/<int:cartao_id>")
@login_obrigatorio
def atualizar(cartao_id):
    atual = buscar(cartao_id)
    nome, bandeira, limite, fech, venc, ativo = _validar(corpo_json(), atual)
    db = get_db()
    tem_compras = db.execute("SELECT 1 FROM lancamento WHERE cartao_id = ?", (cartao_id,)).fetchone()
    if tem_compras and (fech != atual["dia_fechamento"] or venc != atual["dia_vencimento"]):
        raise ErroApi("Não é possível alterar fechamento/vencimento de um cartão com compras", 409)
    db.execute(
        """UPDATE cartao SET nome=?, bandeira=?, limite_centavos=?, dia_fechamento=?, dia_vencimento=?, ativo=?
            WHERE id = ?""", (nome, bandeira, limite, fech, venc, ativo, cartao_id))
    db.commit()
    return jsonify(buscar(cartao_id))


@bp.delete("/<int:cartao_id>")
@login_obrigatorio
def excluir(cartao_id):
    buscar(cartao_id)
    db = get_db()
    if db.execute("SELECT 1 FROM lancamento WHERE cartao_id = ?", (cartao_id,)).fetchone():
        raise ErroApi("Cartão possui compras; desative-o em vez de excluir", 409)
    db.execute("DELETE FROM cartao WHERE id = ?", (cartao_id,))
    db.commit()
    return jsonify(mensagem="Cartão excluído")
