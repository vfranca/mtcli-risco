import json
from datetime import date, datetime, time
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from mtcli_risco.checar import checar


@patch("mtcli_risco.checar.risco_excedido", return_value=True)
@patch("mtcli_risco.checar.salvar_estado")
@patch(
    "mtcli_risco.checar.carregar_estado",
    return_value={"data": "2020-01-01", "bloqueado": False},
)
def test_checar_bloqueia(
    mock_carregar, mock_salvar, mock_risco_excedido
):
    runner = CliRunner()
    result = runner.invoke(checar, ["--limite", "-50"])

    assert result.exit_code == 0
    assert "Limite" in result.output
    mock_salvar.assert_called_once()


@patch("mtcli_risco.checar.risco_excedido", return_value=False)
@patch("mtcli_risco.checar.salvar_estado")
@patch(
    "mtcli_risco.checar.carregar_estado",
    return_value={"data": "2020-01-01", "bloqueado": False},
)
def test_checar_dentro_limite(
    mock_carregar, mock_salvar, mock_risco_excedido
):
    runner = CliRunner()
    result = runner.invoke(checar, ["--limite", "-500"])

    assert result.exit_code == 0
    assert "Dentro do limite de risco." in result.output
    mock_salvar.assert_called_once()


@patch(
    "mtcli_risco.checar.carregar_estado",
    return_value={"data": date.today().isoformat(), "bloqueado": True},
)
def test_checar_ja_bloqueado(mock_carregar):
    runner = CliRunner()
    result = runner.invoke(checar, ["--limite", "-500"])

    assert result.exit_code == 0
    assert "Bloqueado hoje por risco" in result.output


@patch("mtcli_risco.checar.calcular_lucro_total_dia", return_value=123.45)
def test_checar_exibe_lucro(mock_lucro):
    runner = CliRunner()
    result = runner.invoke(checar, ["--lucro"])

    assert result.exit_code == 0
    assert "Lucro total do dia: 123.45" in result.output
