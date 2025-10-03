import os
import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from mtcli_risco.models.checar_model import (
    carregar_estado,
    salvar_estado,
    risco_excedido,
    encerrar_todas_posicoes,
    cancelar_todas_ordens,
)
from mtcli_risco.models.trades_model import calcular_lucro_total_dia

TEST_ARQ = "teste_estado.json"


def test_carregar_estado_vazio(tmp_path):
    path = tmp_path / "estado.json"
    estado = carregar_estado(str(path))
    assert estado == {"data": None, "bloqueado": False}


def test_carregar_estado_existente(tmp_path):
    path = tmp_path / "estado.json"
    with open(path, "w") as f:
        json.dump({"data": "2025-09-20", "bloqueado": True}, f)
    estado = carregar_estado(str(path))
    assert estado == {"data": "2025-09-20", "bloqueado": True}


def test_salvar_estado(tmp_path):
    path = tmp_path / "estado.json"
    salvar_estado(str(path), date(2025, 9, 20), True)
    with open(path) as f:
        data = json.load(f)
    assert data == {"data": "2025-09-20", "bloqueado": True}


@patch("mtcli_risco.models.checar_model.calcular_lucro_total_dia")
def test_risco_excedido_true(mock_lucro_total):
    mock_lucro_total.return_value = -300.0
    assert risco_excedido(-250.0) is True


@patch("mtcli_risco.models.checar_model.calcular_lucro_total_dia")
def test_risco_excedido_false(mock_lucro_total):
    mock_lucro_total.return_value = -300.0
    assert risco_excedido(-500.0) is False


@patch("mtcli_risco.models.checar_model.mt5")
def test_encerrar_todas_posicoes(mock_mt5):
    mock_pos = MagicMock()
    mock_pos.symbol = "WINV25"
    mock_pos.volume = 1.0
    mock_pos.ticket = 12345
    mock_pos.type = 0  # BUY

    mock_mt5.positions_get.return_value = [mock_pos]

    mock_result = MagicMock()
    mock_result.retcode = mock_mt5.TRADE_RETCODE_DONE
    mock_mt5.order_send.return_value = mock_result

    encerrar_todas_posicoes()

    mock_mt5.order_send.assert_called_once()


@patch("mtcli_risco.models.checar_model.mt5")
def test_cancelar_todas_ordens(mock_mt5):
    mock_ordem = MagicMock()
    mock_ordem.ticket = 98765

    mock_mt5.orders_get.return_value = [mock_ordem]

    mock_result = MagicMock()
    mock_result.retcode = mock_mt5.TRADE_RETCODE_DONE
    mock_mt5.order_delete.return_value = mock_result

    cancelar_todas_ordens()
    mock_mt5.order_delete.assert_called_once_with(98765)
