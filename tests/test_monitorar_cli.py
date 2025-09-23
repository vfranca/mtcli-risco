import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from datetime import date
from mtcli_risco.monitorar import monitorar


@patch("mtcli_risco.monitorar.risco_excedido", return_value=True)
@patch("mtcli_risco.monitorar.salvar_estado")
@patch(
    "mtcli_risco.monitorar.carregar_estado",
    return_value={"data": "2020-01-01", "bloqueado": False},
)
@patch("mtcli_risco.monitorar.encerrar_todas_posicoes")
@patch("mtcli_risco.monitorar.cancelar_todas_ordens")
@patch("time.sleep", side_effect=KeyboardInterrupt)
def test_monitorar_excede_limite(
    mock_sleep,
    mock_cancelar,
    mock_encerrar,
    mock_carregar,
    mock_salvar,
    mock_risco_excedido,
):
    runner = CliRunner()
    result = runner.invoke(monitorar, ["--limite", "-200", "--intervalo", "1"])

    assert result.exit_code == 0
    assert "Monitorando risco" in result.output
    assert "Limite -200.0 excedido" in result.output
    mock_encerrar.assert_called_once()
    mock_cancelar.assert_called_once()
    mock_salvar.assert_called()


@patch("mtcli_risco.monitorar.risco_excedido", return_value=False)
@patch("mtcli_risco.monitorar.salvar_estado")
@patch(
    "mtcli_risco.monitorar.carregar_estado",
    return_value={"data": "2020-01-01", "bloqueado": False},
)
@patch("time.sleep", side_effect=KeyboardInterrupt)
def test_monitorar_dentro_limite(
    mock_sleep,
    mock_carregar,
    mock_salvar,
    mock_risco_excedido,
):
    runner = CliRunner()
    result = runner.invoke(monitorar, ["--limite", "-500", "--intervalo", "1"])

    assert result.exit_code == 0
    assert "Dentro do limite -500" in result.output
    mock_salvar.assert_called()


@patch("mtcli_risco.monitorar.risco_excedido")
@patch("mtcli_risco.monitorar.salvar_estado")
@patch(
    "mtcli_risco.monitorar.carregar_estado",
    return_value={"data": date.today().isoformat(), "bloqueado": True},
)
@patch("mtcli_risco.monitorar.encerrar_todas_posicoes")
@patch("mtcli_risco.monitorar.cancelar_todas_ordens")
@patch("time.sleep", side_effect=KeyboardInterrupt)
def test_monitorar_estado_ja_bloqueado(
    mock_sleep,
    mock_cancelar,
    mock_encerrar,
    mock_carregar,
    mock_salvar,
    mock_risco_excedido,
):
    runner = CliRunner()
    result = runner.invoke(monitorar, ["--limite", "-250", "--intervalo", "1"])

    assert result.exit_code == 0
    assert f"Sistema bloqueado hoje" in result.output
    mock_encerrar.assert_not_called()
    mock_cancelar.assert_not_called()

