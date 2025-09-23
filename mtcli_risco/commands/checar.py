"""Comando checar - verifica se o loss limit foi atingido."""

import click
from datetime import date
from mtcli.logger import setup_logger
from ..conf import LOSS_LIMIT, STATUS_FILE
from ..models.lucro import calcular_lucro_total_dia
from ..models.risco import (
    carregar_estado,
    salvar_estado,
    risco_excedido,
    encerrar_todas_posicoes,
    cancelar_todas_ordens,
)


log = setup_logger()


@click.command("checar")
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
def checar(limite, lucro):
    """Verifica e bloqueia ordens se o limite de prejuízo for atingido."""
    if lucro:
        lucro = calcular_lucro_total_dia()
        click.echo(f"Lucro total do dia: {lucro:.2f}")
        log.info(f"Lucro total do dia: {lucro:.2f}")
        return

    estado = carregar_estado(STATUS_FILE)
    hoje = date.today()

    if estado["data"] != hoje.isoformat():
        estado["bloqueado"] = False

    if estado["bloqueado"]:
        click.echo("Bloqueado hoje por risco. Nenhuma ordem deve ser enviada.")
        return

    if risco_excedido(limite):
        click.echo(
            f"Limite {limite:.2f} excedido. Encerrando posições e bloqueando novas ordens."
        )
        log.info(f"Risco {limite:.2f} excedido, iniciando encerramento de posições.")
        encerrar_todas_posicoes()
        cancelar_todas_ordens()
        estado["bloqueado"] = True
    else:
        click.echo("Dentro do limite de risco.")
        log.info(f"Risco dentro do limite {limite:.2f}")

    salvar_estado(STATUS_FILE, hoje, estado["bloqueado"])


if __name__ == "__main__":
    checar()
