"""Comando risco: monitora e bloqueia ordens se o limite diário de prejuízo for atingido."""

import click
from .commands.checar import checar
from .commands.monitorar import monitorar
from .commands.trades import trades


@click.group("risco")
@click.version_option(package_name="mtcli-risco")
def cli():
    """Monitora e bloqueia ordens se o limite de prejuízo for atingido."""
    pass


cli.add_command(checar, name="checar")
cli.add_command(monitorar, name="monitorar")
cli.add_command(trades, name="trades")


if __name__ == "__main__":
    cli()
