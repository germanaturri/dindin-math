"""Lançamentos de entradas e saídas (UC06, UC07 e UC09)."""
import datetime as dt

from flask import Blueprint, g, jsonify, request

from ..auth import login_obrigatorio
from ..db import get_db, linha_para_dict, linhas_para_lista
from ..erros import ErroApi, ErroValidacao, NaoEncontrado
from ..servicos.faturas import obter_ou_criar_fatura
from ..validacao import (centavos_para_reais, corpo_json, data_iso, dinheiro_em_centavos,
                         inteiro, mes_param, opcao, texto, verificar)

bp = Blueprint("lancamentos", __name__, url_prefix="/api/lancamentos")
TIPOS = ("ENTRADA", "SAIDA")

SQL_BASE = """
SELECT l.id, l.tipo, l.descricao, l.valor_centavos, l.data, l.observacao,
       l.parcela_numero, l.parcela_total, l.grupo_parcelamento,
       l.categoria_id, c.nome AS categoria, c.cor AS categoria_cor,
       l.forma_pagamento_id, fp.codigo AS forma_codigo, fp.nome AS forma_pagamento,
       l.cartao_id, ca.nome AS cartao, l.fatura_id, f.mes_referencia AS fatura_mes
  FROM lancamento l
  JOIN categoria c        ON c.id = l.categoria_id
  JOIN forma_pagamento fp ON fp.id = l.forma_pagamento_id
  LEFT JOIN cartao ca     ON ca.id = l.cartao_id
  LEFT JOIN fatura f      ON f.id = l.fatura_id
 WHERE l.usuario_id = ?"""


def _formatar(l: dict) -> dict:
    l["valor"] = centavos_para_reais(l["valor_centavos"])
    return l


def buscar(lancamento_id) -> dict:
    linha = get_db().execute(SQL_BASE + " AND l.id = ?", (g.usuario["id"], lancamento_id)).fetchone()
    if linha is None:
        raise NaoEncontrado("Lançamento")
    return _formatar(linha_para_dict(linha))


@bp.get("")
@login_obrigatorio
def listar():
    """Extrato com filtros: ?mes=AAAA-MM&tipo=&categoria_id=&forma=&cartao_id=&busca="""
    sql, params = SQL_BASE, [g.usuario["id"]]
    a = request.args
    if a.get("mes") != "todos":
        mes = mes_param(a.get("mes"))
        sql += " AND substr(l.data, 1, 7) = ?"
        params.append(mes)
    if a.get("tipo"):
        if a["tipo"].upper() not in TIPOS:
            raise ErroValidacao({"tipo": "Use ENTRADA ou SAIDA"})
        sql += " AND l.tipo = ?"; params.append(a["tipo"].upper())
    if a.get("categoria_id"):
        sql += " AND l.categoria_id = ?"; params.append(a.get("categoria_id", type=int))
    if a.get("forma"):
        sql += " AND fp.codigo = ?"; params.append(a["forma"].upper())
    if a.get("cartao_id"):
        sql += " AND l.cartao_id = ?"; params.append(a.get("cartao_id", type=int))
    if a.get("busca"):
        sql += " AND l.descricao LIKE ?"; params.append(f"%{a['busca'].strip()}%")
    sql += " ORDER BY l.data DESC, l.id DESC"
    itens = [_formatar(l) for l in linhas_para_lista(get_db().execute(sql, params).fetchall())]
    entradas = sum(l["valor_centavos"] for l in itens if l["tipo"] == "ENTRADA")
    saidas = sum(l["valor_centavos"] for l in itens if l["tipo"] == "SAIDA")
    return jsonify(itens=itens, totais={
        "entradas": centavos_para_reais(entradas),
        "saidas": centavos_para_reais(saidas),
        "saldo": centavos_para_reais(entradas - saidas),
        "quantidade": len(itens),
    })


@bp.get("/<int:lancamento_id>")
@login_obrigatorio
def obter(lancamento_id):
    return jsonify(buscar(lancamento_id))


def _validar(dados: dict) -> dict:
    """Valida o payload e resolve categoria, forma de pagamento e cartão."""
    db, uid = get_db(), g.usuario["id"]
    erros = {}
    v = {
        "tipo": opcao(dados, "tipo", erros, TIPOS),
        "descricao": texto(dados, "descricao", erros, 2, 120),
        "valor_centavos": dinheiro_em_centavos(dados, "valor", erros),
        "data": data_iso(dados, "data", erros),
        "categoria_id": inteiro(dados, "categoria_id", erros, 1),
        "forma_pagamento_id": inteiro(dados, "forma_pagamento_id", erros, 1),
        "observacao": texto(dados, "observacao", erros, 0, 255, obrigatorio=False),
        "cartao": None,
    }
    if v["categoria_id"]:
        cat = db.execute("SELECT tipo FROM categoria WHERE id = ? AND usuario_id = ?",
                         (v["categoria_id"], uid)).fetchone()
        if cat is None:
            erros["categoria_id"] = "Categoria não encontrada"
        elif v["tipo"] and cat["tipo"] != v["tipo"]:
            erros["categoria_id"] = "Categoria não corresponde ao tipo do lançamento"
    forma = None
    if v["forma_pagamento_id"]:
        forma = db.execute("SELECT codigo, exige_cartao FROM forma_pagamento WHERE id = ?",
                           (v["forma_pagamento_id"],)).fetchone()
        if forma is None:
            erros["forma_pagamento_id"] = "Forma de pagamento inválida"
    if forma and forma["exige_cartao"]:
        if v["tipo"] == "ENTRADA":
            erros["forma_pagamento_id"] = "Entradas não podem ser lançadas no cartão de crédito"
        cartao_id = inteiro(dados, "cartao_id", erros, 1)
        if cartao_id:
            cartao = db.execute(
                "SELECT id, dia_fechamento, dia_vencimento, ativo FROM cartao WHERE id = ? AND usuario_id = ?",
                (cartao_id, uid)).fetchone()
            if cartao is None:
                erros["cartao_id"] = "Cartão não encontrado"
            elif not cartao["ativo"]:
                erros["cartao_id"] = "Cartão desativado"
            else:
                v["cartao"] = dict(cartao)
    verificar(erros)
    return v


@bp.post("")
@login_obrigatorio
def criar():
    v = _validar(corpo_json())
    db = get_db()
    cartao_id = fatura_id = None
    if v["cartao"]:
        cartao_id = v["cartao"]["id"]
        fatura_id = obter_ou_criar_fatura(db, v["cartao"], dt.date.fromisoformat(v["data"]))
    cur = db.execute(
        """INSERT INTO lancamento (usuario_id, tipo, descricao, valor_centavos, data, categoria_id,
                                   forma_pagamento_id, cartao_id, fatura_id, observacao)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (g.usuario["id"], v["tipo"], v["descricao"], v["valor_centavos"], v["data"], v["categoria_id"],
         v["forma_pagamento_id"], cartao_id, fatura_id, v["observacao"]))
    db.commit()
    return jsonify(mensagem="Lançamento registrado", lancamentos=[buscar(cur.lastrowid)]), 201


@bp.put("/<int:lancamento_id>")
@login_obrigatorio
def atualizar(lancamento_id):
    atual = buscar(lancamento_id)
    dados = {**{"tipo": atual["tipo"], "descricao": atual["descricao"], "valor": atual["valor"],
                "data": atual["data"], "categoria_id": atual["categoria_id"],
                "forma_pagamento_id": atual["forma_pagamento_id"], "cartao_id": atual["cartao_id"],
                "observacao": atual["observacao"]}, **corpo_json()}
    v = _validar(dados)
    db = get_db()
    cartao_id = fatura_id = None
    if v["cartao"]:
        cartao_id = v["cartao"]["id"]
        fatura_id = obter_ou_criar_fatura(db, v["cartao"], dt.date.fromisoformat(v["data"]))
    db.execute(
        """UPDATE lancamento SET tipo=?, descricao=?, valor_centavos=?, data=?, categoria_id=?,
                  forma_pagamento_id=?, cartao_id=?, fatura_id=?, observacao=?
            WHERE id = ? AND usuario_id = ?""",
        (v["tipo"], v["descricao"], v["valor_centavos"], v["data"], v["categoria_id"],
         v["forma_pagamento_id"], cartao_id, fatura_id, v["observacao"], lancamento_id, g.usuario["id"]))
    db.commit()
    return jsonify(buscar(lancamento_id))


@bp.delete("/<int:lancamento_id>")
@login_obrigatorio
def excluir(lancamento_id):
    buscar(lancamento_id)
    db = get_db()
    db.execute("DELETE FROM lancamento WHERE id = ? AND usuario_id = ?", (lancamento_id, g.usuario["id"]))
    db.commit()
    return jsonify(mensagem="Lançamento excluído")
