import json
from datetime import date, datetime, time
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from mtcli_risco.plugin import cli


@patch("mtcli_risco.plugin.risco_excedido", return_value=True)
@patch("mtcli_risco.plugin.salvar_estado")
@patch(
    "mtcli_risco.plugin.carregar_estado",
    return_value={"data": "2020-01-01", "bloqueado": False},
)
@patch("mtcli_risco.plugin.conectar")
@patch("mtcli_risco.plugin.shutdown")
def test_cli_risco_bloqueia(
    mock_shutdown, mock_conectar, mock_carregar, mock_salvar, mock_risco_excedido
):
    runner = CliRunner()
    result = runner.invoke(cli, ["--limite", "-50"])

    assert result.exit_code == 0
    assert "🚫 Limite diário" in result.output
    mock_salvar.assert_called_once()
    mock_shutdown.assert_called_once()


@patch("mtcli_risco.plugin.risco_excedido", return_value=False)
@patch("mtcli_risco.plugin.salvar_estado")
@patch(
    "mtcli_risco.plugin.carregar_estado",
    return_value={"data": "2020-01-01", "bloqueado": False},
)
@patch("mtcli_risco.plugin.conectar")
@patch("mtcli_risco.plugin.shutdown")
def test_cli_risco_dentro_limite(
    mock_shutdown, mock_conectar, mock_carregar, mock_salvar, mock_risco_excedido
):
    runner = CliRunner()
    result = runner.invoke(cli, ["--limite", "-500"])

    assert result.exit_code == 0
    assert "Dentro do limite de risco." in result.output
    mock_salvar.assert_called_once()
    mock_shutdown.assert_called_once()


@patch(
    "mtcli_risco.plugin.carregar_estado",
    return_value={"data": date.today().isoformat(), "bloqueado": True},
)
@patch("mtcli_risco.plugin.conectar")
@patch("mtcli_risco.plugin.shutdown")
def test_cli_risco_ja_bloqueado(mock_shutdown, mock_conectar, mock_carregar):
    runner = CliRunner()
    result = runner.invoke(cli, ["--limite", "-500"])

    assert result.exit_code == 0
    assert "⚠ Bloqueado hoje por risco" in result.output
    mock_shutdown.assert_called_once()
