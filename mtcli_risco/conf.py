import os
from mtcli.conf import config


LOSS_LIMIT = float(os.getenv("LOSS_LIMIT", config["DEFAULT"].getfloat("loss_limit", fallback=-180.00)))
