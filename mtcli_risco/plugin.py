"""Comando risco: monitora e bloqueia ordens se o limite diário de prejuízo for atingido."""

import click
from .checar import checar
from .monitorar import monitorar


@click.group("risco")
@click.version_option(package_name="mtcli-risco")
def cli():
    """Monitora e bloqueia ordens se o limite de prejuízo for atingido."""
    pass


cli.add_command(checar)
cli.add_command(monitorar)


if __name__ == "__main__":
    cli()
