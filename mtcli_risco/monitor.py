import time
import click
from datetime import date
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger
from .conf import LOSS_LIMIT, STATUS_FILE
from .risco import (
    carregar_estado,
    salvar_estado,
    risco_excedido,
    encerrar_todas_posicoes,
    cancelar_todas_ordens,
)

log = setup_logger()


@click.command("risco-monitor")
@click.option("--limite", "-l", default=LOSS_LIMIT, help="Limite de perda diária.")
@click.option(
    "--intervalo", "-i", default=60, help="Intervalo entre verificações (segundos)."
)
def monitor(limite, intervalo):
    """Monitoramento contínuo do risco em tempo real."""
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
                click.echo("Limite excedido. Encerrando posições.")
                encerrar_todas_posicoes()
                cancelar_todas_ordens()
                salvar_estado(STATUS_FILE, hoje, True)
            else:
                click.echo("Dentro do limite.")

            time.sleep(intervalo)
    except KeyboardInterrupt:
        click.echo("Monitoramento interrompido.")
    finally:
        shutdown()


if __name__ == "__main__":
    monitor()
