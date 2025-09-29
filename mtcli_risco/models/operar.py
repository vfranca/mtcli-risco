from datetime import date, datetime, time
import MetaTrader5 as mt5
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger

log = setup_logger("mtcli_risco_risco")

# Configurações de risco (você pode parametrizar depois)
PERDA_DIARIA_MAX = 2000.0
VOLUME_MAX_OPERACAO = 5.0
HORARIO_CORTE = time(16, 45)

estado = {
    "lucro_dia": 0.0,
    "bloqueado": False,
    "data": None,
}

def resetar_estado():
    hoje = date.today()
    estado["data"] = hoje
    estado["lucro_dia"] = 0.0
    estado["bloqueado"] = False
    log.info("Estado de risco resetado.")

def atualizar_lucro():
    """Atualiza o lucro do dia puxando do MetaTrader5."""
    conectar()
    hoje = date.today()
    if estado.get("data") != hoje:
        resetar_estado()

    inicio = datetime.combine(hoje, time(0, 0))
    fim = datetime.combine(hoje, time(23, 59))
    deals = mt5.history_deals_get(inicio, fim)
    shutdown()

    lucro_realizado = 0.0
    if deals is not None:
        lucro_realizado = sum(deal.profit for deal in deals if deal.type in (1, 2))

    estado["lucro_dia"] = lucro_realizado
    log.info(f"Lucro realizado hoje: {lucro_realizado:.2f}")

    if lucro_realizado <= -PERDA_DIARIA_MAX:
        estado["bloqueado"] = True
        log.warning(f"Perda diária excedida: {lucro_realizado:.2f}. Sistema bloqueado.")

def pode_operar(volume):
    if estado.get("bloqueado"):
        log.warning("Operação bloqueada devido a risco diário excedido.")
        return False

    if volume > VOLUME_MAX_OPERACAO:
        log.warning(f"Volume {volume} excede limite máximo de {VOLUME_MAX_OPERACAO}")
        return False

    agora = datetime.now().time()
    if agora > HORARIO_CORTE:
        log.warning("Fora do horário permitido para operar.")
        return False

    return True

