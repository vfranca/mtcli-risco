"""
Hardstop via Sistema Operacional (Windows).

Responsável por:
- Encerrar o processo do MetaTrader 5
- Bloquear tráfego de rede do terminal via Firewall
- Impedir qualquer novo envio de ordens após PANIC
"""

import os
import subprocess
import signal
from mtcli.logger import setup_logger

log = setup_logger()

MT5_PROCESS_NAME = "terminal64.exe"
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
    log.critical("[HARDSTOP] Encerrando processo do MT5")

    _run(
        [
            "taskkill",
            "/F",   # força
            "/IM",
            MT5_PROCESS_NAME,
        ]
    )


def block_mt5_firewall() -> None:
    """
    Bloqueia qualquer tráfego de rede do MT5 via Firewall do Windows.
    """
    log.critical("[HARDSTOP] Bloqueando tráfego de rede do MT5 (Firewall)")

    # Remove regra anterior se existir (idempotente)
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
            f"program=%ProgramFiles%\\MetaTrader 5\\terminal64.exe",
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
