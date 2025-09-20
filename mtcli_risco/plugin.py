"""Comando risco adiciona risco ao mtcli."""

import click
from datetime import date
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger
from .conf import LOSS_LIMIT, ARQUIVO_ESTADO
from .risco import carregar_estado, salvar_estado, risco_excedido

log = setup_logger()


@click.command("risco")
@click.version_option(package_name="mtcli-risco")
@click.option(
    "--limite",
    "-l",
    default=LOSS_LIMIT,
    help="Limite de perda diária (ex: -500), default -180.00.",
)
def cli(limite):
    """Monitora e bloqueia ordens se o limite de prejuízo for atingido."""
    conectar()

    estado = carregar_estado(ARQUIVO_ESTADO)
    hoje = date.today()

    if estado["data"] != hoje.isoformat():
        estado["bloqueado"] = False
        salvar_estado(ARQUIVO_ESTADO, hoje, False)

    if estado["bloqueado"]:
        click.echo("⚠ Bloqueado hoje por risco. Nenhuma ordem deve ser enviada.")
        shutdown()
        return

    if risco_excedido(limite):
        click.echo(f"🚫 Limite diário ({limite}) excedido. Bloqueando novas ordens.")
        salvar_estado(ARQUIVO_ESTADO, hoje, True)
    else:
        click.echo("Dentro do limite de risco.")

    shutdown()


if __name__ == "__main__":
    cli()
