import os
from mtcli.conf import config


LOSS_LIMIT = float(
    os.getenv(
        "LOSS_LIMIT",
        config["DEFAULT"].getfloat("loss_limit", fallback=-180.00),
    )
)

STATUS_FILE = os.getenv(
    "STATUS_FILE",
    config["DEFAULT"].get("status_file", fallback="bloqueio.json"),
)

INTERVALO = int(
    os.getenv(
        "INTERVALO",
        config["DEFAULT"].getint("intervalo", fallback=60),
    )
)

# Caminho do executável do MetaTrader 5 (usado no HARDSTOP)
MT5_TERMINAL_PATH = os.getenv(
    "MT5_TERMINAL_PATH",
    config["DEFAULT"].get(
        "mt5_terminal_path",
        fallback=r"C:\Program Files\MetaTrader 5\terminal64.exe",
    ),
)
