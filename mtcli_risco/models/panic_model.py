"""
Modo PANIC CLOSE.

- Funciona em conta hedge e netting
- Detecta market fechado
- Reexecuta automaticamente quando o market abrir
- Suporta modo DRY-RUN (simulação)
"""

import time
import MetaTrader5 as mt5
from mtcli.logger import setup_logger
from mtcli.mt5_context import mt5_conexao

log = setup_logger()


def _trade_permitido() -> bool:
    info = mt5.account_info()
    return bool(info and info.trade_allowed)


def _market_aberto(symbol: str) -> bool:
    info = mt5.symbol_info(symbol)
    return bool(info and info.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL)


def _close_position(position, dry_run: bool = False) -> bool:
    symbol = position.symbol
    tick = mt5.symbol_info_tick(symbol)

    if not tick:
        log.error(f"[PANIC] Tick indisponível para {symbol}")
        return False

    tipo = (
        mt5.ORDER_TYPE_SELL
        if position.type == mt5.ORDER_TYPE_BUY
        else mt5.ORDER_TYPE_BUY
    )

    price = tick.bid if tipo == mt5.ORDER_TYPE_SELL else tick.ask

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": position.volume,
        "type": tipo,
        "price": price,
        "deviation": 20,
        "magic": 999999,
        "comment": "PANIC CLOSE",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    if position.ticket:
        request["position"] = position.ticket

    if dry_run:
        log.warning(f"[PANIC][DRY] Fechamento simulado: {request}")
        return True

    result = mt5.order_send(request)

    if not result:
        log.error(
            f"[PANIC] order_send None | {symbol} | last_error={mt5.last_error()}"
        )
        return False

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        log.error(
            f"[PANIC] Falha ao fechar {symbol} | retcode={result.retcode}"
        )
        return False

    log.critical(
        f"[PANIC] Posição fechada | {symbol} vol={position.volume}"
    )
    return True


def panic_close_all(
    retry_on_market_open: bool = True,
    retry_interval: int = 60,
    dry_run: bool = False,
) -> dict:
    """
    Executa o fechamento emergencial de posições e ordens.

    retry_on_market_open:
        Reexecuta automaticamente quando o market abrir.

    dry_run:
        Simula ações sem enviar ordens.
    """
    stats = {
        "positions_total": 0,
        "positions_closed": 0,
        "orders_cancelled": 0,
        "market_closed": False,
        "trade_disabled": False,
        "dry_run": dry_run,
    }

    while True:
        with mt5_conexao():
            if not _trade_permitido():
                log.critical("[PANIC] Trading desabilitado na conta!")
                stats["trade_disabled"] = True
                return stats

            positions = mt5.positions_get()
            orders = mt5.orders_get()

            if positions:
                stats["positions_total"] = len(positions)

            market_fechado = False

            # 1️⃣ Fechar posições
            if positions:
                for pos in positions:
                    if not _market_aberto(pos.symbol):
                        market_fechado = True
                        log.critical(
                            f"[PANIC] Market fechado para {pos.symbol}"
                        )
                        continue

                    if _close_position(pos, dry_run=dry_run):
                        stats["positions_closed"] += 1

            # 2️⃣ Cancelar ordens pendentes
            if orders:
                for ordem in orders:
                    if dry_run:
                        log.warning(
                            f"[PANIC][DRY] Cancelamento simulado | ticket={ordem.ticket}"
                        )
                        stats["orders_cancelled"] += 1
                        continue

                    result = mt5.order_delete(ordem.ticket)
                    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                        stats["orders_cancelled"] += 1
                        log.warning(
                            f"[PANIC] Ordem cancelada | ticket={ordem.ticket}"
                        )
                    else:
                        log.error(
                            f"[PANIC] Falha ao cancelar ordem {ordem.ticket}"
                        )

        if not market_fechado:
            break

        stats["market_closed"] = True

        if not retry_on_market_open:
            break

        log.critical(
            f"[PANIC] Market fechado. Repetindo em {retry_interval}s..."
        )
        time.sleep(retry_interval)

    log.critical(f"[PANIC] Resultado final: {stats}")
    return stats
