"""Lógica do plugin risco."""

import MetaTrader5 as mt5
import json
import os
from datetime import date, datetime, time
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger

log = setup_logger()


def carregar_estado(arquivo_estado):
    """Carrega o estado do controle de risco."""
    if os.path.exists(arquivo_estado):
        with open(arquivo_estado, "r") as f:
            log.info(f"Carregando dados do arquivo {arquivo_estado}")
            return json.load(f)
    return {"data": None, "bloqueado": False}


def salvar_estado(arquivo_estado, data, bloqueado):
    """Salva o estado do controle de risco."""
    with open(arquivo_estado, "w") as f:
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


def risco_excedido(limite):
    """Verifica se o prejuízo excedeu o limite permitido."""
    conectar()
    try:
        total_lucro = calcular_lucro_total_dia()
        return total_lucro <= limite
    except Exception as e:
        log.error(f"Erro ao verificar risco: {e}")
        return False
    finally:
        shutdown()
