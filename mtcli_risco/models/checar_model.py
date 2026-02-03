"""
Model de controle de risco.

Responsável por:
- persistência de estado diário
- verificação de limite de prejuízo
- encerramento de posições
- cancelamento de ordens
"""

import json
import os
from datetime import date
import MetaTrader5 as mt5
from mtcli.logger import setup_logger
from mtcli_risco.mt5_context import mt5_conexao
from .trades_model import calcular_lucro_total_dia

log = setup_logger()


def carregar_estado(status_file: str) -> dict:
    """
    Carrega o estado persistido do controle de risco.
    """
    if os.path.exists(status_file):
        with open(status_file, "r") as f:
            log.info(f"[ESTADO] Carregando {status_file}")
            return json.load(f)
    return {"data": "", "bloqueado": False}


def salvar_estado(status_file: str, data: date, bloqueado: bool) -> None:
    """
    Persiste o estado diário do controle de risco.
    """
    with open(status_file, "w") as f:
        json.dump(
            {"data": data.isoformat(), "bloqueado": bloqueado},
            f,
            indent=2,
        )
    log.info(f"[ESTADO] Salvo | data={data.isoformat()} bloqueado={bloqueado}")


def encerrar_todas_posicoes() -> None:
    """
    Encerra todas as posições abertas no MT5.
    """
    with mt5_conexao():
        positions = mt5.positions_get()

        if not positions:
            log.info("[MT5] Nenhuma posição aberta.")
            return

        for pos in positions:
            tipo_oposto = (
                mt5.ORDER_TYPE_SELL
                if pos.type == mt5.ORDER_TYPE_BUY
                else mt5.ORDER_TYPE_BUY
            )

            ordem = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": tipo_oposto,
                "position": pos.ticket,
                "deviation": 10,
                "magic": 1000,
                "comment": "Fechamento por limite de risco",
            }

            log.warning(f"[MT5] Encerrando posição {pos.ticket}")
            resultado = mt5.order_send(ordem)

            if not resultado or resultado.retcode != mt5.TRADE_RETCODE_DONE:
                log.error(f"[MT5] Falha ao fechar {pos.ticket}: {resultado}")
            else:
                log.info(f"[MT5] Posição {pos.ticket} encerrada.")


def cancelar_todas_ordens() -> None:
    """
    Cancela todas as ordens pendentes.
    """
    with mt5_conexao():
        ordens = mt5.orders_get()

        if not ordens:
            log.info("[MT5] Nenhuma ordem pendente.")
            return

        for ordem in ordens:
            resultado = mt5.order_delete(ordem.ticket)
            if not resultado or resultado.retcode != mt5.TRADE_RETCODE_DONE:
                log.error(f"[MT5] Falha ao cancelar ordem {ordem.ticket}")
            else:
                log.info(f"[MT5] Ordem {ordem.ticket} cancelada.")


def risco_excedido(limite: float) -> bool:
    """
    Verifica se o prejuízo diário ultrapassou o limite configurado.
    """
    try:
        total = calcular_lucro_total_dia()
        if total <= limite:
            log.warning(
                f"[RISCO] Excedido | resultado={total:.2f} limite={limite:.2f}"
            )
            return True
        return False
    except Exception as exc:
        log.error(f"[RISCO] Erro ao verificar limite: {exc}")
        return False
