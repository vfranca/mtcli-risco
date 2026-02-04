"""
Comando monitorar.

Monitora continuamente o risco diário e executa PANIC CLOSE
quando o limite é excedido.
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
)
from mtcli_risco.models.panic_model import panic_close_all

log = setup_logger()


@click.command()
@click.version_option(package_name="mtcli-risco")
@click.option("--limite", "-l", default=LOSS_LIMIT, show_default=True)
@click.option("--intervalo", "-i", default=INTERVALO, show_default=True)
@click.option("--dry-run", is_flag=True, help="Simula o panic close.")
def monitorar_cmd(limite: float, intervalo: int, dry_run: bool):
    """
    Inicia o monitoramento contínuo do risco diário.
    """
    click.echo(
        f"Monitorando risco | limite={limite:.2f} intervalo={intervalo}s"
    )
    log.info(
        f"[MONITOR] Iniciado | limite={limite} intervalo={intervalo}s dry_run={dry_run}"
    )

    try:
        while True:
            hoje = date.today()
            estado = carregar_estado(STATUS_FILE)

            if estado["data"] != hoje.isoformat():
                salvar_estado(STATUS_FILE, hoje, False)
                estado["bloqueado"] = False

            if not estado["bloqueado"] and risco_excedido(limite):
                click.echo("LIMITE DE RISCO EXCEDIDO — PANIC CLOSE")
                log.critical("[MONITOR] Disparando PANIC CLOSE")

                resultado = panic_close_all(
                    retry_on_market_open=True,
                    dry_run=dry_run,
                )

                salvar_estado(STATUS_FILE, hoje, True)
                log.critical(f"[MONITOR] Panic finalizado: {resultado}")

            time.sleep(intervalo)

    except KeyboardInterrupt:
        click.echo("Monitoramento interrompido.")
        log.info("[MONITOR] Interrompido pelo usuário.")
