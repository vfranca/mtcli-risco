"""
Comando trades.

Exibe lucros realizados, abertos e totais do dia.
"""

import click
from mtcli.logger import setup_logger
from mtcli_risco.models.trades_model import (
    obter_lucro_aberto,
    calcular_lucro_realizado,
    calcular_lucro_total_dia,
)

log = setup_logger()


@click.command(
    "trades",
    help="Exibe os lucros realizados, abertos e totais do dia.",
)
@click.version_option(package_name="mtcli-risco")
@click.option("--aberto", "-a", is_flag=True, help="Exibe o lucro em aberto.")
@click.option("--realizado", "-r", is_flag=True, help="Exibe o lucro realizado.")
@click.option("--total", "-t", is_flag=True, help="Exibe o lucro total.")
def trades_cmd(aberto: bool, realizado: bool, total: bool):
    """
    Exibe informações de lucro do dia atual.
    """
    if aberto:
        valor = obter_lucro_aberto()
        click.echo(f"{valor:.2f}")
        return

    if realizado:
        valor = calcular_lucro_realizado()
        click.echo(f"{valor:.2f}")
        return

    if total:
        valor = calcular_lucro_total_dia()
        click.echo(f"{valor:.2f}")
        return

    aberto_v = obter_lucro_aberto()
    realizado_v = calcular_lucro_realizado()
    total_v = aberto_v + realizado_v

    click.echo(f"lucro em aberto: {aberto_v:.2f}")
    click.echo(f"lucro realizado: {realizado_v:.2f}")
    click.echo(f"lucro total: {total_v:.2f}")
