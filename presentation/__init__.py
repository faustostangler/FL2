import logging; logging.basicConfig(level=logging.DEBUG); logging.debug("presentation > cli.__init__")
from .cli import CLIController

__all__ = ['CLIController']
