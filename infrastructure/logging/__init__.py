import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("infrastructure > helpers > logger __init__")
from .logger import Logger

__all__ = ["Logger"]
