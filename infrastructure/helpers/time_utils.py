import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("infrastructure > helpers > time_utils")
import time
import psutil
import random
from typing import Optional
from infrastructure.config import Config


class TimeUtils:
    """Helper for dynamic sleep intervals based on CPU usage."""
    import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("time_utils.TimeUtils")
    def __init__(self, config: Config):
        import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("TimeUtils.__init__")
        self.config = config

    def sleep_dynamic(self, wait: Optional[float] = None, cpu_interval: Optional[float] = None) -> None:
        """Sleep for a dynamically adjusted time based on CPU utilization.

        The logic adjusts the delay as follows:
        - High CPU (>80%): randomly increases the wait time.
        - Medium CPU (50–80%): moderate delay.
        - Low CPU (<50%): short delay.

        Args:
            wait: Base wait time in seconds.
            cpu_interval: Sampling interval for ``psutil.cpu_percent``.
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
