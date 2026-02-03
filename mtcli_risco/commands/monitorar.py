"""
Comando monitorar.

Monitora continuamente o risco diário em intervalos regulares.
"""

import time
import click
from datetime import date
from mtcli.logger import setup_logger
from mtcli_risco.conf import LOSS_LIMIT, STATUS_FILE, INTERVALO
from mtcli_risco.models.checar_model import (
    carregar_estado,
    salvar_estado,
    risco_excedido,
    encerrar_todas_posicoes,
    cancelar_todas_ordens,
)

log = setup_logger()


@click.command(
    "monitorar",
    help="Monitora continuamente o risco diário em tempo real.",
)
@click.version_option(package_name="mtcli-risco")
@click.option("--limite", "-l", default=LOSS_LIMIT, help="Limite de perda diária.")
@click.option(
    "--intervalo",
    "-i",
    default=INTERVALO,
    help="Intervalo entre verificações (segundos).",
)
def monitorar_cmd(limite: float, intervalo: int):
    """
    Inicia o monitoramento contínuo do risco diário.
    """
    click.echo(f"Monitorando risco a cada {intervalo}s | Limite: {limite:.2f}")
    log.info(f"[MONITOR] Iniciado | limite={limite} intervalo={intervalo}s")

    try:
        while True:
            hoje = date.today()
            estado = carregar_estado(STATUS_FILE)

            if estado["data"] != hoje.isoformat():
                log.info("[ESTADO] Novo dia detectado, resetando bloqueio.")
                salvar_estado(STATUS_FILE, hoje, False)
                estado["bloqueado"] = False

            if not estado["bloqueado"] and risco_excedido(limite):
                click.echo(f"Limite {limite:.2f} excedido. Encerrando posições.")
                log.warning("[RISCO] Limite excedido durante monitoramento.")
                encerrar_todas_posicoes()
                cancelar_todas_ordens()
                salvar_estado(STATUS_FILE, hoje, True)

            time.sleep(intervalo)

    except KeyboardInterrupt:
        click.echo("Monitoramento interrompido.")
        log.info("[MONITOR] Interrompido pelo usuário.")
