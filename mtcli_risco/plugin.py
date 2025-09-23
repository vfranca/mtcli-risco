"""Comando risco: monitora e bloqueia ordens se o limite diário de prejuízo for atingido."""

import click
from .commands.checar import checar
from .commands.monitorar import monitorar
from .commands.lucro import lucro


@click.group("risco")
@click.version_option(package_name="mtcli-risco")
def cli():
    """Monitora e bloqueia ordens se o limite de prejuízo for atingido."""
    pass


cli.add_command(checar)
cli.add_command(monitorar)
cli.add_command(lucro)


if __name__ == "__main__":
    cli()
