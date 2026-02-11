"""
Comando PANIC CLOSE.
"""

import click
from mtcli.logger import setup_logger
from mtcli_risco.models.panic_model import panic_close_all
from mtcli_risco import conf

log = setup_logger()


@click.command()
@click.option(
    "--no-retry",
    is_flag=True,
    help="Não aguardar reabertura do mercado",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Simula o panic close sem enviar ordens nem hardstop",
)
@click.option(
    "--terminal-path",
    type=click.Path(exists=True),
    help="Caminho do terminal MT5 (override temporário)",
)
def panic_cmd(no_retry: bool, dry_run: bool, terminal_path: str | None):
    """
    Executa o PANIC CLOSE com HARDSTOP.
    """
    if terminal_path:
        log.warning(
            f"[PANIC] Override do caminho do terminal: {terminal_path}"
        )
        conf.MT5_TERMINAL_PATH = terminal_path

    resultado = panic_close_all(
        retry_on_market_open=not no_retry,
        dry_run=dry_run,
    )

    click.echo("PANIC CLOSE executado.")
    click.echo(resultado)
