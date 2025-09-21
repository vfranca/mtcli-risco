import os
import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from mtcli_risco.risco import (
    carregar_estado,
    salvar_estado,
    risco_excedido,
    calcular_lucro_total_dia,
    encerrar_todas_posicoes,
    cancelar_todas_ordens,
)

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


@patch("mtcli_risco.risco.mt5")
def test_calcular_lucro_total_dia(mock_mt5):
    mock_deal1 = MagicMock(profit=100.0, type=1)  # SELL
    mock_deal2 = MagicMock(profit=-200.0, type=2)  # BUY
    mock_deal3 = MagicMock(profit=50.0, type=4)  # SWAP, ignorado

    mock_mt5.history_deals_get.return_value = [mock_deal1, mock_deal2, mock_deal3]

    mock_info = MagicMock(profit=30.0)
    mock_mt5.account_info.return_value = mock_info

    lucro = calcular_lucro_total_dia()
    assert lucro == -70.0  # (100 - 200) + 30


@patch("mtcli_risco.risco.mt5")
def test_risco_excedido_true(mock_mt5):
    mock_mt5.history_deals_get.return_value = [MagicMock(profit=-200.0, type=1)]
    mock_mt5.account_info.return_value = MagicMock(profit=-100.0)

    assert risco_excedido(-250.0) is True


@patch("mtcli_risco.risco.mt5")
def test_risco_excedido_false(mock_mt5):
    mock_mt5.history_deals_get.return_value = [MagicMock(profit=500.0, type=1)]
    mock_mt5.account_info.return_value = MagicMock(profit=100.0)
    assert risco_excedido(-500.0) is False


@patch("mtcli_risco.risco.mt5")
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


@patch("mtcli_risco.risco.mt5")
def test_cancelar_todas_ordens(mock_mt5):
    mock_ordem = MagicMock()
    mock_ordem.ticket = 98765

    mock_mt5.orders_get.return_value = [mock_ordem]

    mock_result = MagicMock()
    mock_result.retcode = mock_mt5.TRADE_RETCODE_DONE
    mock_mt5.order_delete.return_value = mock_result

    cancelar_todas_ordens()
    mock_mt5.order_delete.assert_called_once_with(98765)


@patch("mtcli_risco.risco.mt5")
@patch("mtcli_risco.risco.encerrar_todas_posicoes")
@patch("mtcli_risco.risco.cancelar_todas_ordens")
def test_risco_excedido_com_acoes(mock_cancelar, mock_encerrar, mock_mt5):
    # Simula prejuízo do dia
    mock_mt5.history_deals_get.return_value = [MagicMock(profit=-300.0, type=1)]
    mock_mt5.account_info.return_value = MagicMock(profit=-100.0)

    resultado = risco_excedido(-200.0)

    assert resultado is True
    mock_encerrar.assert_called_once()
    mock_cancelar.assert_called_once()
