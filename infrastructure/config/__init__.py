import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("infrastructure > config.__init__")
from .config import Config

__all__ = ["Config"]
