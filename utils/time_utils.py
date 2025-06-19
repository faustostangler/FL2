import time
import psutil
import random

from config.config import Config

config = Config()

def sleep_dynamic(wait: float = None, cpu_interval: float = None) -> None:   # type: ignore
        """
        Dynamically adjusts the sleep time based on the system's CPU usage.

        The function monitors the CPU usage and adjusts the sleep duration as follows:
        - If CPU usage is greater than 80%, the function returns a longer sleep time (suggested 0.5 seconds).
        - If CPU usage is between 50% and 80%, the function returns a moderate sleep time (suggested 0.3 seconds).
        - If CPU usage is below 50%, the function returns a short sleep time (suggested 0.1 seconds).
        """
        wait = wait or config.global_settings["wait"] or 2

        # Get the current CPU usage
        cpu_usage = psutil.cpu_percent(interval=cpu_interval or 0.25)

        # Adjust sleep time based on CPU usage
        if cpu_usage > 80:
            wait = wait * random.uniform(0.3, 1.5)  # Increase delay if CPU usage is high
        elif cpu_usage > 50:
            wait = wait * random.uniform(0.2, 1.0)  # delay if CPU usage is medium load
        else:
            wait = wait * random.uniform(0.1, 0.5)  # delay if CPU usage is medium low

        time.sleep(wait)
