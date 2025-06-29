import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("infrastructure > helpers > time_utils")
import time
import psutil
import random
from typing import Optional
from infrastructure.config import Config


class TimeUtils:
    """
    Utilitários para controle de tempo adaptado à carga da CPU.
    """
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("time_utils class TimeUtils")
    def __init__(self, config: Config):
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("TimeUtils __init__")
        self.config = config

    def sleep_dynamic(self, wait: Optional[float] = None, cpu_interval: Optional[float] = None) -> None:
        """
        Aguarda dinamicamente com base no uso de CPU.

        A lógica ajusta o tempo de espera:
        - Alta CPU (>80%): aumenta aleatoriamente o delay.
        - Média CPU (50–80%): delay moderado.
        - Baixa CPU (<50%): delay curto.

        Args:
            wait (float): Tempo base de espera.
            cpu_interval (float): Intervalo de amostragem da CPU.
        """
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("TimeUtils.sleep_dynamic()")
        wait = wait or self.config.global_settings.wait or 2
        cpu_usage = psutil.cpu_percent(interval=cpu_interval or 0.25)

        if cpu_usage > 80:
            wait *= random.uniform(0.3, 1.5)
        elif cpu_usage > 50:
            wait *= random.uniform(0.2, 1.0)
        else:
            wait *= random.uniform(0.1, 0.5)

        time.sleep(wait)
