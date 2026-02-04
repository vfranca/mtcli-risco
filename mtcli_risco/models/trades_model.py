"""
Model de cálculos de lucro diário.
"""

import MetaTrader5 as mt5
from datetime import datetime, time
from mtcli.logger import setup_logger
from mtcli.mt5_context import mt5_conexao

log = setup_logger()


def calcular_lucro_realizado() -> float:
    """
    Calcula o lucro/prejuízo realizado no dia atual.
    """
    hoje = datetime.now().date()
    inicio = datetime.combine(hoje, time(0, 0))
    fim = datetime.combine(hoje, time(23, 59))

    with mt5_conexao():
        deals = mt5.history_deals_get(inicio, fim)

    if not deals:
        log.info("[TRADES] Nenhum deal realizado hoje.")
        return 0.0

    lucro = sum(
        deal.profit for deal in deals if deal.entry == mt5.DEAL_ENTRY_OUT
    )

    log.info(f"[TRADES] Lucro realizado: {lucro:.2f}")
    return lucro


def obter_lucro_aberto() -> float:
    """
    Obtém o lucro/prejuízo das posições atualmente abertas.
    """
    with mt5_conexao():
        info = mt5.account_info()

    if not info:
        log.warning("[TRADES] account_info indisponível.")
        return 0.0

    log.info(f"[TRADES] Lucro em aberto: {info.profit:.2f}")
    return info.profit


def calcular_lucro_total_dia() -> float:
    """
    Calcula o lucro total do dia (realizado + aberto).
    """
    realizado = calcular_lucro_realizado()
    aberto = obter_lucro_aberto()
    total = realizado + aberto

    log.info(
        f"[TRADES] Total do dia | realizado={realizado:.2f} aberto={aberto:.2f}"
    )
    return total
