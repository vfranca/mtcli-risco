"""Cálculos do lucro do dia."""

import MetaTrader5 as mt5
from datetime import date, datetime, time
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger
from ..mt5_context import mt5_conexao


log = setup_logger()


def calcular_lucro_realizado() -> float:
    """Calcula o lucro realizado do dia."""
    hoje = datetime.now().date()
    inicio = datetime.combine(hoje, time(0, 0))
    fim = datetime.combine(hoje, time(23, 59))

    with mt5_conexao():
        deals = mt5.history_deals_get(inicio, fim)

    lucro_realizado = 0.0
    if deals is not None:
        lucro_realizado = sum(deal.profit for deal in deals if deal.type in (1, 2))
    log.info(f"lucro realizado: {lucro_realizado:.2f}")

    return lucro_realizado


def lucro_aberto() -> float:
    """Obtem o lucro em aberto."""
    with mt5_conexao():
        info = mt5.account_info()

    lucro_aberto = info.profit if info else 0.0
    log.info(f"lucro aberto: {lucro_aberto:.2f}")

    return lucro_aberto


def calcular_lucro_total_dia() -> float:
    """Calcula o lucro total do dia."""
    lucro_realizado = calcular_lucro_realizado()
    lucro_aberto = calcular_lucro_aberto()
    total = lucro_realizado + lucro_aberto
    log.info(
        f"Lucro realizado: {lucro_realizado:.2f}, lucro aberto: {lucro_aberto:.2f}, total: {total:.2f}"
    )
    return total
