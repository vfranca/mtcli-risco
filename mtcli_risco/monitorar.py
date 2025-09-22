"""Comando monitorar - monitora o prejuízo do dia."""

import time
import click
from datetime import date
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger
from .conf import LOSS_LIMIT, STATUS_FILE, INTERVALO
from .risco import (
    carregar_estado,
    salvar_estado,
    risco_excedido,
    encerrar_todas_posicoes,
    cancelar_todas_ordens,
)

log = setup_logger()


@click.command("monitorar")
@click.option("--limite", "-l", default=LOSS_LIMIT, help="Limite de perda diária.")
@click.option(
    "--intervalo", "-i", default=INTERVALO, help="Intervalo entre verificações (segundos) default 60."
)
def monitorar(limite, intervalo):
    """Monitora continuamente o risco em tempo real."""
    conectar()
    click.echo(f"Monitorando risco a cada {intervalo}s. Limite: {limite}")
    try:
        while True:
            hoje = date.today()
            estado = carregar_estado(STATUS_FILE)

            if estado.get("data") != hoje.isoformat():
                estado["bloqueado"] = False
                salvar_estado(STATUS_FILE, hoje, False)

            if not estado.get("bloqueado") and risco_excedido(limite):
                click.echo("Limite {limite} excedido. Encerrando posições.")
                encerrar_todas_posicoes()
                cancelar_todas_ordens()
                salvar_estado(STATUS_FILE, hoje, True)
            elif estado.get("bloqueado"):
                    click.echo(f"O limite {limite} foi excedido")
                    shutdown()
                    return
            else:
                click.echo(f"Dentro do limite {limite}")

            time.sleep(intervalo)
    except KeyboardInterrupt:
        click.echo("Monitoramento interrompido.")
    finally:
        shutdown()


if __name__ == "__main__":
    monitorar()
