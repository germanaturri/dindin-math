"""Funções de validação e conversão do payload recebido pela API.

Cada função recebe o dicionário de erros e o preenche quando encontra um
problema, assim a API devolve TODOS os erros de uma vez (melhor usabilidade).
"""
import datetime as dt
import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from flask import request

from .erros import ErroApi, ErroValidacao

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
COR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
MES_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def corpo_json() -> dict:
    """Lê o corpo JSON da requisição (exige Content-Type application/json)."""
    if not request.is_json:
        raise ErroApi("Envie os dados em JSON (Content-Type: application/json)", 415)
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise ErroApi("JSON inválido", 400)
    return dados


def texto(dados, campo, erros, minimo=1, maximo=255, obrigatorio=True):
    valor = dados.get(campo)
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        if obrigatorio:
            erros[campo] = "Campo obrigatório"
        return None
    if not isinstance(valor, str):
        erros[campo] = "Deve ser um texto"
        return None
    valor = valor.strip()
    if not (minimo <= len(valor) <= maximo):
        erros[campo] = f"Deve ter entre {minimo} e {maximo} caracteres"
        return None
    return valor


def email(dados, campo, erros):
    valor = texto(dados, campo, erros, 5, 120)
    if valor and not EMAIL_RE.match(valor):
        erros[campo] = "E-mail inválido"
        return None
    return valor.lower() if valor else None


def opcao(dados, campo, erros, opcoes, obrigatorio=True, padrao=None):
    valor = dados.get(campo, padrao)
    if valor is None:
        if obrigatorio:
            erros[campo] = "Campo obrigatório"
        return None
    if isinstance(valor, str):
        valor = valor.strip().upper()
    if valor not in opcoes:
        erros[campo] = f"Valor deve ser um de: {', '.join(opcoes)}"
        return None
    return valor


def inteiro(dados, campo, erros, minimo=None, maximo=None, obrigatorio=True, padrao=None):
    valor = dados.get(campo, padrao)
    if valor is None or valor == "":
        if obrigatorio:
            erros[campo] = "Campo obrigatório"
        return None
    try:
        if isinstance(valor, bool):
            raise ValueError
        valor = int(valor)
    except (TypeError, ValueError):
        erros[campo] = "Deve ser um número inteiro"
        return None
    if (minimo is not None and valor < minimo) or (maximo is not None and valor > maximo):
        erros[campo] = f"Deve estar entre {minimo} e {maximo}"
        return None
    return valor


def dinheiro_em_centavos(dados, campo, erros, permitir_zero=False, obrigatorio=True):
    """Converte '1.234,56', '1234.56' ou 1234.56 em centavos (int) usando Decimal.

    Decimal evita o erro clássico de ponto flutuante: 0.1 + 0.2 != 0.3.
    """
    valor = dados.get(campo)
    if valor is None or valor == "":
        if obrigatorio:
            erros[campo] = "Campo obrigatório"
        return None
    try:
        if isinstance(valor, bool):
            raise InvalidOperation
        if isinstance(valor, str):
            s = valor.strip().replace("R$", "").replace(" ", "")
            if "," in s:                      # formato brasileiro 1.234,56
                s = s.replace(".", "").replace(",", ".")
            numero = Decimal(s)
        else:
            numero = Decimal(str(valor))
    except (InvalidOperation, ValueError):
        erros[campo] = "Valor monetário inválido"
        return None
    if not numero.is_finite():
        erros[campo] = "Valor monetário inválido"
        return None
    centavos = int((numero * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    if centavos < 0 or (centavos == 0 and not permitir_zero):
        erros[campo] = "Deve ser maior que zero"
        return None
    if centavos > 100_000_000_00:            # teto de R$ 100 milhões por lançamento
        erros[campo] = "Valor acima do permitido"
        return None
    return centavos


def data_iso(dados, campo, erros, obrigatorio=True):
    valor = dados.get(campo)
    if not valor:
        if obrigatorio:
            erros[campo] = "Campo obrigatório"
        return None
    try:
        return dt.date.fromisoformat(str(valor)).isoformat()
    except ValueError:
        erros[campo] = "Data inválida (use AAAA-MM-DD)"
        return None


def cor(dados, campo, erros, padrao="#6B7280"):
    valor = dados.get(campo) or padrao
    if not COR_RE.match(str(valor)):
        erros[campo] = "Cor deve estar no formato #RRGGBB"
        return None
    return valor.upper()


def mes_param(valor, obrigatorio=False):
    """Valida o parâmetro ?mes=AAAA-MM; sem valor usa o mês atual."""
    if not valor:
        if obrigatorio:
            raise ErroValidacao({"mes": "Parâmetro obrigatório"})
        return dt.date.today().strftime("%Y-%m")
    if not MES_RE.match(valor):
        raise ErroValidacao({"mes": "Use o formato AAAA-MM"})
    return valor


def verificar(erros: dict):
    if erros:
        raise ErroValidacao(erros)


def centavos_para_reais(centavos: int) -> float:
    return round((centavos or 0) / 100, 2)
