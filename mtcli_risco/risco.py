"""Lógica do plugin risco."""

import MetaTrader5 as mt5
import json
import os
from datetime import date

SYMBOL = "WIN$N"  # Altere conforme necessário

def carregar_estado(arquivo_estado):
    if os.path.exists(arquivo_estado):
        with open(arquivo_estado, "r") as f:
            return json.load(f)
    return {"data": None, "bloqueado": False}

def salvar_estado(arquivo_estado, data, bloqueado):
    with open(arquivo_estado, "w") as f:
        json.dump({"data": data.isoformat(), "bloqueado": bloqueado}, f)

def risco_excedido(limite):
    info = mt5.account_info()
    if info is None:
        raise RuntimeError("Erro ao obter informações da conta.")
    return info.profit <= limite

def enviar_ordem_compra(symbol=SYMBOL, volume=1.0):
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        raise RuntimeError("Erro ao obter preço do ativo.")

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY,
        "price": tick.ask,
        "deviation": 10,
        "magic": 123456,
        "comment": "ordem automatica",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    return result
