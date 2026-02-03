import click
from .commands.checar import checar_cmd
from .commands.monitorar import monitorar_cmd
from .commands.trades import trades_cmd


@click.group()
@click.version_option(package_name="mtcli-risco")
def risco_cli():
    """
    Plugin mtcli-risco.

    Conjunto de comandos para gerenciamento e controle de risco diário
    baseado em lucro/prejuízo no MetaTrader 5.
    """
    pass


cli.add_command(checar_cmd, name="checar")
cli.add_command(monitorar_cmd, name="monitorar")
cli.add_command(trades_cmd, name="trades")
