import logging
import uuid
from typing import Optional

from infrastructure.config.config import Config
from infrastructure.logging.progress_formatter import ProgressFormatter
from infrastructure.logging.context_tracker import ContextTracker



class Logger:
    """
    Logger da aplicação.
    Encapsula configuração, contexto e formatação de progresso.
    Usa o sistema de logging nativo do Python.
    """

    def __init__(self, config: Config, level: str = "DEBUG", logger_name: Optional[str] = None):
        self._run_id = uuid.uuid4().hex[:8]
        self.config = config
        self.logger_name = logger_name or self.config.global_settings.app_name or "FLY"
        self.progress_formatter = ProgressFormatter()
        self.context_tracker = ContextTracker(config.paths.root_dir)
        self._logger = self._setup_logger(level)


    def _setup_logger(self, level: str) -> logging.LoggerAdapter:
        """
        Configura o logger nativo do Python com handlers para terminal e arquivo.
        """
        log_path = self.config.logging.full_path
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(logging.DEBUG)

        if not logger.hasHandlers():
            formatter = SafeFormatter(
                "%(run_id)s %(worker_id)s %(asctime)s %(levelname)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

            sh = logging.StreamHandler()
            sh.setLevel(getattr(logging, level.upper(), logging.INFO))
            sh.setFormatter(formatter)
            logger.addHandler(sh)

            fh = logging.FileHandler(log_path, encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        adapter = MergedLoggerAdapter(logger, extra={"run_id": self._run_id})

        return adapter

    def log(self, message: str, level: str = "info", progress: Optional[dict] = None, extra: Optional[dict] = None):
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
            log_fn = getattr(self._logger, level.lower(), self._logger.info)
            merged_extra = {"run_id": self._run_id, "worker_id": ""}
            if extra:
                merged_extra.update(extra)
            log_fn(full_message, extra=merged_extra)
        except Exception as e:
            print(f"Logging failed: {e} - {full_message}")


class SafeFormatter(logging.Formatter):
    def format(self, record):
        # Define valores padrão
        defaults = {
            "run_id": "1",
            "worker_id": "1", 
        }

        for key, default in defaults.items():
            if not hasattr(record, key) or not getattr(record, key):
                setattr(record, key, default)

        return super().format(record)

class MergedLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        base = self.extra if isinstance(self.extra, dict) else {}
        extra = kwargs.get("extra") or {}
        if not isinstance(extra, dict):
            extra = {}
        kwargs["extra"] = {**base, **extra}
        return msg, kwargs
