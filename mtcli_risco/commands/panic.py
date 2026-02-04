"""
Comando panic.

Executa o PANIC CLOSE manualmente.
"""

import click
from mtcli.logger import setup_logger
from mtcli_risco.models.panic_model import panic_close_all

log = setup_logger()


@click.command()
@click.option("--dry-run", is_flag=True, help="Simula o panic close.")
@click.option(
    "--no-retry",
    is_flag=True,
    help="Não repetir quando o market estiver fechado.",
)
def panic_cmd(dry_run: bool, no_retry: bool):
    """
    Executa manualmente o fechamento emergencial de posições.
    """
    click.echo("Executando PANIC CLOSE...")
    log.critical(
        f"[PANIC] Execução manual | dry_run={dry_run} retry={not no_retry}"
    )

    resultado = panic_close_all(
        retry_on_market_open=not no_retry,
        dry_run=dry_run,
    )

    click.echo("PANIC CLOSE finalizado.")
    log.critical(f"[PANIC] Resultado: {resultado}")
