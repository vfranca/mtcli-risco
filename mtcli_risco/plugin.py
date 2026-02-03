"""
Registro do plugin mtcli-risco no mtcli principal.
"""

from .cli import cli as risco_cli


def register(main_cli):
    """
    Registra o grupo de comandos 'risco' no mtcli principal.
    """
    main_cli.add_command(risco_cli, name="risco")
