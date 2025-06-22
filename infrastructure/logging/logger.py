import logging
from typing import Optional
from infrastructure.config.config import Config
from infrastructure.logging.progress_formatter import ProgressFormatter
from infrastructure.logging.context_tracker import ContextTracker


class Logger:
    """
    Logger da aplicação FLY.
    Encapsula configuração, contexto e formatação de progresso.
    Usa o sistema de logging nativo do Python.
    """

    def __init__(self, config: Config, level: str = "DEBUG"):
        self.config = config
        self.logger = self._setup_logger(level)
        self.progress_formatter = ProgressFormatter()
        self.context_tracker = ContextTracker(config.paths.root_dir)

    def _setup_logger(self, level: str) -> logging.Logger:
        """
        Configura o logger nativo do Python com handlers para terminal e arquivo.
        """
        log_path = self.config.logging.full_path
        logger = logging.getLogger("FLY")
        logger.setLevel(logging.DEBUG)

        if not logger.hasHandlers():
            formatter = logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            # Console
            sh = logging.StreamHandler()
            sh.setLevel(getattr(logging, level.upper(), logging.INFO))
            sh.setFormatter(formatter)
            logger.addHandler(sh)

            # Arquivo
            fh = logging.FileHandler(log_path, encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        return logger
    def log(self, message: str, level: str = "info", progress: Optional[dict] = None):
        """
        Registra uma mensagem com contexto e progresso, se aplicável.
        """
        context_msg = self.context_tracker.get_context() if level.lower() == "debug" else ""
        progress_msg = self.progress_formatter.format(progress) if progress else ""

        full_message = message
        if context_msg:
            full_message += f" | {context_msg}"
        if progress_msg:
            full_message += f" | {progress_msg}"

        try:
            log_fn = getattr(self.logger, level.lower(), self.logger.info)
            log_fn(full_message)
        except Exception as e:
            print(f"Logging failed: {e}")
            print(f"Logging failed: {e}")
