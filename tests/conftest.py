import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_mt5():
    with patch("mtcli_risco.risco.mt5") as mock_mt5:
        mock_mt5.account_info.return_value = MagicMock(profit=-200.0)
        yield mock_mt5

