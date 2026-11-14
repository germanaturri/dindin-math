"""Formas de pagamento (tabela de domínio, somente leitura)."""
from flask import Blueprint, jsonify

from ..auth import login_obrigatorio
from ..db import get_db, linhas_para_lista

bp = Blueprint("formas_pagamento", __name__, url_prefix="/api/formas-pagamento")


@bp.get("")
@login_obrigatorio
def listar():
    linhas = get_db().execute(
        "SELECT id, codigo, nome, exige_cartao FROM forma_pagamento ORDER BY id"
    ).fetchall()
    formas = linhas_para_lista(linhas)
    for f in formas:
        f["exige_cartao"] = bool(f["exige_cartao"])
    return jsonify(formas)
