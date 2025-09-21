"""Lógica do plugin risco."""

import MetaTrader5 as mt5
import json
import os
from datetime import date, datetime, time
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger

log = setup_logger()


def carregar_estado(STATUS_FILE):
    """Carrega o estado do controle de risco."""
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            log.info(f"Carregando dados do arquivo {STATUS_FILE}")
            return json.load(f)
    return {"data": None, "bloqueado": False}


def salvar_estado(STATUS_FILE, data, bloqueado):
    """Salva o estado do controle de risco."""
    with open(STATUS_FILE, "w") as f:
        json.dump({"data": data.isoformat(), "bloqueado": bloqueado}, f)
        log.info(f"Salvando o estado: data {data} bloqueado {bloqueado}")


def calcular_lucro_total_dia():
    """Calcula o lucro total do dia."""
    hoje = datetime.now().date()
    inicio = datetime.combine(hoje, time(0, 0))
    fim = datetime.combine(hoje, time(23, 59))

    deals = mt5.history_deals_get(inicio, fim)
    lucro_realizado = 0.0

    if deals is not None:
        lucro_realizado = sum(deal.profit for deal in deals if deal.type in (1, 2))

    info = mt5.account_info()
    lucro_aberto = info.profit if info else 0.0

    total = lucro_realizado + lucro_aberto
    log.info(
        f"Lucro realizado: {lucro_realizado}, lucro aberto: {lucro_aberto}, total: {total}"
    )
    return total


def encerrar_todas_posicoes():
    positions = mt5.positions_get()
    if not positions:
        log.info("Nenhuma posição aberta para fechar.")
        return

    for pos in positions:
        tipo_oposto = (
            mt5.ORDER_TYPE_SELL
            if pos.type == mt5.ORDER_TYPE_BUY
            else mt5.ORDER_TYPE_BUY
        )
        ordem_fechar = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": tipo_oposto,
            "position": pos.ticket,
            "deviation": 10,
            "magic": 1000,
            "comment": "Fechando posição por limite de risco",
        }
        resultado = mt5.order_send(ordem_fechar)
        if resultado.retcode != mt5.TRADE_RETCODE_DONE:
            log.error(f"Falha ao fechar posição {pos.ticket}: {resultado.retcode}")
        else:
            log.info(f"Posição {pos.ticket} fechada com sucesso.")


def cancelar_todas_ordens():
    ordens = mt5.orders_get()
    if not ordens:
        log.info("Nenhuma ordem pendente para cancelar.")
        return

    for ordem in ordens:
        resultado = mt5.order_delete(ordem.ticket)
        if resultado.retcode != mt5.TRADE_RETCODE_DONE:
            log.error(f"Falha ao cancelar ordem {ordem.ticket}: {resultado.retcode}")
        else:
            log.info(f"Ordem {ordem.ticket} cancelada com sucesso.")


def risco_excedido(limite):
    conectar()
    try:
        total_lucro = calcular_lucro_total_dia()
        if total_lucro <= limite:
            log.warning(
                "Limite de prejuízo excedido! Encerrando posições e cancelando ordens."
            )
            encerrar_todas_posicoes()
            cancelar_todas_ordens()
            return True
        return False
    except Exception as e:
        log.error(f"Erro ao verificar risco: {e}")
        return False
    finally:
        shutdown()
