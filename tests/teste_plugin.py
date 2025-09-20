import json
from datetime import date
from unittest.mock import patch, mock_open
from click.testing import CliRunner
from mtcli_risco.plugin import cli


def test_limite_nao_excedido(monkeypatch):
    runner = CliRunner()

    fake_estado = {"data": date.today().isoformat(), "bloqueado": False}

    monkeypatch.setattr("mtcli_risco.plugin.carregar_estado", lambda _: fake_estado)
    monkeypatch.setattr("mtcli_risco.plugin.risco_excedido", lambda limite: False)
    monkeypatch.setattr("mtcli_risco.plugin.salvar_estado", lambda *args: None)
    monkeypatch.setattr("mtcli_risco.plugin.shutdown", lambda: None)

    result = runner.invoke(cli, ["--limite", "-200"])
    assert "Dentro do limite de risco." in result.output


def test_limite_excedido(monkeypatch):
    runner = CliRunner()

    fake_estado = {"data": date.today().isoformat(), "bloqueado": False}

    monkeypatch.setattr("mtcli_risco.plugin.carregar_estado", lambda _: fake_estado)
    monkeypatch.setattr("mtcli_risco.plugin.risco_excedido", lambda limite: True)
    monkeypatch.setattr("mtcli_risco.plugin.salvar_estado", lambda *args: None)
    monkeypatch.setattr("mtcli_risco.plugin.shutdown", lambda: None)

    result = runner.invoke(cli, ["--limite", "-200"])
