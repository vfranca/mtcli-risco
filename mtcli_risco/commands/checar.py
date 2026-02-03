"""
Comando checar.

Verifica se o limite diário de prejuízo foi atingido e,
se necessário, encerra posições e bloqueia novas ordens.
"""

import click
from datetime import date
from mtcli.logger import setup_logger
from mtcli_risco.conf import LOSS_LIMIT, STATUS_FILE
from mtcli_risco.models.trades_model import calcular_lucro_total_dia
from mtcli_risco.models.checar_model import (
    carregar_estado,
    salvar_estado,
    risco_excedido,
    encerrar_todas_posicoes,
    cancelar_todas_ordens,
)

log = setup_logger()


@click.command(
    "checar",
    help="Verifica se o limite diário de prejuízo foi atingido.",
)
@click.version_option(package_name="mtcli-risco")
@click.option(
    "--limite",
    "-l",
    default=LOSS_LIMIT,
    help="Limite de perda diária (ex: -500).",
)
@click.option(
    "--lucro",
    is_flag=True,
    default=False,
    help="Exibe o lucro total do dia e encerra.",
)
def checar_cmd(limite: float, lucro: bool):
    """
    Executa uma verificação pontual do risco diário.
    """
    if lucro:
        total = calcular_lucro_total_dia()
        click.echo(f"Lucro total do dia: {total:.2f}")
        log.info(f"[RISCO] Lucro total do dia: {total:.2f}")
        return

    hoje = date.today()
    estado = carregar_estado(STATUS_FILE)

    # Reset diário
    if estado["data"] != hoje.isoformat():
        log.info("[ESTADO] Novo dia detectado, resetando bloqueio.")
        estado["bloqueado"] = False
        salvar_estado(STATUS_FILE, hoje, False)

    if estado["bloqueado"]:
        click.echo("Sistema bloqueado hoje por limite de risco.")
        log.warning("[RISCO] Sistema já bloqueado hoje.")
        return

    if risco_excedido(limite):
        click.echo(
            f"Limite {limite:.2f} excedido. Encerrando posições e bloqueando ordens."
        )
        log.warning(f"[RISCO] Limite {limite:.2f} excedido.")
        encerrar_todas_posicoes()
        cancelar_todas_ordens()
        salvar_estado(STATUS_FILE, hoje, True)
    else:
        click.echo("Dentro do limite de risco.")
        log.info(f"[RISCO] Dentro do limite {limite:.2f}.")
