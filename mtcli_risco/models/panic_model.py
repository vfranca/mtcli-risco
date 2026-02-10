"""
Modo PANIC CLOSE.

Responsável por:
- Encerrar TODAS as posições abertas (hedge ou netting)
- Cancelar TODAS as ordens pendentes
- Funcionar com market aberto ou fechado (retry automático)
- Suportar modo DRY-RUN (simulação)
- Acionar HARDSTOP via Sistema Operacional (Windows)
"""

import time
import MetaTrader5 as mt5

from mtcli.logger import setup_logger
from mtcli.mt5_context import mt5_conexao
from mtcli_risco.models.hardstop_model import hardstop

log = setup_logger()


def _trade_permitido() -> bool:
    """
    Verifica se a conta permite trading.
    """
    info = mt5.account_info()
    return bool(info and info.trade_allowed)


def _market_aberto(symbol: str) -> bool:
    """
    Verifica se o mercado do símbolo está aberto para trading.
    """
    info = mt5.symbol_info(symbol)
    return bool(info and info.trade_mode == mt5.SYMBOL_TRADE_MODE_FULL)


def _close_position(position, dry_run: bool = False) -> bool:
    """
    Fecha uma posição individual (compatível com hedge e netting).
    """
    symbol = position.symbol
    tick = mt5.symbol_info_tick(symbol)

    if not tick:
        log.error(f"[PANIC] Tick indisponível para {symbol}")
        return False

    order_type = (
        mt5.ORDER_TYPE_SELL
        if position.type == mt5.ORDER_TYPE_BUY
        else mt5.ORDER_TYPE_BUY
    )

    price = tick.bid if order_type == mt5.ORDER_TYPE_SELL else tick.ask

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": position.volume,
        "type": order_type,
        "price": price,
        "deviation": 20,
        "magic": 999999,
        "comment": "PANIC CLOSE",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # Conta hedge → fechamento por ticket
    if position.ticket:
        request["position"] = position.ticket

    if dry_run:
        log.warning(f"[PANIC][DRY] Fechamento simulado: {request}")
        return True

    result = mt5.order_send(request)

    if not result:
        log.error(
            f"[PANIC] order_send retornou None | "
            f"{symbol} | last_error={mt5.last_error()}"
        )
        return False

    if result.retcode != mt5.TRADE_RETCODE_DONE:
        log.error(
            f"[PANIC] Falha ao fechar posição {symbol} | "
            f"retcode={result.retcode}"
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
    Executa o fechamento emergencial de TODAS as posições e ordens.

    Parâmetros
    ----------
    retry_on_market_open : bool
        Reexecuta automaticamente quando o market estiver fechado.
    retry_interval : int
        Intervalo (segundos) entre tentativas quando market fechado.
    dry_run : bool
        Simula as ações sem enviar ordens reais.

    Retorna
    -------
    dict
        Estatísticas da execução do panic close.
    """
    stats = {
        "positions_total": 0,
        "positions_closed": 0,
        "orders_cancelled": 0,
        "market_closed": False,
        "trade_disabled": False,
        "dry_run": dry_run,
        "hardstop_executed": False,
    }

    while True:
        market_fechado = False

        with mt5_conexao():
            if not _trade_permitido():
                log.critical("[PANIC] Trading desabilitado na conta!")
                stats["trade_disabled"] = True
                break

            positions = mt5.positions_get()
            orders = mt5.orders_get()

            if positions:
                stats["positions_total"] = len(positions)

            # 1️⃣ Fechamento de posições
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

            # 2️⃣ Cancelamento de ordens pendentes
            if orders:
                for ordem in orders:
                    if dry_run:
                        log.warning(
                            f"[PANIC][DRY] Cancelamento simulado | "
                            f"ticket={ordem.ticket}"
                        )
                        stats["orders_cancelled"] += 1
                        continue

                    request = {
                        "action": mt5.TRADE_ACTION_REMOVE,
                        "order": ordem.ticket,
                    }

                    result = mt5.order_send(request)

                    if not result:
                        log.error(
                            f"[PANIC] Falha ao cancelar ordem {ordem.ticket} | "
                            f"last_error={mt5.last_error()}"
                        )
                        continue

                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        stats["orders_cancelled"] += 1
                        log.warning(
                            f"[PANIC] Ordem cancelada | ticket={ordem.ticket}"
                        )
                    else:
                        log.error(
                            f"[PANIC] Falha ao cancelar ordem {ordem.ticket} | "
                            f"retcode={result.retcode}"
                        )

        if not market_fechado:
            break

        stats["market_closed"] = True

        if not retry_on_market_open:
            break

        log.critical(
            f"[PANIC] Market fechado. Nova tentativa em {retry_interval}s..."
        )
        time.sleep(retry_interval)

    # 3️⃣ HARDSTOP via Sistema Operacional
    if not dry_run:
        hardstop()
        stats["hardstop_executed"] = True
    else:
        log.warning("[PANIC][DRY] HARDSTOP não executado (modo simulação)")

    log.critical(f"[PANIC] Resultado final: {stats}")
    return stats
