"""
Hardstop via Sistema Operacional (Windows).

Responsável por:
- Encerrar o processo do MetaTrader 5
- Bloquear tráfego de rede do terminal via Firewall
- Impedir qualquer novo envio de ordens após PANIC
"""

import os
import subprocess
from mtcli.logger import setup_logger
from mtcli_risco.conf import MT5_TERMINAL_PATH

log = setup_logger()

FIREWALL_RULE_NAME = "MT5_HARDSTOP_BLOCK"


def _run(cmd: list[str]) -> bool:
    """
    Executa comando no Windows.
    """
    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False,
        )
        return True
    except subprocess.CalledProcessError as exc:
        log.error(f"[HARDSTOP] Falha ao executar comando: {cmd} | {exc}")
        return False


def kill_mt5_process() -> None:
    """
    Encerra o processo do MetaTrader 5 à força.
    """
    exe_name = os.path.basename(MT5_TERMINAL_PATH)

    log.critical(f"[HARDSTOP] Encerrando processo {exe_name}")

    _run(
        [
            "taskkill",
            "/F",
            "/IM",
            exe_name,
        ]
    )


def block_mt5_firewall() -> None:
    """
    Bloqueia qualquer tráfego de rede do MT5 via Firewall do Windows.
    """
    log.critical(
        f"[HARDSTOP] Bloqueando tráfego de rede do MT5 | {MT5_TERMINAL_PATH}"
    )

    # Remove regra anterior (idempotente)
    _run(
        [
            "netsh",
            "advfirewall",
            "firewall",
            "delete",
            "rule",
            f"name={FIREWALL_RULE_NAME}",
        ]
    )

    # Cria regra de bloqueio
    _run(
        [
            "netsh",
            "advfirewall",
            "firewall",
            "add",
            "rule",
            f"name={FIREWALL_RULE_NAME}",
            "dir=out",
            "action=block",
            f"program={MT5_TERMINAL_PATH}",
            "enable=yes",
        ]
    )


def unblock_mt5_firewall() -> None:
    """
    Remove o bloqueio de firewall do MT5 (uso manual).
    """
    log.warning("[HARDSTOP] Removendo bloqueio de firewall do MT5")

    _run(
        [
            "netsh",
            "advfirewall",
            "firewall",
            "delete",
            "rule",
            f"name={FIREWALL_RULE_NAME}",
        ]
    )


def hardstop() -> None:
    """
    Executa o HARDSTOP completo:
    - Mata o MT5
    - Bloqueia rede via Firewall
    """
    log.critical("========== HARDSTOP ACIONADO ==========")
    kill_mt5_process()
    block_mt5_firewall()
    log.critical("========== MT5 TOTALMENTE BLOQUEADO ==========")
