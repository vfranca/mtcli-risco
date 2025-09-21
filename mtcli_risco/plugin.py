"""Comando risco adiciona risco ao mtcli."""

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
    calcular_lucro_total_dia,
)


log = setup_logger()


@click.command("risco")
@click.version_option(package_name="mtcli-risco")
@click.option(
    "--limite",
    "-l",
    default=LOSS_LIMIT,
    help="Limite de perda diária (ex: -500), default -180.00.",
)
@click.option(
    "--lucro",
    is_flag=True,
    default=False,
    help="Exibe o lucro total do dia atualizado e sai.",
)
def cli(limite, lucro):
    """Monitora e bloqueia ordens se o limite de prejuízo for atingido."""
    conectar()

    if lucro:
        lucro = calcular_lucro_total_dia()
        click.echo(f"Lucro total do dia: {lucro:.2f}")
        shutdown()
        return

    estado = carregar_estado(STATUS_FILE)
    hoje = date.today()

    if estado["data"] != hoje.isoformat():
        estado["bloqueado"] = False
        salvar_estado(STATUS_FILE, hoje, False)

    if estado["bloqueado"]:
        click.echo("⚠ Bloqueado hoje por risco. Nenhuma ordem deve ser enviada.")
        shutdown()
        return

    if risco_excedido(limite):
        click.echo(
            f"🚫 Limite diário ({limite}) excedido. Encerrando posições e bloqueando novas ordens."
        )
        encerrar_todas_posicoes()
        cancelar_todas_ordens()
        salvar_estado(STATUS_FILE, hoje, True)
    else:
        click.echo("Dentro do limite de risco.")

    shutdown()


if __name__ == "__main__":
    cli()
