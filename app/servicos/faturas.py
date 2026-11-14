"""Regras de negócio do cartão de crédito.

Regra adotada (igual à da maioria dos bancos):
  * A fatura FECHA no dia de fechamento do cartão.
  * Compras feitas ANTES do dia de fechamento entram na fatura que fecha no
    mesmo mês; compras NO dia de fechamento ou depois vão para a fatura que
    fecha no mês seguinte.
  * O vencimento acontece no dia de vencimento: no mesmo mês do fechamento se
    dia_vencimento > dia_fechamento, senão no mês seguinte.
  * A fatura é identificada pelo mês do VENCIMENTO (mes_referencia 'AAAA-MM').
  * Em compras parceladas, a parcela i cai (i-1) faturas depois da 1ª.
"""
import datetime as dt


def somar_meses(ano: int, mes: int, n: int) -> tuple[int, int]:
    total = ano * 12 + (mes - 1) + n
    return total // 12, total % 12 + 1


def somar_meses_data(data: dt.date, n: int) -> dt.date:
    """Mesma data n meses depois (dia limitado ao último dia do mês)."""
    import calendar
    ano, mes = somar_meses(data.year, data.month, n)
    return dt.date(ano, mes, min(data.day, calendar.monthrange(ano, mes)[1]))


def calcular_datas_fatura(data_compra: dt.date, dia_fechamento: int, dia_vencimento: int,
                          parcela: int = 1) -> dict:
    ano, mes = data_compra.year, data_compra.month
    if data_compra.day >= dia_fechamento:
        ano, mes = somar_meses(ano, mes, 1)          # já fechou: vai para a próxima
    ano, mes = somar_meses(ano, mes, parcela - 1)    # desloca pelas parcelas
    fechamento = dt.date(ano, mes, dia_fechamento)
    if dia_vencimento > dia_fechamento:
        venc = dt.date(ano, mes, dia_vencimento)
    else:
        a2, m2 = somar_meses(ano, mes, 1)
        venc = dt.date(a2, m2, dia_vencimento)
    return {
        "mes_referencia": venc.strftime("%Y-%m"),
        "data_fechamento": fechamento.isoformat(),
        "data_vencimento": venc.isoformat(),
    }


def obter_ou_criar_fatura(db, cartao: dict, data_compra: dt.date, parcela: int = 1) -> int:
    """Devolve o id da fatura onde a compra (ou parcela) cai, criando se preciso."""
    datas = calcular_datas_fatura(data_compra, cartao["dia_fechamento"], cartao["dia_vencimento"], parcela)
    linha = db.execute(
        "SELECT id FROM fatura WHERE cartao_id = ? AND mes_referencia = ?",
        (cartao["id"], datas["mes_referencia"]),
    ).fetchone()
    if linha:
        return linha["id"]
    cur = db.execute(
        """INSERT INTO fatura (cartao_id, mes_referencia, data_fechamento, data_vencimento)
           VALUES (?, ?, ?, ?)""",
        (cartao["id"], datas["mes_referencia"], datas["data_fechamento"], datas["data_vencimento"]),
    )
    return cur.lastrowid


def dividir_parcelas(valor_centavos: int, n: int) -> list[int]:
    """Divide um valor em n parcelas inteiras de centavos.

    O resto da divisão inteira vai para a 1ª parcela, garantindo que a soma
    das parcelas seja exatamente o valor total. Ex.: R$ 100,00 em 3x ->
    [3334, 3333, 3333].
    """
    if n < 1:
        raise ValueError("n deve ser >= 1")
    base, resto = divmod(valor_centavos, n)
    return [base + resto] + [base] * (n - 1)


def status_calculado(fatura: dict, hoje: dt.date | None = None) -> str:
    """ABERTA até a data de fechamento; depois FECHADA, a não ser que esteja PAGA."""
    if fatura["status"] == "PAGA":
        return "PAGA"
    hoje = hoje or dt.date.today()
    return "FECHADA" if hoje >= dt.date.fromisoformat(fatura["data_fechamento"]) else "ABERTA"
