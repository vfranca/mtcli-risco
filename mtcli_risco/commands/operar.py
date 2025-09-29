import click
from mtcli_risco.models.operar import atualizar_lucro, pode_operar

@click.command("operar")
@click.option("--volume", required=True, type=float, help="Volume da operação")
def operar(volume):
    atualizar_lucro()

    if not pode_operar(volume):
        click.echo("Operação bloqueada por risco.")
        return
        # Aqui você chama a função que executa o trade (simulação ou real)
    click.echo(f"Operação executada com volume {volume}.")

if __name__ == "__main__":
    operar()
